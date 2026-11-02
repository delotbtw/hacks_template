import asyncio
from pathlib import Path

from alembic import command
from alembic.config import Config

from tests.conftest import _url, recreate_database

ROOT = Path(__file__).resolve().parent.parent
MIGRATION_DB = "app_migrations_test"


def _cfg() -> Config:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", _url(MIGRATION_DB))
    return cfg


async def test_upgrade_head_and_no_model_drift():
    await recreate_database(MIGRATION_DB)
    cfg = _cfg()
    # env.py вызывает asyncio.run, поэтому запускаем в отдельном потоке
    await asyncio.to_thread(command.upgrade, cfg, "head")
    # check бросает исключение, если автогенерация находит расхождения моделей и миграций
    await asyncio.to_thread(command.check, cfg)
