import datetime
import logging
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial, wraps
from os import PathLike
from pathlib import Path

from playwright.sync_api import Page


def now_str(dt_fmt: str = "%Y%m%d_%H%M%S") -> str:
    return datetime.datetime.now().strftime(dt_fmt)


def file_save_decorator(
    func: Callable[[Page], str | bytes],
    is_bytes: bool = False,
) -> Callable[[Page, str | PathLike], None]:
    @wraps(func)
    def wrapper(
        page: Page,
        out_path: str | PathLike = f"out_{now_str()}",
    ) -> None:
        exec_result: str | bytes = func(page)
        path: Path = Path(out_path)
        # if path not exists, create it
        path.parent.mkdir(parents=True, exist_ok=True)
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


@dataclass(frozen=True, slots=True, kw_only=True)
class Config:
    email: str
    password: str
    timeout: float = 10000.0
    headless: bool = False
    min_order_price: float = 5.0
    is_safe: bool = True
    safe_gap: float = 1.0


def init_logger(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
