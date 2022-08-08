from pprint import pprint

import requests

ORIGIN = "https://pidc7pzvalqalb4l5vu2xqjkly0nswnm.lambda-url.ap-northeast-1.on.aws/"


def test_01():
    #
    words = ["としみち", "きようたく", "しひよう", "ろくじゆう"]
    res = requests.get(ORIGIN, params={"mode": "compute", "words": ",".join(words)})
    pprint(res.json(), compact=True)
    print("url:", ORIGIN + "?words=" + ",".join(words))


def test_02():
    res = requests.get(
        ORIGIN,
        params={
            "mode": "get",
            "crossword_id": "4abe99c87a714fc8a7c7f5cdd43e4572",
        },
    )
    pprint(res.json(), compact=True)
