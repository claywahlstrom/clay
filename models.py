
"""
Models for working with objects.

"""

import abc as _abc
import inspect as _inspect

class Abstract:

    """Used to disable instantiation of this type"""

    @_abc.abstractmethod
    def __init__(self):
        """Initializes this object"""
        if isinstance(self, Abstract):
            raise NotImplementedError('Cannot instantiate {} because it is abstract'.format(type(self)))

Static = Abstract # alias

class Serializable(Abstract):

    """Abstract class used to convert between Python and JSON types"""

    def __repr__(self):
        """Returns the string representation of this object"""
        self.verify_props()

        return r'{}({})'.format(
            self.__class__.__name__,
            ', '.join(prop + '=' + repr(getattr(self, prop, None)) for prop in self.props))

    def verify_props(self):
        """Verifies properties exist. Raises a runtime error if not found"""
        if not hasattr(self, 'props'):
            raise RuntimeError('{} must implement the props attribute'.format(self.__class__.__name__))

    def to_json(self):
        """Serializes this object to JSON"""
        self.verify_props()
        return {prop: getattr(self, prop, None) for prop in self.props}

    @staticmethod
    def from_json(cls, data):
        """Deserializes the given data to an object"""
        obj = cls()
        if not isinstance(obj, Serializable):
            raise TypeError('cls must be of base type Serializable')
        obj.verify_props()
        for key, value in data.items():
            if key not in obj.props:
                print('Warning: Property {} may not serialize because it is not listed in props'.format(key))
            setattr(obj, key, value)
        return obj

class Anonymous(Serializable):

    """Used to initialize attributes using dictionaries and keyword arguments"""

    def __init__(self, *initial_data, **kwargs):
        """Initializes this Anonymous"""
        self.update(*initial_data, **kwargs)

    @property
    def props(self):
        """Returns the attributes for this Anonymous dynamically"""
        attrs = _inspect.classify_class_attrs(Anonymous)
        # return the difference of the instance and class attributes
        return list(set(dir(self)).difference(set(a.name for a in attrs)))

    def update(self, *initial_data, **kwargs):
        """Updates attributes using dictionaries and keyword arguments"""
        for param in initial_data:
            for key in param.keys():
                setattr(self, key, param[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

Model = Anonymous # alias

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    testif('Raises NotImplementedError because it is abstract',
        lambda: Abstract(),
        None,
        raises=NotImplementedError,
        name=qualify(Abstract.__init__))

    testif('Raises NotImplementedError for subclass types without __init__ implementation',
        lambda: Serializable(),
        None,
        raises=NotImplementedError,
        name=qualify(Abstract.__init__))

    class Serious(Serializable):
        def __init__(self):
            pass

    testif('Serializable.verfiy_props raises RuntimeError when props missing',
        lambda: Serious().verify_props(),
        None,
        raises=RuntimeError)

    class Serious(Serializable):
        def __init__(self):
            pass

        props = ['int', 'string', 'list', 'implicit']

        @property
        def int(self):
            return 42

        @property
        def string(self):
            return 'Hello'

        @property
        def list(self):
            return ['Example', 'list']

    testif('Serializable.__repr__ returns correct string representation',
        repr(Serious()),
        "Serious(int=42, string='Hello', list=['Example', 'list'], implicit=None)")
    testif('Serializable.to_json returns correct converted object',
        Serious().to_json(),
        {'int': 42, 'string': 'Hello', 'list': ['Example', 'list'], 'implicit': None})
    testif('Serializable.from_json raises TypeError for incorrect subtype',
        lambda: Serializable.from_json(object, {}),
        None,
        raises=TypeError)
    testif('Serializable.from_json sets attributes correctly',
        Serializable.from_json(Serious, {'implicit': 0}).implicit,
        0)

    testif('Anonymous raises AttributeError for invalid argument types',
        lambda: Anonymous([1, 2, 3]),
        None,
        raises=AttributeError)
    obj = Anonymous({
        'one': 1,
        'two': 2,
    }, three=3)
    testif('Anonymous sets attribute correctly (1)', obj.one, 1)
    testif('Anonymous sets attribute correctly (2)', obj.two, 2)
    testif('Anonymous sets attribute correctly (3)', obj.three, 3)
    testif('Anonymous has three attributes set', len(obj.props), 3)
    obj.update({'two': obj.three}, three=obj.two) # swap the values of two and three
    testif('Anonymous updates attributes correctly',
        (obj.two, obj.three),
        (3, 2))
    testif('Anonymous has three attributes set', len(obj.props), 3)
