"""Convert fixture reads to live data without changing the original panel layout/tokens."""
from pathlib import Path
path = Path('apps/dashboard/src/components/ExtensionPanel.tsx')
s = path.read_text(encoding='utf-8')
s = s.replace("import * as fx from '../lib/fixture'", "import { useProduct } from '../lib/product'")
s = s.replace("from './v3'", "from './Voice'")
for name in ['StatusBar', 'Scope', 'ActiveSession', 'Analyzing', 'Checkpoint', 'Followup', 'Verified', 'PausedCheckpoint']:
    lines = s.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('function '+name+'('):
            lines.insert(i+1, '  const fx = useProduct()')
            break
    s = '\n'.join(lines)+'\n'
s = s.replace("useState('00:41')", "useState('00:00')")
s = s.replace('let sec = 41', 'let sec = Math.max(0, Math.floor(Date.now() / 1000 - fx.SESSION_STARTED))')
s = s.replace("setElapsed(`00:${String(sec % 60).padStart(2, '0')}`)", "setElapsed(`${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`)")
s = s.replace('Monitoring meaningful changes', 'Ready for approved saved changes')
s = s.replace('CodeProof: monitoring', 'CodeProof: ready')
s = s.replace('Local workspace\n          trusted', 'Approved file scope')
s = s.replace('<input type="checkbox" defaultChecked', '<input type="checkbox" checked readOnly')
s = s.replace('— your latest change introduces a parameterized query.', '— {fx.REASON}')
s = s.replace('capturedAt="2:24 PM"', 'capturedAt={fx.CAPTURED_AT}')
s = s.replace('<SpeechPlayback text={fx.INITIAL_QUESTION} />', '<SpeechPlayback text={fx.INITIAL_QUESTION} />')
s = s.replace('Your explanation is saved. Your next connected AI request still needs this checkpoint.', 'Submitted explanations are saved. Your unsent draft stays in this tab. Managed Ask AI still needs this checkpoint.')
s = s.replace('{saved && (\n        // Low-emphasis', '{saved && fx.RECEIPTS_ENABLED && (\n        // Low-emphasis')
s = s.replace('Your next connected AI request', 'Your next managed AI request').replace('Your connected AI request', 'Your managed AI request')
path.write_text(s, encoding='utf-8')
