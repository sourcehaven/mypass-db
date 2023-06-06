from typing import Literal


def create_query_all(query_like: dict):
    return lambda q: all([q[k] == v for k, v in query_like.items()])


def create_query_any(query_like: dict):
    return lambda q: any([q[k] == v for k, v in query_like.items()])


def create_query(query_like: dict, logic: Literal['and', 'or']):
    if logic == 'and':
        return create_query_all(query_like)
    else:
        return create_query_any(query_like)
