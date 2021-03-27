
"""
Models for working with objects.

"""

import abc as _abc
import collections as _collections
import inspect as _inspect
import uuid as _uuid

from clay.time.dates import YMD_FMT

class Abstract:

    """Used to disable instantiation of this type"""

    @_abc.abstractmethod
    def __init__(self):
        """Initializes this object"""
        if isinstance(self, Abstract):
            raise NotImplementedError('Cannot instantiate {} because it is abstract'.format(type(self)))

    def raise_if_base(self, base):
        """Raises NotImplementedError if the type of this object matches the base type"""
        if type(self) == base:
            raise NotImplementedError('Cannot instantiate {} because it is abstract'.format(type(self)))

Interface = Abstract # alias
Static = Abstract # alias

class Serializable(Abstract):

    """Abstract class used to convert between Python and JSON types"""

    def __init__(self):
        """Always throws NotImplementedError because this class is abstract"""
        self.raise_if_base(Serializable)

    def __repr__(self):
        """Returns the string representation of this object"""
        self.verify_props()

        return r'{}({})'.format(
            self.__class__.__name__,
            ', '.join(prop + '=' + repr(getattr(self, prop, None))
                for prop in sorted(self.props)))

    def verify_props(self):
        """Verifies properties exist. Raises a runtime error if not found"""
        if not hasattr(self, 'props'):
            raise RuntimeError('{} must implement the props attribute'.format(self.__class__.__name__))

    def to_json(self):
        """Serializes this object to JSON"""
        self.verify_props()
        return {prop: getattr(self, prop, None) for prop in self.props}

class Anonymous(Serializable):

    """Used to initialize attributes using dictionaries and keyword arguments"""

    def __init__(self, *initial_data, **kwargs):
        """Initializes this Anonymous"""
        self._props = _collections.OrderedDict()
        self.update(*initial_data, **kwargs)

    def __contains__(self, key):
        """Returns True if key is a property of this Anonymous, False otherwise"""
        return key in self.props

    def __getitem__(self, name):
        """Gets the attribute with the given name"""
        return getattr(self, name)

    def __setitem__(self, name, value):
        """Sets the attribute with the given name to value"""
        setattr(self, name, value)

    def __setattr__(self, name, value):
        """Sets the attribute with the given name to value"""
        super().__setattr__(name, value)

        # track only public properties
        if not name.startswith('_'):
            self._props[name] = type(value)

    def __eq__(self, other):
        """Returns True if this Anonymous is equal to other, False otherwise"""
        assert self.props == other.props
        for prop in self.props:
            if self[prop] != other[prop]:
                return False
        return True

    @property
    def props(self):
        """Returns the attributes for this Anonymous"""
        return self._props.copy()

    def get(self, name, default=None):
        """Gets the attribute with the given name. Defaults to None"""
        try:
            return getattr(self, name)
        except AttributeError as ae:
            return default
        except:
            raise

    def update(self, *initial_data, **kwargs):
        """Updates attributes using dictionaries and keyword arguments"""
        for param in initial_data:
            if not isinstance(param, dict):
                raise TypeError('initial_data must be of type dict')
            # set props using dictionaries
            self.__convert_data(param)
        # set props using kwargs
        self.__convert_data(kwargs)

    def __convert_data(self, lookup):
        """Assigns the lookup keys and values to this Anonymous"""
        import datetime as dt
        for key in lookup:
            value = lookup[key]
            if key in self.props and self.props.get(key) == dt.datetime:
                try:
                    # attempt to read as date value
                    value = dt.datetime.strptime(value, YMD_FMT)
                except:
                    pass
            self[key] = value

def json2model(data, model):
    """Deserializes the given data to an object of type model"""

    obj = model()

    if not isinstance(obj, Serializable):
        raise TypeError('model must be of base type Serializable')

    obj.verify_props()
    for key, value in data.items():
        if key not in obj.props:
            print('Warning: Property {} may not serialize because '.format(key) +
                'it is not listed in props')
        setattr(obj, key, value)
    return obj

class Model(Anonymous):

    """Used to work with database models"""

    def __init__(self, *initial_data, **kwargs):
        """Initializes this Model"""

        # set an initial ID value
        self.__id = None

        super().__init__(*initial_data, **kwargs)

        # if the ID is not set, use a GUID by default
        if self.id is None:
            self.id = str(_uuid.uuid4())

    def __repr__(self):
        """Returns the string representation of this model"""
        self.verify_props()

        return r'{}({})'.format(
            self.__class__.__name__,
            ', '.join(prop + '=' + repr(getattr(self, prop, None))
                for prop in sorted(self.props, key=lambda x: (x != 'id', x))))

    @property
    def id(self) -> str:
        """Gets the ID of this Model"""
        return self.__id

    @id.setter
    def id(self, value: str) -> str:
        """Sets the ID of this Model"""
        if not isinstance(value, str):
            raise TypeError('value must be of type str')

        self.__id = value

if __name__ == '__main__':

    from clay.tests import testif, testraises
    from clay.utils import qualify

    class BaseClassWithoutInitializer(Abstract):
        pass

    class BaseClass(Abstract):
        def __init__(self):
            self.raise_if_base(BaseClass)

    class Implementation(BaseClass):
        def __init__(self):
            super().__init__()

    testraises('class is abstract',
        lambda: Abstract(),
        NotImplementedError,
        name=qualify(Abstract.__init__))

    testraises('base class does not implement initializer',
        lambda: BaseClassWithoutInitializer(),
        NotImplementedError,
        name=qualify(BaseClassWithoutInitializer.__init__))

    testraises('instantiating abstract class',
        lambda: BaseClass(),
        NotImplementedError,
        name=qualify(BaseClass.__init__))

    testif('instantiates with no errors',
        type(Implementation()) is Implementation,
        True,
        name=qualify(Implementation.__init__))

    class Serious(Serializable):
        def __init__(self):
            pass

    testif('Raises RuntimeError when props missing',
        lambda: Serious().verify_props(),
        None,
        raises=RuntimeError,
        name=qualify(Serializable.verify_props))

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
        "Serious(implicit=None, int=42, list=['Example', 'list'], string='Hello')")
    testif('Serializable.to_json returns correct converted object',
        Serious().to_json(),
        {'int': 42, 'string': 'Hello', 'list': ['Example', 'list'], 'implicit': None})
    testif('Raises TypeError for incorrect subtype',
        lambda: json2model({}, object),
        None,
        raises=TypeError,
        name=qualify(json2model))
    testif('Sets attributes correctly',
        json2model({'implicit': 0}, Serious).implicit,
        0,
        name=qualify(json2model))

    testif('Raises AttributeError for invalid argument types',
        lambda: Anonymous().update([1, 2, 3]),
        None,
        raises=TypeError,
        name=qualify(Anonymous.update))
    obj = Anonymous({
        'one': 1,
        'two': 2,
    }, three=3)
    testif('Contains "one"', 'one' in obj, True, name=qualify(Anonymous))
    testif('Contains "three"', 'three' in obj, True, name=qualify(Anonymous))
    testif('Contains "three"', 'four' in obj, False, name=qualify(Anonymous))
    testif('Anonymous sets attribute correctly (1)', obj.one, 1)
    testif('Anonymous sets attribute correctly (2)', obj.two, 2)
    testif('Anonymous sets attribute correctly (3)', obj.three, 3)
    testif('Anonymous has three attributes set', len(obj.props), 3)

    testif('returns value if exists',
        obj.get('one'),
        1,
        name=qualify(Anonymous.get))
    testif('returns default if not exists',
        obj.get('four'),
        None,
        name=qualify(Anonymous.get))
    testif('returns correct default if not exists',
        obj.get('four', -4),
        -4,
        name=qualify(Anonymous.get))

    def test_anonymous_get_fails_if_getattr_does():
        # allow monkey-patching
        global getattr

        # store a reference to the built-in
        builtin = getattr

        # set up the new getattr
        def getattr(self, name):
            raise ValueError

        # perform the test
        testraises('raises error when getattr raises',
            lambda: obj.get('one'),
            ValueError,
            name=qualify(Anonymous.get))

        # reset the built-in
        getattr = builtin

    test_anonymous_get_fails_if_getattr_does()

    obj.update({'two': obj.three}, three=obj.two) # swap the values of two and three
    testif('Anonymous updates attributes correctly',
        (obj.two, obj.three),
        (3, 2))
    testif('Anonymous has three attributes set', len(obj.props), 3)

    testif('Model.id uses UUID if no ID specified',
        type(_uuid.UUID(Model({}).id)),
        _uuid.UUID)
    testif('Model.id uses given ID if specified',
        Model({'id': '0000'}).id,
        '0000')
    testif('Model.id raises TypeError for invalid ID type',
        lambda: Model({'id': bytes()}),
        None,
        raises=TypeError)
    testif('Returns correct string representation with ID first',
        repr(Model({'nj': 'no-joke', 'jk': 'joke', 'id': '0000'})),
        "Model(id='0000', jk='joke', nj='no-joke')",
        qualify(Model.__repr__))
