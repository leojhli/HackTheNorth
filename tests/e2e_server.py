"""Explicit test server only. Never imported by the product runtime."""
import tempfile
import os
from pathlib import Path
import uvicorn
from backend.main import create_app
from backend.config import Settings
from backend.db import Database
from tests.conftest import FixtureAssessor

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='beprogram-e2e-') as directory:
        port=int(os.environ.get('BEPROGRAM_E2E_PORT','8020'))
        config = Settings(_env_file=None, environment='test', database_url='sqlite:///'+str(Path(directory)/'e2e.db'),
            auth_mode='local', local_dev_token='automated-test-only-token-not-a-real-secret',
            allowed_origins=f'http://127.0.0.1:{port}', app_origin=f'http://127.0.0.1:{port}')
        database = Database(config.database_url)
        app = create_app(config, database, FixtureAssessor())
        try:
            uvicorn.run(app, host='127.0.0.1', port=port, access_log=False)
        finally:
            database.engine.dispose()
