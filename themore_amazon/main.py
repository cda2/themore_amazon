import argparse
import logging
import sys
from argparse import ArgumentParser
from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from playwright.sync_api import (
    Browser,
    ElementHandle,
    Page,
    Playwright,
    Response,
    TimeoutError,
)

from themore_amazon.captcha_solve import (
    is_captcha_present,
    solve_captcha_with_solver,
)
from themore_amazon.utils import (
    now_str,
    save_html,
    save_screenshot,
)

SEC_IN_MIL: int = 1000
GLOBAL_TIMEOUT: int = int(6.5 * SEC_IN_MIL)


def init_browser(playwright: Playwright, headless: bool = False) -> Browser:
    logging.info("initializing browser...")
    browser: Browser = playwright.firefox.launch(
        headless=headless,
    )
    logging.info("browser initialized.")
    return browser


def init_page(browser: Browser, default_timeout: int = GLOBAL_TIMEOUT) -> Page:
    logging.info("initializing page...")
    page: Page = browser.new_page()
    # set viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.set_default_timeout(default_timeout)
    logging.info("page initialized.")
    return page


def goto_url(page: Page, url: str) -> Response:
    return page.goto(url)


def get_5999_won_currency(page: Page, is_safe: bool = True) -> Decimal:
    url: str = "https://www.thecashback.kr/exchangerate.php"
    logging.info(f"getting 5999 won price from {url}...")
    goto_url(page, url)
    left_input: ElementHandle | None = page.wait_for_selector("#left_input")
    price: str = left_input.input_value().strip()
    if not price or price == "0":
        logging.error("price is empty. maybe not operating time?")
        sys.exit(1)

    logging.info(f"5999 won price: {price}")
    dec_price: Decimal = Decimal(price)

    if is_safe:
        dec_price -= Decimal("0.01")

    return dec_price


def goto_amazon(page: Page) -> None:
    url: str = "https://www.amazon.com/gp/product/B086KKT3RX"
    logging.info(f"going to {url}...")
    goto_url(page, url)


def type_price_and_submit(page: Page, price: str) -> None:
    price_input_sel: str = "#gcui-asv-reload-form-custom-amount"
    submit_btn_sel: str = "input[type='submit'][name='submit.gc-buy-now']"

    # 1. find price input
    price_input: ElementHandle = page.wait_for_selector(price_input_sel)

    # 2. clear price input
    price_input.fill("")

    # 3. type price
    price_input.type(price)

    # 4. wait for submit button (active state, not disabled)
    logging.info("waiting for submit button...")
    submit_btn_element: ElementHandle = page.wait_for_selector(submit_btn_sel)

    # 5. check price input value,
    # price input cleared when submit button is active in some cases
    logging.info("found submit button. wait to disable predefined price...")
    try:
        page.wait_for_selector(
            ".gcui-asv-reload-predefined-amount-button[aria-checked='true']",
        )
    except TimeoutError:
        logging.info("not found any active predefined price. continue...")

    price_input_value: str = price_input.input_value().strip()
    logging.info(f"price input value: {price_input_value}")

    while not price_input_value or price_input_value != price:
        page.wait_for_timeout(500)
        logging.warning("price input value is not correct. re-typing price...")
        price_input.fill("")
        price_input.type(price)
        price_input_value = price_input.input_value().strip()

    # 6. click submit button
    assert price_input_value == price
    logging.info("price input value is correct. clicking submit button...")
    submit_btn_element.click()


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


def buy_reload(
        page: Page,
) -> None:
    # check email verification
    try:
        logging.info("checking email verification needed...")
        page.wait_for_selector(
            "#channelDetailsWithImprovedLayout",
        )
        logging.info("email verification needed.")
        logging.info("check your email.")
        input("ENTER ANYTHING TO CONTINUE: ")
        logging.info("continuing...")
    except TimeoutError:
        logging.info("email verification not needed.")

    # disable amazon currency converter
    try:
        logging.info("trying to disable amazon currency converter...")
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
            """input[type="submit"][name="placeYourOrder1"]""",
        )
        logging.info("found order button.")
    except TimeoutError:
        logging.error("no order button found. screenshotting...")
        save_screenshot(page, out_path=f"error_{now_str()}.png")
        logging.warning("extracting html...")
        # save html
        save_html(page, out_path=f"error_{now_str()}.html")
        logging.warning("exiting...")
        sys.exit(1)

    # block below line if you want to not buy
    page.click("""input[type="submit"][name="placeYourOrder1"]""")
    logging.info(
        "clicked order button. waiting for order confirmation button ...",
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
    dollar_dec: Decimal = get_5999_won_currency(page=page, is_safe=is_safe)
    price: str = str(dollar_dec.quantize(Decimal("1e-2")))
    try:
        goto_amazon(page)
        if is_captcha_present(page):
            solve_captcha_with_solver(page)
        type_price_and_submit(page, price)
        login(page, email, password)
        if is_captcha_present(page):
            solve_captcha_with_solver(page)
        buy_reload(page)
    except Exception as e:
        logging.error(f"error occured: {e}")
        save_screenshot(page, out_path=f"error_{now_str()}.png")
    finally:
        browser.close()


def load_yaml_config(file_path: Path | str) -> Mapping[str, Any]:
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with Path.open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_args():
    parser: ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--safe",
        default=True,
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--timeout",
        default=GLOBAL_TIMEOUT,
        type=int,
        help="timeout in milliseconds",
    )
    parser.add_argument(
        "--headless",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    return parser.parse_args()
