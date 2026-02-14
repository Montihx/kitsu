from __future__ import annotations

import logging


def configure_logging(log_level: str) -> logging.Logger:
    level = logging.getLevelName(log_level.upper())
    resolved_level = level if isinstance(level, int) else logging.INFO

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=resolved_level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )

    logger = logging.getLogger("kitsu")
    logger.setLevel(resolved_level)
    return logger
