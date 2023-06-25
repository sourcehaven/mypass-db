class GetSetDescriptor:
    def __init__(self, attr):
        self.attr = attr

    def __get__(self, obj, obj_cls):
        return getattr(obj, self.attr)

    def __set__(self, obj, __v):
        setattr(obj, self.attr, __v)


class GetDescriptor:
    def __init__(self, attr):
        self.attr = attr

    def __get__(self, obj, obj_cls):
        return getattr(obj, self.attr)


class SetDescriptor:
    def __init__(self, attr):
        self.attr = attr

    def __set__(self, obj, __v):
        setattr(obj, self.attr, __v)
