import os
from typing import Tuple


def _resolve_folder(base_folder: str) -> str:
    """Return an absolute folder path for the database.

    Using the project root instead of the current working directory ensures
    that we always point to the same database file, even if the app is started
    from different paths (e.g., during deployments or CLI usage).
    """
    if os.path.isabs(base_folder):
        return base_folder

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(project_root, base_folder)


def get_database_location() -> Tuple[str, str]:
    """Return a writable database folder and file path.

    The function prefers the folder set in the DATABASE_FOLDER environment
    variable (defaulting to "db"). If creating that folder fails (for
    example, in read-only environments like serverless deployments), it
    falls back to a writable directory under /tmp.
    """
    configured_folder = os.getenv("DATABASE_FOLDER", "db")
    target_folder = _resolve_folder(configured_folder)

    try:
        os.makedirs(target_folder, exist_ok=True)
        database_folder = target_folder
    except OSError:
        fallback_name = os.path.basename(target_folder.rstrip("/")) or "db"
        fallback_folder = os.path.join("/tmp", fallback_name)
        os.makedirs(fallback_folder, exist_ok=True)
        database_folder = fallback_folder

    database_path = os.path.join(database_folder, "database.db")
    return database_folder, database_path
