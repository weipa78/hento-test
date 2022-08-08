from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UTCDateTimeAttribute,
    UnicodeAttribute,
)
from pynamodb.models import Model

import config


class CrosswordWord(MapAttribute):
    answer = UnicodeAttribute(null=False)
    clue = UnicodeAttribute(null=False)
    row = NumberAttribute(null=False)
    col = NumberAttribute(null=False)
    direction = NumberAttribute(null=False)  # 0: across, 1: down

    def __repr__(self):
        return str(self.attribute_values)


class Crossword(Model):
    class Meta:
        table_name = config.ENV + "Crossword"
        region = "ap-northeast-1"

    crossword_id = UnicodeAttribute(hash_key=True)
    words = ListAttribute(of=CrosswordWord, null=False)
    rows = NumberAttribute(null=False)
    cols = NumberAttribute(null=False)

    creator = UnicodeAttribute(null=True)
    title = UnicodeAttribute(null=True)

    created_at = UTCDateTimeAttribute(null=False)
    updated_at = UTCDateTimeAttribute(null=False)
