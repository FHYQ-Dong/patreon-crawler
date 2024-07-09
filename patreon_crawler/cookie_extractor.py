import os
import glob

import browser_cookie3


def get_cookies(cookie_file: str, domain_name: str) -> list[tuple[str, str]]:
    if cookie_file != "auto":
        return _get_cookies(cookie_file, domain_name)

    default_cookie_files_paths = [
        'Google\\Chrome\\User Data\\Default\\Cookies',
        'Google\\Chrome\\User Data\\Default\\Network\\Cookies',
        'Google\\Chrome\\User Data\\Profile *\\Cookies',
        'Google\\Chrome\\User Data\\Profile *\\Network\\Cookies'
    ]

    paths = []
    for _path in default_cookie_files_paths:
        paths.extend(glob.glob(os.path.expandvars(f"%LOCALAPPDATA%\\{_path}")))

    for path in paths:
        try:
            cookies = _get_cookies(path, domain_name)
            if cookies:
                return cookies
        except Exception as e:
            print(f"Failed to get cookies from {path}: {e}")


def _get_cookies(cookie_file: str, domain_name: str) -> list[tuple[str, str]]:
    cookies = browser_cookie3.chrome(cookie_file, domain_name)
    return [
        (cookie.name, cookie.value)
        for cookie in cookies
    ]
