import json
from argparse import ArgumentParser

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException
from nextflight import extract

from guns_lol_scraper.constants import (
    CHALLENGE_DICT_KEY,
    CONFIG_KEY,
    OPTIONAL_KEYS,
    EXIT_FAILURE,
    URL_MATCH_REGEX,
)

from loguru import logger

import re


def main():
    parser = ArgumentParser()

    parser.add_argument("--keep-all", "--all", action="store_true", dest="keep_all")

    parser.add_argument(
        "--keep-config",
        action="append_const",
        dest="keep",
        const=CONFIG_KEY,
        default=[],
    )

    parser.add_argument(
        "--keep-challenge",
        action="append_const",
        dest="keep",
        const=CHALLENGE_DICT_KEY,
        default=[],
    )

    parser.add_argument(
        "--indent", "-i", 
        action="store", 
        dest="indent", 
        type=int, 
        default=4
    )

    parser.add_argument("url", action="store", type=str)

    args = parser.parse_args()

    if re.fullmatch(URL_MATCH_REGEX, args.url) is None:
        logger.error("Failed to match guns.lol url")
        exit(EXIT_FAILURE)

    if args.keep_all:
        keep = OPTIONAL_KEYS
    else:
        keep = set(args.keep)

    try:
        r = requests.get(args.url)
        r.raise_for_status()
    except RequestException:
        logger.exception("Failed to make request to guns.lol profile")
        exit(EXIT_FAILURE)

    html = r.text

    page = extract(html)

    account_info: dict = page.find_by_keys(["account_created"])

    inverse_keys = OPTIONAL_KEYS - keep

    for key in inverse_keys:
        account_info.pop(key, None)

    print(json.dumps(account_info, indent=4))


if __name__ == "__main__":
    main()
