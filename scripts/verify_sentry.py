"""Verify redacted Sentry Logs + Tracing; offline by default, explicit --send only."""
import argparse
import json
import time
import uuid
from pathlib import Path
import sentry_sdk
from sentry_sdk.transport import Transport
from backend.config import Settings
from backend.assessment import LocalAssessor
from backend import observability


class RecordingTransport(Transport):
    def __init__(self):
        super().__init__(); self.envelopes=[]

    def capture_envelope(self, envelope):
        self.envelopes.append(envelope)


def main(send, output):
    config=Settings()
    if send and not config.sentry_enabled:
        raise SystemExit('Set SENTRY_ENABLED=true and a Sentry project DSN locally before --send. No event sent.')
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as stream: stream.write('{}')
    transport=None if send else RecordingTransport()
    diagnostic=config.model_copy(update={'sentry_enabled':True,'environment':'test',
        'sentry_dsn':config.sentry_dsn if send else 'https://public@o0.ingest.us.sentry.io/1'})
    observability.configure(diagnostic, transport)
    correlation=str(uuid.uuid4())
    report={'mode':'live_send' if send else 'offline_sdk_transport','correlation_id':correlation,
        'method':'Real local inference on a synthetic helper. Offline mode captures real SDK envelopes in memory without contacting Sentry. No user code or history is read.',
        'dashboard_receipt_verified':False,'independent_quality_review':False}
    try:
        with observability.stage('managed_ask',correlation):
            LocalAssessor(config).ask('Explain this return value.',{'files':[{'path':'src/synthetic.js',
                'lines':[{'number':1,'text':'export function answer() { return 42; }'}]}],'partial':False})
        sentry_sdk.flush(timeout=5)
        if transport:
            items=[item for env in transport.envelopes for item in env.items]
            wire=b'\n'.join(env.serialize() for env in transport.envelopes).decode()
            assert 'synthetic.js' not in wire and 'return 42' not in wire and 'Explain this' not in wire
            if config.local_dev_token: assert config.local_dev_token not in wire
            transactions=[item.payload.json for item in items if item.type=='transaction']
            logs=[item for item in items if item.type=='log']
            assert transactions and logs
            assert any(s['op']=='codeproof.local_inference' for t in transactions for s in t['spans'])
            report.update(sdk_products_verified=['Tracing','Logs'],transactions=len(transactions),log_envelopes=len(logs),
                nested_inference_verified=True,private_payload_absent=True)
        else:
            report['note']='SDK flushed. Delivery/visibility and a real product improvement must still be verified in your Sentry dashboard.'
    finally:
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        sentry_sdk.get_client().close()
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--send',action='store_true',help='Send redacted diagnostics to the explicitly enabled project.')
    parser.add_argument('--output',default='docs/release-review/sentry-'+str(time.time_ns())+'.json')
    args=parser.parse_args()
    main(args.send,args.output)
