from typing import Mapping, overload


class ElasticClass(Mapping):
    """
    Base class for storing elastic data.

    All attributes and items are generated on the fly as needed,
    and non-existing ones are returned as None.

    The class cannot store None values.
    None values are handled by only returning them if needed, but they are not stored by the class itself.
    """

    def __init__(self, **kwargs):
        """
        Initializing a data class for storing elastic data.

        Parameters:
            kwargs: keyword arguments, where every key should be a string
        """
        self.__blacklist = {'_abc_impl', '_is_protocol'}
        for k in kwargs:
            if kwargs[k] is not None:
                setattr(self, k, kwargs[k])

    def __getitem__(self, __item):
        try:
            return getattr(self, __item)
        except AttributeError:
            raise KeyError(f'{__item} is not present inside {self.__class__.__name__}')

    def __setitem__(self, __key, __value):
        setattr(self, __key, __value)

    def __contains__(self, item):
        return hasattr(self, item)

    def _is_mangled(self, field_name):
        return any(field_name.startswith(f'_{base.__name__}__') for base in self.__class__.mro())

    def _get_parts(self):
        for name in vars(self):
            if not name.startswith('__') and not self._is_mangled(name) and name not in self.__blacklist:
                yield name

    def __len__(self):
        return len(tuple(self._get_parts()))

    def __iter__(self):
        return self._get_parts()

    def __str__(self):
        parts_repr = ', '.join([
            f'{pn}="{pv}"' if isinstance(pv, str) else f'{pn}={pv}'
            for pn, pv in self.items()])
        return f'{self.__class__.__name__}({parts_repr})'

    def __repr__(self):
        return str(self)

    def is_empty(self):
        return len(self) <= 0

    def __copy__(self):
        return type(self)(**self)

    def copy(self):
        return self.__copy__()

    @overload
    def pop(self, __item):
        ...

    @overload
    def pop(self, __item, __default):
        ...

    def pop(self, __item, __default=...):
        if __default is ... and not hasattr(self, __item):
            raise AttributeError(f'Object {self} has not attribute "{__item}".')
        if not hasattr(self, __item):
            return __default
        val = self[__item]
        delattr(self, __item)
        return val

    def update(self, other: Mapping):
        for k, v in other.items():
            setattr(self, k, v)

    def __or__(self, other: Mapping):
        result = type(self)(**self)
        result.update(other)
        return result
