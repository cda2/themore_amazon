from argparse import ArgumentParser
from logging import getLevelName

from themore_amazon.main import (
    load_yaml_config,
    process_reload_all,
)
from themore_amazon.utils import Config, init_logger


def main(config_path: str, log_level: str) -> None:
    init_logger(getLevelName(log_level))
    config: Config = load_yaml_config(str(config_path))
    process_reload_all(config=config)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.yml",
        help="path to config file",
    )
    parser.add_argument(
        "-l",
        "--log-level",
        type=str,
        default="INFO",
        help="logging level",
    )
    args = parser.parse_args()
    main(args.config, args.log_level)
