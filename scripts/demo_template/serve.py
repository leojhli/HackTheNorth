"""Local preview only: no packages, accounts or internet needed."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if __name__ == '__main__':
    handler = partial(SimpleHTTPRequestHandler, directory=str(Path(__file__).parent))
    # Set the module MIME type explicitly for Windows installations.
    handler.func.extensions_map['.js'] = 'text/javascript'
    print('Open http://127.0.0.1:8010 - Ctrl+C stops this preview.', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8010), handler).serve_forever()
