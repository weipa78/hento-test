from crossword.models import Crossword
import json

if __name__ == '__main__':
    """_summary_
    python -m tools.migrate
    """
    if not Crossword.exists():
        Crossword.create_table(billing_mode='PAY_PER_REQUEST', wait=True)

    # クロスワードのデータを追加
    with open('tests/data/crosswords.json', encoding='utf-8') as f:
        crosswords = json.load(f)
    for crossword in crosswords:
        crossword_item = Crossword()
        crossword_item.from_json(json.dumps(crossword, ensure_ascii=False))
        crossword_item.save()
