from typing import Any

from sqlalchemy.orm import declarative_base
from werkzeug.datastructures import MultiDict

Base = declarative_base()


def to_dict(orm) -> dict:
    return {c.name: getattr(orm, c.name) for c in orm.__table__.columns}


def query_multidict_to_orm(query: MultiDict[str, str], orm) -> dict[str, Any]:
    result = {}
    for column in orm.__table__.columns:
        if column.name in query:
            result[column.name] = column.type.python_type(query[column.name])
    return result
