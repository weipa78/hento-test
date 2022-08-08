import json
from actions import CrosswordCompute, CrosswordCreate, CrosswordDelete, CrosswordGet, CrosswordList, CrosswordUpdate


def lambda_handler(event, context):
    action = None
    response = None
    method_not_allowed: bool = False
    not_found: bool = False

    segments: str = str(event["requestContext"]["http"]["path"]).strip("/").split("/")
    method: str = event["requestContext"]["http"]["method"]

    if len(segments) == 1:
        if segments == ['']:
            if method == "GET":
                action = CrosswordList()
                data = {}
                response = action.execute(data)
            elif method == "POST":
                action = CrosswordCreate()
                data: CrosswordCreate.Data = json.loads(event["body"])
                response = action.execute(data)
            else:
                method_not_allowed = True
        elif segments == ["compute"]:
            if method == "GET":
                action = CrosswordCompute()
                data: CrosswordCompute.Data = {
                    "words": event["queryStringParameters"].get("words")
                }
                response = action.execute(data)
            else:
                method_not_allowed = True
        else:
            if method == "GET":
                action = CrosswordGet()
                data: CrosswordGet.Data = {
                    "crossword_id": segments[0]
                }
                response = action.execute(data)
            elif method == "PUT":
                action = CrosswordUpdate()
                data: CrosswordUpdate.Data = {
                    "crossword_id": segments[0]
                }
                data.update(json.loads(event["body"]))
                response = action.execute(data)
            elif method == "DELETE":
                action = CrosswordDelete()
                data: CrosswordDelete.Data = {
                    "crossword_id": segments[0]
                }
                response = action.execute(data)
            else:
                method_not_allowed = True
    else:
        not_found = True

    if not_found:
        return { "statusCode": 404 }
    if method_not_allowed:
        return { "statusCode": 405 }

    return response
