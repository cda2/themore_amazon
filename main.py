import argparse
import datetime
import logging
from argparse import ArgumentParser
from functools import wraps
from os import PathLike
from pathlib import Path
from typing import Optional, Mapping, Any, TypedDict

import yaml
from playwright.sync_api import (
    sync_playwright,
    Browser,
    Page,
    Response,
    ElementHandle,
    TimeoutError,
    Playwright,
)

SEC_IN_MIL: int = 1000
GLOBAL_TIMEOUT: int = 5 * SEC_IN_MIL


def init_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def init_browser(playwright: Playwright, headless: bool = False) -> Browser:
    logging.info("initializing browser...")
    browser: Browser = playwright.chromium.launch(
        headless=headless,
    )
    logging.info("browser initialized.")
    return browser


def init_page(browser: Browser, default_timeout: int = GLOBAL_TIMEOUT) -> Page:
    logging.info("initializing page...")
    page: Page = browser.new_page()
    # set viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.set_default_timeout(GLOBAL_TIMEOUT)
    logging.info("page initialized.")
    return page


def goto_url(page: Page, url: str) -> Response:
    return page.goto(url)


def now_str(dt_fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.datetime.now().strftime(dt_fmt)


def get_5999_won_concurrency(page: Page, is_safe: bool = True) -> float:
    url: str = "https://www.thecashback.kr/exchangerate.php"
    logging.info(f"getting 5999 won price from {url}...")
    goto_url(page, url)
    left_input: Optional[ElementHandle] = page.query_selector("#left_input")
    price: str = left_input.input_value()
    logging.info(f"5999 won price: {price}")

    return float(price) - 0.03 if is_safe else float(price)


def goto_amazon(page: Page) -> None:
    url: str = "https://www.amazon.com/gp/product/B086KKT3RX"
    logging.info(f"going to {url}...")
    goto_url(page, url)


def type_price_and_submit(page: Page, price: str) -> None:
    logging.info(f"typing price {price}...")
    page.type("#gcui-asv-reload-form-custom-amount", price)
    logging.info("submitting...")
    page.click("input[type='submit'][name='submit.gc-buy-now']")


def login(page: Page, email: str, password: str) -> None:
    logging.info("logging in...")
    page.type("#ap_email", email)
    logging.info("typed email. clicking continue...")
    page.click("#continue")
    # wait for page to load
    logging.info("waiting for password input...")
    page.wait_for_selector("#ap_password")
    logging.info("found password input. typing password...")
    page.type("#ap_password", password)
    logging.info("typed password. clicking login...")
    page.click("#signInSubmit")
    logging.info("login complete.")


def captcha_solve(page: Page, password: str) -> None:
    try:
        captcha_element: ElementHandle = page.wait_for_selector(
            "#auth-captcha-image",
        )
        logging.info("found captcha element.")
        password_element: ElementHandle = page.wait_for_selector(
            "#ap_password",
        )
        logging.info("found password element. typing password...")
        password_element.type(password)
        logging.info("typed password. solving captcha...")
        with open("captcha.png", "wb") as f:
            captcha_bytes: bytes = captcha_element.screenshot()
            f.write(captcha_bytes)
        logging.info("solve captcha manually.")
        captcha_string: str = input("SOLVE CAPTCHA STRING: ")
        page.type("#auth-captcha-guess", captcha_string)
        logging.info("solved captcha. submitting...")
        page.click("#signInSubmit")
        logging.info("submitted.")

    except TimeoutError:
        logging.info("no captcha found. continuing...")


def file_save_decorator(func):
    @wraps(func)
    def wrapper(
        page: Page, out_path: str | PathLike = f"out_{now_str()}", **kwargs
    ) -> None:
        with Path(out_path).open(**kwargs) as f:
            result: str | bytes = func(page, out_path)
            f.write(result)

    return wrapper


@file_save_decorator
def save_html(page: Page, mode: str = "w", encoding: str = "utf-8") -> str:
    return page.content()


@file_save_decorator
def save_screenshot(page: Page, mode="wb") -> bytes:
    return page.screenshot()


def buy_reload(
    page: Page,
    password: str,
) -> None:
    captcha_solve(page, password)
    # check email verification
    try:
        logging.info("Checking email verification needed...")
        page.wait_for_selector(
            "#channelDetailsWithImprovedLayout",
        )
        logging.info("Email verification needed.")
        logging.info("Press enter verification code in your email.")
        input("ENTER TO CONTINUE: ")
        logging.info("continuing...")
    except TimeoutError:
        logging.info("Email verification not needed.")

    # disable amazon currency converter
    try:
        logging.info("Trying to disable amazon currency converter...")
        disable_radio: ElementHandle = page.wait_for_selector(
            "#marketplaceRadio",
        )
        disable_radio.click()
        logging.info("clicked disable. waiting for order button...")
    except TimeoutError as e:
        logging.info(f"no currency converter found: {e}")

    try:
        logging.info("waiting for order button...")
        page.wait_for_selector(
            """input[type="submit"][name="placeYourOrder1"]"""
        )
        logging.info("found order button.")
    except TimeoutError:
        logging.info("no order button found. screenshotting...")
        save_screenshot(page, out_path=f"error_{now_str()}.png")
        logging.info("extracting html...")
        # save html
        save_html(page, out_path=f"error_{now_str()}.html")

    # block below line if you want to not buy
    page.click("""input[type="submit"][name="placeYourOrder1"]""")
    logging.info(
        "clicked order button. waiting for order confirmation button ..."
    )
    page.wait_for_selector("#widget-purchaseConfirmationDetails")
    logging.info("job finished. quit...")
    save_html(page, out_path=f"result_{now_str()}.html")
    page.close()


def process_reload_all(
    browser: Browser,
    email: str,
    password: str,
    is_safe: bool = True,
    default_timeout: int = GLOBAL_TIMEOUT,
) -> None:
    page: Page = init_page(browser=browser, default_timeout=default_timeout)
    price: str = str(get_5999_won_concurrency(page=page, is_safe=is_safe))
    goto_amazon(page)
    type_price_and_submit(page, price)
    login(page, email, password)
    buy_reload(page, password)
    browser.close()


def load_yaml_config(file_path: Path | str) -> Mapping[str, Any]:
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with open(file_path, mode="r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args():
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "--safe",
        default=True,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--timeout", default=5, type=int, help="timeout in seconds"
    )
    return parser.parse_args()


class Config(TypedDict):
    email: str
    password: str


if __name__ == "__main__":
    init_logger()
    args: argparse.Namespace = parse_args()
    pw_core: Playwright = sync_playwright().start()
    playwright_browser: Browser = init_browser(pw_core)
    config: Config = Config(**load_yaml_config("config.yml"))

    process_reload_all(
        playwright_browser,
        is_safe=args.safe,
        default_timeout=GLOBAL_TIMEOUT,
        **config,
    )
