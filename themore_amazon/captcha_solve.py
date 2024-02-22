import logging

from amazoncaptcha import AmazonCaptcha
from playwright.sync_api import ElementHandle, Page


def is_captcha_present(page: Page) -> bool:
    logging.info("checking if captcha is present...")
    return (
        page.query_selector("form[action='/errors/validateCaptcha']")
        is not None
    )


def solve_captcha_with_solver(page: Page) -> str:
    logging.info("solving captcha with solver...")

    logging.info("finding captcha image ElementHandle...")
    # 1. find captcha image ElementHandle
    captcha_image: ElementHandle = page.wait_for_selector(
        "form[action='/errors/validateCaptcha'] img[src*='Captcha']",
    )
    # 2. get captcha image src
    logging.info("getting captcha image src...")
    captcha_image_src: str = captcha_image.get_attribute("src")
    # 3. create captcha solver
    logging.info("creating captcha solver...")
    solver: AmazonCaptcha = AmazonCaptcha.fromlink(captcha_image_src)
    # 4. solve captcha
    logging.info("solving captcha...")
    solved_answer: str = solver.solve()
    # 5. type captcha answer to input
    logging.info("typing captcha answer to input...")
    logging.info(f"captcha answer: {solved_answer}")
    page.type("#captchacharacters", solved_answer)
    # 6. submit captcha
    logging.info("submitting captcha...")
    page.click("form[action='/errors/validateCaptcha'] button[type='submit']")

    return solved_answer
