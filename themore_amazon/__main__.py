import argparse
import logging

from playwright.sync_api import Browser, Playwright, sync_playwright

from themore_amazon.main import (
    init_browser,
    load_yaml_config,
    parse_args,
    process_reload_all,
)
from themore_amazon.utils import Config, init_logger


def main() -> None:
    init_logger()
    args: argparse.Namespace = parse_args()
    logging.info(f"args: {args}")
    pw_core: Playwright = sync_playwright().start()
    playwright_browser: Browser = init_browser(pw_core, headless=args.headless)
    config: Config = Config(**load_yaml_config("config.yml"))

    process_reload_all(
        playwright_browser,
        is_safe=args.safe,
        default_timeout=args.timeout,
        **config,
    )


if __name__ == "__main__":
    main()
