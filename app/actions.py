import json
from copy import deepcopy
from datetime import datetime
from typing import TypedDict
from uuid import uuid4

from genxword.calculate import Crossword as GenxCrossword
from genxword.control import Genxword
from models import Crossword, CrosswordWord

EMPTY = "-"

WORD_ANSWER_INDEX = 0
WORD_HINT_INDEX = 1
WORD_ROW_INDEX = 2
WORD_COL_INDEX = 3
WORD_DIRECTION_INDEX = 4
WORD_DIRECTION_ACROSS = 0
WORD_DIRECTION_DOWN = 1


class CrosswordCompute:
    class Data(TypedDict):
        words: str

    def execute(self, data: Data):
        query_words: str = data["words"]
        req_words: list[str] = []
        if query_words:
            req_words = query_words.split(",")

        gen = Genxword(auto=True, mixmode=False)
        gen.wlist(req_words, len(req_words))
        gen.grid_size()

        # クロスワードを作成
        calc = GenxCrossword(gen.nrow, gen.ncol, EMPTY, gen.wordlist)
        calc.compute_crossword()

        # 結果を取得。単語リストを開始行の昇順、開始列の昇順で並べ替える。
        word_list = deepcopy(
            sorted(
                calc.best_wordlist, key=lambda w: (w[WORD_ROW_INDEX], w[WORD_COL_INDEX])
            )
        )
        grid = deepcopy(calc.best_grid)

        indexes = self.trimmed_grid_indexes(grid)
        row_start = indexes["row_start"]
        row_stop = indexes["row_stop"]
        col_start = indexes["col_start"]
        col_stop = indexes["col_stop"]
        # グリッドを最小化する
        clean_grid = [row[col_start:col_stop] for row in grid[row_start:row_stop]]
        for word in word_list:
            word[WORD_ROW_INDEX] -= row_start
            word[WORD_COL_INDEX] -= col_start

        # 単語リストを整形
        res_word_list = {
            "across": {},
            "down": {},
        }
        count = 0
        for word in word_list:
            count += 1
            res_word = {
                "clue": word[WORD_ANSWER_INDEX] + "のヒント",
                "answer": word[WORD_ANSWER_INDEX],
                "row": word[WORD_ROW_INDEX],
                "col": word[WORD_COL_INDEX],
            }
            if word[WORD_DIRECTION_INDEX] == WORD_DIRECTION_ACROSS:
                res_word_list["across"][count] = res_word
            else:
                res_word_list["down"][count] = res_word
        # 使用不可能だった単語リスト
        unused_words = []
        used_words = [w[WORD_ANSWER_INDEX] for w in word_list]
        for word in req_words:
            if word not in used_words:
                unused_words.append(word)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    # "wordList": word_list,
                    "grid": clean_grid,
                    "wordList": res_word_list,
                    "unusedWords": unused_words,
                }
            ),
        }

    def trimmed_grid_indexes(self, grid: list[list[str]]) -> dict[str, int]:
        row_start = None
        row_stop = len(grid)
        col_start = None
        col_stop = len(grid[0])
        for i in range(len(grid)):
            if row_start is None:
                if any(grid[i][j] != EMPTY for j in range(len(grid[0]))):
                    row_start = i
            else:
                if all(grid[i][j] == EMPTY for j in range(len(grid[0]))):
                    row_stop = i
                    break
        for j in range(len(grid[0])):
            if col_start is None:
                if any(grid[i][j] != EMPTY for i in range(len(grid))):
                    col_start = j
            else:
                if all(grid[i][j] == EMPTY for i in range(len(grid))):
                    col_stop = j
                    break
        return {
            "row_start": row_start,
            "row_stop": row_stop,
            "col_start": col_start,
            "col_stop": col_stop,
        }


class CrosswordList:
    class Data(TypedDict):
        crossword_id: str

    def execute(self, data: Data):
        crosswords = []
        for item in Crossword.scan(
            limit=10, attributes_to_get=["title", "crossword_id"]
        ):
            crosswords.append(
                {
                    "title": item.title,
                    "crossword_id": item.crossword_id,
                }
            )
        return {
            "statusCode": 200,
            "body": json.dumps({"crosswords": crosswords}),
        }


class CrosswordGet:
    class Data(TypedDict):
        crossword_id: str

    def execute(self, data: Data):
        crossword_id: str = data["crossword_id"]
        try:
            crossword_item = Crossword.get(crossword_id)
        except Crossword.DoesNotExist:
            return {"statusCode": 404}
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "title": crossword_item.title,
                    "format": format_words(crossword_item.words),
                    "rows": crossword_item.rows,
                    "cols": crossword_item.cols,
                    "words": [w.attribute_values for w in crossword_item.words],
                }
            ),
        }


class CrosswordCreate:
    class RequiredData(TypedDict):
        words: list
        cols: int
        rows: int

    class Data(RequiredData, total=False):
        title: str

    def execute(self, data: Data):
        if "words" not in data or "rows" not in data or "cols" not in data:
            return {"statusCode": 422}
        crossword_id = uuid4().hex
        # データをセット
        crossword_item = Crossword()
        crossword_item.crossword_id = crossword_id
        crossword_item.words = data["words"]
        crossword_item.cols = data["cols"]
        crossword_item.rows = data["rows"]
        crossword_item.created_at = datetime.now()
        crossword_item.updated_at = datetime.now()
        if "title" in data:
            crossword_item.title = data["title"]
        # データを保存
        crossword_item.save()
        return {
            "statusCode": 201,
            "body": json.dumps(
                {
                    "crossword_id": crossword_id,
                }
            ),
        }


class CrosswordUpdate:
    class Data(TypedDict):
        crossword_id: str
        words: list
        title: str

    def execute(self, data: Data):
        crossword_id: str = data["crossword_id"]
        if "words" not in data or "title" not in data:
            return {"statusCode": 422}
        # データを取得
        try:
            crossword_item = Crossword.get(crossword_id)
        except Crossword.DoesNotExist:
            return {"statusCode": 404}
        # データを保存
        crossword_item.update(
            actions=[
                Crossword.words.set(data["words"]),
                Crossword.title.set(data["title"]),
                Crossword.updated_at.set(datetime.now()),
            ]
        )
        return {
            "statusCode": 200,
            "body": json.dumps({}),
        }


class CrosswordDelete:
    class Data(TypedDict):
        crossword_id: str

    def execute(self, data: Data):
        crossword_id: str = data["crossword_id"]
        try:
            crossword_item = Crossword.get(crossword_id)
        except Crossword.DoesNotExist:
            return {"statusCode": 404}
        crossword_item.delete()
        return {
            "statusCode": 200,
        }


def format_words(words: list[CrosswordWord]):
    res_word_list = {
        "across": {},
        "down": {},
    }
    count = 0
    for word in sorted(words, key=lambda w: (w.row, w.col)):
        count += 1
        res_word = {
            "clue": word.clue,
            "answer": word.answer,
            "row": word.row,
            "col": word.col,
        }
        if word.direction == WORD_DIRECTION_ACROSS:
            res_word_list["across"][count] = res_word
        else:
            res_word_list["down"][count] = res_word
    return res_word_list
