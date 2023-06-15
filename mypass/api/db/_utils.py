from typing import Callable, Any


def _is_special(key: str):
    return key.startswith('_')


def clear_special_keys(mapping: dict[str, Any], is_spec: Callable[[str], bool] = None):
    if is_spec is None:
        is_spec = _is_special
    return {k: v for k, v in mapping.items() if not is_spec(k)}
