from typing import Any

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def orm_to_dict(orm) -> dict:
    return {c.name: getattr(orm, c.name) for c in orm.__table__.columns}


def dict_to_orm(_dict: dict[str, str], orm) -> dict[str, Any]:
    result = {}
    for column in orm.__table__.columns:
        if column.name in _dict:
            result[column.name] = column.type.python_type(_dict[column.name])
    return result
