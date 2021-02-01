
"""
di: Dependency injection tools

"""

from clay.guids import Guid
from clay.utils import qualify

class TypeUnboundError(Exception):

    """Raised when a type is not bound"""

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super().__init__(repr(self), *args, **kwargs)

    def __repr__(self):
        """Returns the string representation"""
        return self.name + ' not bound'

class _Kernel:

    """Used to set up the bindings and track resolutions"""

    def __init__(self):
        """Initializes this kernel"""
        self.__id = str(Guid.new())
        self._bindings = {}
        self._resolutions = {}

    def bind(self, type, expr):
        """Binds the given type to the expression"""
        self._bindings[qualify(type)] = expr

    def get(self, type):
        """
        Resolves and returns the evaluated expression for the given type.
        Raises `TypeUnboundError` if the type is not bound.

        """
        name = qualify(type)
        if name not in self._resolutions:
            if name not in self._bindings:
                raise TypeUnboundError(name)
            self._resolutions[name] = self._bindings[name]()
        return self._resolutions[name]

    @property
    def id(self):
        """The ID of this kernel"""
        return self.__id

kernel = _Kernel()

if __name__ == '__main__':

    from clay.tests import testif, testraises

    class TestService:
        def __init__(self, repo_name):
            self.repo_name = repo_name

    testraises('type not bound',
        lambda: kernel.get(TestService),
        TypeUnboundError,
        name=qualify(_Kernel.get))

    test_service = TestService('test_repo.json')
    kernel.bind(TestService, lambda: test_service)

    testif('returns bound service',
        kernel.get(TestService),
        test_service,
        name=qualify(_Kernel.get))
