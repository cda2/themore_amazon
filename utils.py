import datetime
import logging
from functools import partial, wraps
from os import PathLike
from pathlib import Path
from typing import TypedDict

from playwright.sync_api import Page


def now_str(dt_fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.datetime.now().strftime(dt_fmt)


def file_save_decorator(func, is_bytes: bool = False):
    @wraps(func)
    def wrapper(
        page: Page,
        out_path: str | PathLike = f"out_{now_str()}",
        **kwargs,
    ) -> None:
        exec_result: str | bytes = func(page, **kwargs)
        path: Path = Path(out_path)
        if is_bytes:
            path.write_bytes(exec_result)
        else:
            path.write_text(exec_result)

    return wrapper


text_save_decorator = file_save_decorator

bytes_save_decorator = partial(file_save_decorator, is_bytes=True)


@text_save_decorator
def save_html(page: Page) -> str:
    return page.content()


@bytes_save_decorator
def save_screenshot(page: Page) -> bytes:
    return page.screenshot()


class Config(TypedDict):
    email: str
    password: str


def init_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
