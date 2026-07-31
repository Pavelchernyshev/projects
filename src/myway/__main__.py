"""Entry point: `python -m myway`."""

from __future__ import annotations

import logging
import sys

from .bot import build_application
from .config import Config, ConfigError


def main() -> int:
    try:
        config = Config.from_env()
    except ConfigError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )
    # httpx logs every Telegram long-poll at INFO, which drowns everything else.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    log = logging.getLogger("myway")
    log.info("starting %s (stt=%s)", config.product_name, config.stt_backend)

    app = build_application(config)
    app.run_polling(drop_pending_updates=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
