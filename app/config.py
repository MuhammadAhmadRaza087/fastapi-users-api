import os


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
SEED_ON_STARTUP = _bool("SEED_ON_STARTUP", True)
SEED_COUNT = int(os.getenv("SEED_COUNT", "25"))
