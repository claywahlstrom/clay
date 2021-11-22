
"""
Guids: extension methods for uuid.UUID

"""

import uuid as _uuid

class Guid(_uuid.UUID):

    FMT_LENS = (8, 4, 4, 4, 12)

    # stores newly generated instances
    _generated = set()

    def __repr__(self) -> str:
        """Returns the string representation of this Guid"""
        return '{{{}}}'.format(self)

    @staticmethod
    def new() -> 'Guid':
        """Returns a new Guid instance"""
        new_guid = Guid(str(_uuid.uuid4()))
        # generate a new Guid while it is not unique
        while new_guid in Guid._generated:
            new_guid = Guid(str(_uuid.uuid4()))
        # add new Guid to generated set
        Guid._generated.add(new_guid)
        return new_guid

    @staticmethod
    def is_valid(guid: str) -> bool:
        """
        Returns True if the given string value is a valid guid,
        False otherwise

        """
        return Guid.is_valid_size(guid) and Guid.is_valid_type(guid)

    @staticmethod
    def is_valid_size(guid: str) -> bool:
        """
        Returns True if the given string value is a valid size guid,
        False otherwise

        """
        return guid and tuple(map(len, guid.split('-'))) == Guid.FMT_LENS

    @staticmethod
    def is_valid_type(guid: str) -> bool:
        """
        Returns True if the given string value is composed of hexadecimal digits,
        False otherwise

        """
        try:
            Guid(guid)
            return True
        except:
            return False

    @staticmethod
    def empty() -> 'Guid':
        """Returns an instance of Guid containing all zeros"""
        return Guid('00000000-0000-0000-0000-000000000000')

    @property
    def is_empty(self) -> bool:
        """Returns True if this Guid is empty (all zeros), False otherwise"""
        return self == Guid.empty()

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    invalid_sized_guid = '93234F-333J-FDD-D-DDDD'
    valid_guid = str(Guid.new())
    invalid_guid = 'X' + valid_guid[1:]

    testif('Returns correct string representation',
        repr(Guid.empty()),
        '{00000000-0000-0000-0000-000000000000}',
        name=qualify(Guid.__repr__))

    testif('Validates valid guid size',
        Guid.is_valid_size(str(Guid.empty())),
        True,
        name=qualify(Guid.is_valid_size))
    testif('Does not validate invalid guid size',
        Guid.is_valid_size(invalid_sized_guid),
        False,
        name=qualify(Guid.is_valid_size))

    testif('Validates valid guid size',
        Guid.is_valid_type(valid_guid),
        True,
        name=qualify(Guid.is_valid_type))
    testif('Does not validate invalid guid size',
        Guid.is_valid_type(invalid_guid),
        False,
        name=qualify(Guid.is_valid_type))

    testif('Validates valid guid',
        Guid.is_valid(str(Guid.empty())),
        True,
        name=qualify(Guid.is_valid))
    testif('Does not validate invalid guid',
        Guid.is_valid(invalid_sized_guid),
        False,
        name=qualify(Guid.is_valid))
    testif('Does not validate invalid guid',
        Guid.is_valid(invalid_guid),
        False,
        name=qualify(Guid.is_valid))

    testif('Returns True for empty guid',
        Guid.empty().is_empty,
        True,
        name='Guid.is_empty')
    testif('Returns False for non-empty guid',
        Guid.new().is_empty,
        False,
        name='Guid.is_empty')

    testif('Obeys the law of identity',
        Guid.empty(),
        Guid(str(Guid.empty())),
        name=qualify(Guid.__eq__))

    guids = [Guid.new() for _ in range(1000)]
    actual_len = len(guids)
    expected_len = len(set(guids))

    testif('Generates unique guids in bulk',
        actual_len,
        expected_len,
        name=qualify(Guid.new))
