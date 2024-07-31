from urllib.request import urlopen
from urllib.parse import urlencode, quote
from concurrent.futures import ThreadPoolExecutor
import json

from endstone import ColorFormat

BLACKBE_API = "https://api.blackbe.work/openapi/v3/check?"
STATUS_UNBAN = 2001
STATUS_BAN = 2000

executor = ThreadPoolExecutor()


class BlackBeStatus:
    def __init__(self, name: str, xuid: str, info: str, level: int, qq: int):
        self.name = name
        self.xuid = xuid
        self.info = info
        self.level = level
        self.qq = qq

    def __str__(self):
        return (f"{ColorFormat.GREEN}Name: {ColorFormat.WHITE}{self.name}\n"
                f"{ColorFormat.GREEN}Xuid: {ColorFormat.WHITE}{self.xuid}\n"
                f"{ColorFormat.GREEN}Info: {ColorFormat.WHITE}{self.info}\n"
                f"{ColorFormat.GREEN}Level: {ColorFormat.WHITE}{self.level}\n"
                f"{ColorFormat.GREEN}QQ: {ColorFormat.WHITE}{self.qq}")


def query_status_by_qq(qq: int, callback) -> None:
    url = BLACKBE_API + "qq=" + str(qq)
    _query_status(url, callback)


def query_status_by_name(name: str, callback) -> None:
    url = BLACKBE_API + "name=" + quote(name)
    _query_status(url, callback)


def _query_status(url: str, callback) -> None:
    def task():
        req = urlopen(url)
        if req.getcode() != 200:
            print(f"APIERROR:errcode={req.getcode()}")
            return

        result = json.loads(req.read())
        if result["status"] == STATUS_UNBAN:
            callback(None)
            return

        data = result["data"]["info"][0]
        status = BlackBeStatus(
            name=data["name"],
            xuid=data["xuid"],
            info=data["info"],
            level=data["level"],
            qq=data["qq"]
        )

        callback(status)

    executor.submit(task)
