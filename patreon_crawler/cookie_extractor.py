import os

import browser_cookie3


def get_cookies(cookie_file: str, domain_name: str) -> dict[str, str] | None:
    """
    Get *Chrome* cookies for the specified domain
    :param cookie_file: The path to the cookies file or 'auto' to search for the default location
    :param domain_name: The domain to get the cookies for
    :return: A dictionary of cookies
    """

    if cookie_file != "auto":
        return _get_cookies(cookie_file, domain_name)
    return _get_cookies(None, domain_name)


def _get_cookies(cookie_file: str | None, domain_name: str) -> dict[str, str] | None:
    if cookie_file is not None and not os.path.isfile(cookie_file):
        cookie_file += "\\Cookies"
    cookies = browser_cookie3.chrome(cookie_file, domain_name)
    return {
        cookie.name: cookie.value
        for cookie in cookies
    }
