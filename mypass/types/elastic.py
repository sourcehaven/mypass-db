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
        self._blacklist = {'_abc_impl', '_is_protocol'}
        for k in kwargs:
            if kwargs[k] is not None:
                setattr(self, k, kwargs[k])

    def __getitem__(self, __item):
        try:
            return getattr(self, __item)
        except AttributeError:
            return None

    def __setitem__(self, __key, __value):
        setattr(self, __key, __value)

    def __contains__(self, item):
        return hasattr(self, item)

    def _get_parts(self):
        for name in vars(self):
            if (not name.startswith('__') and (not name.startswith('_') and not name.endswith('_'))
                    and not name.startswith(f'_{self.__class__.__name__}__') and name not in self._blacklist):
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
        return ElasticClass(**self)

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
