from typing import Literal, Callable, Any


def create_query_all(query_like: dict):
    """Missing keys will cause filter to return false."""
    return lambda q: all([q[k] == v if k in q else False for k, v in query_like.items()])


def create_query_any(query_like: dict):
    """Missing keys will evaluate to false."""
    return lambda q: any([q[k] == v if k in q else False for k, v in query_like.items()])


def create_query(query_like: dict, logic: Literal['and', 'or']) -> Callable[[Any], bool]:
    """Missing keys will evaluate to false."""
    if logic == 'and':
        return create_query_all(query_like)
    return create_query_any(query_like)
