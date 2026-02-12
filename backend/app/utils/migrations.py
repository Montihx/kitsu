import logging
import os
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("kitsu.migrations")
DEFAULT_TIMEOUT_SECONDS = 60
try:
    MIGRATIONS_TIMEOUT = int(os.getenv("ALEMBIC_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS))
except ValueError:
    logger.warning("ALEMBIC_TIMEOUT_SECONDS is invalid; using default %s", DEFAULT_TIMEOUT_SECONDS)
    MIGRATIONS_TIMEOUT = DEFAULT_TIMEOUT_SECONDS


def _find_project_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "alembic.ini").exists():
            return parent
    raise RuntimeError("alembic.ini not found in parent directories")


def run_migrations() -> None:
    logger.info("Running Alembic migrations...")

    try:
        project_root = _find_project_root()
    except RuntimeError as exc:
        logger.error("Could not locate alembic.ini near %s", __file__)
        raise RuntimeError("Alembic configuration not found") from exc

    alembic_executable = os.getenv("ALEMBIC_BIN") or shutil.which("alembic")
    if not alembic_executable:
        logger.error("Alembic executable not found via ALEMBIC_BIN or PATH")
        raise RuntimeError("Alembic executable not found")

    try:
        result = subprocess.run(
            [alembic_executable, "upgrade", "head"],
            capture_output=True,
            text=True,
            # Render deployment requires inheriting the full environment for Alembic
            env=os.environ,
            cwd=project_root,
            timeout=MIGRATIONS_TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        logger.error("Alembic migrations timed out after %s seconds", exc.timeout)
        raise RuntimeError("Alembic migrations timed out") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        logger.error("Alembic migrations failed:\n%s", stderr or "<no stderr>")
        stdout = result.stdout.strip()
        if stdout:
            logger.error("Alembic migrations stdout:\n%s", stdout)
        raise RuntimeError("Alembic migrations failed")

    logger.info("Alembic migrations applied successfully")
