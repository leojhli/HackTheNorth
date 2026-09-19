"""Read-only local readiness checks. Never prints credentials, answers or source."""
import argparse
import json
import platform
from pathlib import Path
import httpx
from pydantic import ValidationError
from backend.config import Settings
from backend.assessment import LocalAssessor


def inspect(config, client=None):
    checks = []
    def add(name, ok, detail):
        checks.append({'check': name, 'ok': bool(ok), 'detail': detail})
    add('python', True, platform.python_version())
    add('dashboard_build', Path('apps/dashboard/dist/index.html').is_file(), 'Build with npm --prefix apps/dashboard run build if missing.')
    add('extension_package', Path('artifacts/codeproof-companion.vsix').is_file(), 'Install the VSIX using Extensions: Install from VSIX.')
    model = LocalAssessor(config).status()
    add('local_model', model['available'], model['message'])
    own_client = client is None
    client = client or httpx.Client(base_url='http://127.0.0.1:8000', timeout=5, trust_env=False, follow_redirects=False)
    try:
        health = client.get('/health')
        health.raise_for_status()
        add('backend', health.json().get('status') == 'ok', 'http://127.0.0.1:8000')
        running = client.get('/v1/config')
        running.raise_for_status()
        data = running.json()
        matches = data.get('integration') == 'codeproof_managed' and data.get('cost_mode') == 'local_only' and data.get('ai', {}).get('model') == config.ollama_model
        add('configuration', matches, 'Backend must match .env; use ./scripts/run-local.ps1 -Restart after changes.')
        if config.auth_mode == 'local':
            response = client.get('/v1/projects', headers={'Authorization': 'Bearer ' + config.local_dev_token})
            add('local_token', response.status_code == 200, 'Local token accepted.' if response.status_code == 200 else 'Backend token differs from .env; restart and reconnect the extension.')
    except (httpx.HTTPError, ValueError, AttributeError):
        add('backend_connection', False, 'Start ./scripts/run-local.ps1; confirm port 8000 belongs to CodeProof.')
    finally:
        if own_client:
            client.close()
    return {'ready': all(c['ok'] for c in checks), 'checks': checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        report = inspect(Settings())
    except ValidationError:
        report = {'ready': False, 'checks': [{'check': 'configuration', 'ok': False,
            'detail': 'Invalid .env configuration. Compare settings with .env.example; no values are printed.'}]}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for check in report['checks']:
            print(('OK   ' if check['ok'] else 'FIX  ') + check['check'] + ': ' + check['detail'])
        print('Ready for CodeProof.' if report['ready'] else 'Resolve the FIX items above, then run this command again.')
    return 0 if report['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
