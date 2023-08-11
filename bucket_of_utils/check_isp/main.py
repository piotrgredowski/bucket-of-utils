"""
Module for checking if the current internet service provider is the one you specify.

Usage:
    ```bash
    python -m bucket_of_utils.check_isp --part-of-name "Orange" --exclude-in-name "Mobile"
    ```
"""
from http import HTTPStatus
from typing import Optional
from typing import TypedDict

import requests


class ResponseData(TypedDict):
    org: str


def check_isp(*, include_in_name: Optional[str] = None, exclude_in_name: Optional[str] = None):
    if all((include_in_name is None, exclude_in_name is None)):
        msg = "You must specify at least one of the parameters: include_in_name, exclude_in_name"
        raise ValueError(msg)

    check_ip_url = "https://ipinfo.io"

    response = requests.get(check_ip_url)

    if response.status_code != HTTPStatus.OK:
        msg = f"Error: {response.status_code}"
        raise RuntimeError(msg)

    is_it = False

    include_in_name = include_in_name.lower() if include_in_name is not None else None
    exclude_in_name = exclude_in_name.lower() if exclude_in_name is not None else None

    data: ResponseData = response.json()
    org = data["org"].lower()

    if include_in_name is not None and include_in_name in org:
        is_it = True

    if exclude_in_name is not None and exclude_in_name in org:
        is_it = False
    return is_it


def main():
    def _run(*, include_in_name: Optional[str] = None, exclude_in_name: Optional[str] = None):
        is_it = check_isp(include_in_name=include_in_name, exclude_in_name=exclude_in_name)
        print(is_it)

    import typer

    print(typer.run(_run))


if __name__ == "__main__":
    main()
