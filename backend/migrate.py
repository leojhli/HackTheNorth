"""Schema v1 bootstrap. Future revisions must be explicit migrations, not create_all updates."""
from .config import settings
from .db import Database

if __name__ == '__main__':
    Database(settings().database_url).migrate()
    print('Schema v1 ready')
