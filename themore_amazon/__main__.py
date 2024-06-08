from argparse import ArgumentParser

from themore_amazon.main import (
    load_yaml_config,
    process_reload_all,
)
from themore_amazon.utils import Config, init_logger


def main(config_path: str) -> None:
    init_logger()
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
    args = parser.parse_args()
    main(args.config)
