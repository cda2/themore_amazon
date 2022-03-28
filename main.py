import logging
from typing import Optional

from playwright.sync_api import sync_playwright, Browser, Page, Response, ElementHandle, TimeoutError, Playwright


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


def init_page(browser: Browser) -> Page:
    logging.info("initializing page...")
    page: Page = browser.new_page()
    # set viewport
    page.set_viewport_size({"width": 1920, "height": 1080})
    logging.info("page initialized.")
    return page


def goto_url(page: Page, url: str) -> Response:
    return page.goto(url)


def get_5999_won_concurrency(page: Page) -> str:
    url: str = "https://www.thecashback.kr/exchangerate.php"
    logging.info(f"getting 5999 won price from {url}...")
    goto_url(page, url)
    logging.info("waiting 10 seconds to get 5999 won price safely...")
    page.wait_for_timeout(10000)
    left_input: Optional[ElementHandle] = page.query_selector("#left_input")
    price: str = left_input.input_value()
    # check if 5999 won price is available
    str(float(price))
    logging.info(f"5999 won price: {price}")
    return price


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
        captcha_element: ElementHandle = page.wait_for_selector("#auth-captcha-image", timeout=10000)
        logging.info("found captcha element.")
        password_element: ElementHandle = page.wait_for_selector("#ap_password", timeout=10000)
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


def save_result(page: Page) -> None:
    result_html: str = page.content()
    with open("result.html", mode="w", encoding="utf-8") as f:
        f.write(result_html)


def buy_reload(page: Page, password: str) -> None:
    captcha_solve(page, password)
    # check email verification
    try:
        logging.info("Checking email verification needed...")
        page.wait_for_selector("#channelDetailsWithImprovedLayout", timeout=10000)
        logging.info("Email verification needed.")
        logging.info("Press enter after verified your email.")
        input("ENTER TO CONTINUE: ")
        logging.info("continuing...")
    except TimeoutError:
        logging.info("Email verification not needed.")

    # disable amazon currency converter
    try:
        logging.info("Trying to disable amazon currency converter...")
        disable_radio: ElementHandle = page.wait_for_selector("#marketplaceRadio", timeout=10000)
        disable_radio.click()
        logging.info("clicked disable. waiting for order button...")
    except TimeoutError as e:
        logging.info(f"no currency converter found: {e}")
    try:
        logging.info("waiting for order button...")
        page.wait_for_selector('''input[type="submit"][name="placeYourOrder1"]''')
        logging.info("found order button.")
    except TimeoutError:
        logging.info("no order button found. screenshotting...")
        screenshot_buffer: bytes = page.screenshot()
        # save screenshot
        with open("screenshot.png", "wb") as f:
            f.write(screenshot_buffer)
        logging.info("extracting html...")
        html: str = page.content()
        # save html
        with open("html.html", mode="w", encoding="utf-8") as f:
            f.write(html)
    page.click('''input[type="submit"][name="placeYourOrder1"]''')
    logging.info("clicked order button. waiting for order confirmation button ...")
    page.wait_for_selector("#widget-purchaseConfirmationDetails")
    logging.info("job finished. wait for 5 seconds to check result...")
    page.wait_for_timeout(5000)
    logging.info("waited for 10 seconds. quit...")
    save_result(page)
    page.close()


def process_reload_all(browser: Browser, email: str, password: str):
    page: Page = init_page(browser)
    price: str = get_5999_won_concurrency(page)
    goto_amazon(page)
    type_price_and_submit(page, price)
    login(page, email, password)
    buy_reload(page, password)
    browser.close()


if __name__ == "__main__":
    init_logger()
    play_wright: Playwright = sync_playwright().start()
    bs: Browser = init_browser(play_wright)
    process_reload_all(bs, "ID", "PW")
