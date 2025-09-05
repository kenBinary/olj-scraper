import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


class Logger:
    def __init__(self, name: Optional[str] = None, level: str = "DEBUG"):
        Path("logs").mkdir(exist_ok=True)

        self.logger = logging.getLogger(name or __name__)
        self.logger.setLevel(getattr(logging, level.upper(), logging.DEBUG))

        if not self.logger.handlers:
            # Console handler
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.INFO)
            ch.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)-8s] %(name)s: %(message)s")
            )

            # File handler
            fh_info = logging.handlers.RotatingFileHandler(
                "logs/app.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            fh_info.setLevel(logging.INFO)
            fh_info.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)8s] %(name)s [%(filename)s:%(lineno)d] %(funcName)s(): %(message)s"
                )
            )

            fh_error = logging.handlers.RotatingFileHandler(
                "logs/errors.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            fh_error.setLevel(logging.ERROR)
            fh_error.setFormatter(
                logging.Formatter(
                    "%(asctime)s [%(levelname)8s] %(name)s [%(filename)s:%(lineno)d] %(funcName)s(): %(message)s"
                )
            )

            self.logger.addHandler(ch)
            self.logger.addHandler(fh_info)
            self.logger.addHandler(fh_error)

    def get(self) -> logging.Logger:
        return self.logger

    def set_level(self, level: str):
        lvl = getattr(logging, level.upper(), None)
        if lvl:
            self.logger.setLevel(lvl)
            self.logger.info(f"Log level set to {level.upper()}")
