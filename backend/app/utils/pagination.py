from sqlalchemy import Select


def apply_pagination(statement: Select, limit: int, offset: int) -> Select:
    """
    Apply pagination to a SQLAlchemy statement.
    """
    return statement.limit(limit).offset(offset)

