"""Independent CLI verifier. No BeProgram login, database or history API required.

From repository root: python apps/receipt-verifier/verify.py package.json --trusted-issuer PUBLIC_KEY
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.receipts import RPC, verify_package

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('package', type=Path)
parser.add_argument('--trusted-issuer', action='append', required=True, help='An issuer you trust independently; do not copy trust from an unknown manifest')
parser.add_argument('--rpc', default='https://api.devnet.solana.com')
args = parser.parse_args()
package = json.loads(args.package.read_text(encoding='utf-8'))
result = verify_package(package['manifest'], package['signature'], RPC(args.rpc), args.trusted_issuer)
print(json.dumps(result, indent=2))
sys.exit(0 if result['status'] == 'evidence_matches' else 1)
