from base64 import encode
import json
from datetime import datetime
from pathlib import Path
from pprint import pprint

import pytest
from app import app
from moto import mock_dynamodb
from models import Crossword


@pytest.fixture(scope="function", autouse=True)
def mock_dynamodb_fixture():
    _mock_dynamodb = mock_dynamodb()
    _mock_dynamodb.start()
    # テーブル作成
    Crossword.create_table()
    # データ作成
    with open("tests/data/crosswords.json", encoding="utf-8") as f:
        crossword = json.load(f)[0]
    crossword_item = Crossword()
    crossword_item.from_json(json.dumps(crossword, ensure_ascii=False))
    crossword_item.save()
    yield
    _mock_dynamodb.stop()


@pytest.fixture()
def url_event():
    """Generates API GW Event

    https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html#:~:text=Request%20payload%20format
    """

    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/my/path",
        "rawQueryString": "parameter1=value1&parameter1=value2&parameter2=value",
        "cookies": ["cookie1", "cookie2"],
        "headers": {"header1": "value1", "header2": "value1,value2"},
        "queryStringParameters": {"parameter1": "value1,value2", "parameter2": "value"},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "<urlid>",
            "authentication": None,
            "authorizer": {
                "iam": {
                    "accessKey": "AKIA...",
                    "accountId": "111122223333",
                    "callerId": "AIDA...",
                    "cognitoIdentity": None,
                    "principalOrgId": None,
                    "userArn": "arn:aws:iam::111122223333:user/example-user",
                    "userId": "AIDA...",
                }
            },
            "domainName": "<url-id>.lambda-url.us-west-2.on.aws",
            "domainPrefix": "<url-id>",
            "http": {
                "method": "POST",
                "path": "/my/path",
                "protocol": "HTTP/1.1",
                "sourceIp": "123.123.123.123",
                "userAgent": "agent",
            },
            "requestId": "id",
            "routeKey": "$default",
            "stage": "$default",
            "time": "12/Mar/2020:19:03:58 +0000",
            "timeEpoch": 1583348638390,
        },
        "body": "Hello from client!",
        "pathParameters": {},
        "isBase64Encoded": False,
        "stageVariables": None,
    }


def test_compute_01(url_event):
    # prepare event
    words = ["としみち", "きようたく", "しひよう", "ろくじゆう"]
    url_event["requestContext"]["http"]["path"] = "/compute"
    url_event["requestContext"]["http"]["method"] = "GET"
    url_event["queryStringParameters"] = {
        "words": ",".join(words),
    }
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    pprint(data, compact=True)
    # assert "location" in data.dict_keys()


def test_compute_02(url_event):
    # prepare event
    words = ["あかり", "あぶら", "らいす", "わわわ"]
    url_event["requestContext"]["http"]["path"] = "/compute"
    url_event["requestContext"]["http"]["method"] = "GET"
    url_event["queryStringParameters"] = {
        "words": ",".join(words),
    }
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    pprint(data, compact=True)
    with Path(__file__).parent.joinpath('logs/compute_02.json').open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def test_list_01(url_event):
    # prepare event
    url_event["requestContext"]["http"]["path"] = "/"
    url_event["requestContext"]["http"]["method"] = "GET"
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 200
    data = json.loads(ret["body"])
    pprint(data, compact=True)


def test_get_01(url_event):
    # prepare event
    url_event["requestContext"]["http"]["path"] = "/4abe99c87a714fc8a7c7f5cdd43e4572"
    url_event["requestContext"]["http"]["method"] = "GET"
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    pprint(data, compact=True)
    with Path(__file__).parent.joinpath('logs/get_01.json').open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def test_get_02(url_event):
    # prepare event
    url_event["requestContext"]["http"]["path"] = "/not-exist"
    url_event["requestContext"]["http"]["method"] = "GET"
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 404


def test_create_01(url_event):
    Crossword.create_table()

    with open("tests/data/crosswords.json", encoding="utf-8") as f:
        crossword = json.load(f)[0]
    params = {
        "title": "ユニットテスト " + datetime.now().isoformat(timespec="milliseconds"),
        "rows": crossword["rows"],
        "cols": crossword["cols"],
        "words": crossword["words"],
    }
    # イベント準備
    url_event["requestContext"]["http"]["path"] = "/"
    url_event["requestContext"]["http"]["method"] = "POST"
    url_event["body"] = json.dumps(params, ensure_ascii=False)
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 201
    data = json.loads(ret["body"])
    pprint(data, compact=True)


def test_update_01(url_event):
    with open("tests/data/crosswords.json", encoding="utf-8") as f:
        crossword = json.load(f)[0]
    crossword_item = Crossword()
    crossword_item.from_json(json.dumps(crossword, ensure_ascii=False))
    for w in crossword_item.words:
        w.clue = "ヒント"
    params = {
        "title": "更新テスト " + datetime.now().isoformat(timespec="milliseconds"),
        "words": [w.attribute_values for w in crossword_item.words],
    }
    # イベント準備
    url_event["requestContext"]["http"]["path"] = "/" + crossword_item.crossword_id
    url_event["requestContext"]["http"]["method"] = "PUT"
    url_event["body"] = json.dumps(params, ensure_ascii=False)
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 200
    crossword_item.refresh()
    pprint(crossword_item.attribute_values, compact=True)
    with Path(__file__).parent.joinpath('logs/update_01_req.json').open('w', encoding='utf-8') as f:
        json.dump(params, f, ensure_ascii=False, indent=2)


def test_delete_01(url_event):
    with open("tests/data/crosswords.json", encoding="utf-8") as f:
        crossword = json.load(f)[0]
    crossword_item = Crossword()
    crossword_item.from_json(json.dumps(crossword, ensure_ascii=False))
    # イベント準備
    url_event["requestContext"]["http"]["path"] = "/" + crossword_item.crossword_id
    url_event["requestContext"]["http"]["method"] = "DELETE"
    # execute lambda
    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 200
    with pytest.raises(Crossword.DoesNotExist):
        crossword_item.refresh()


def test_router_01(url_event):
    # イベント準備
    url_event["requestContext"]["http"]["path"] = "/"
    url_event["requestContext"]["http"]["method"] = "DELETE"

    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 405


def test_router_02(url_event):
    # イベント準備
    url_event["requestContext"]["http"]["path"] = "/not-exist"
    url_event["requestContext"]["http"]["method"] = "GET"

    ret = app.lambda_handler(url_event, "")
    assert ret["statusCode"] == 404
