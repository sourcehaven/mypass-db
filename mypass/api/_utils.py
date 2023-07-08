from typing import Callable, Any, Iterable


def _is_special(key: str):
    return key.startswith('_')


def clear_special_keys(mapping: dict[str, Any], is_spec: Callable[[str], bool] = None, whitelist: Iterable[str] = None):
    if whitelist is None:
        whitelist = set()
    if is_spec is None:
        is_spec = _is_special
    return {k: v for k, v in mapping.items() if k in whitelist or not is_spec(k)}
