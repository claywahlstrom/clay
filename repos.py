
"""
Custom repositories

"""

import datetime as _dt
import json as _json
import os as _os

class JsonRepository(object):

    LIST = []
    DICT = {}

    def __init__(self, name, empty):
        """Intializes this JSON repository with the given name
           and empty database structure"""
        self._name = name
        self._empty = empty
        self._has_read = False
        self.clear()

    def _ensure_connected(self):
        if not(self._has_read):
            raise RuntimeError('database has not been read')

    def clear(self):
        """Clears this database"""
        self._db = self._empty

    def create(self, force=False, write=True):
        """Creates this database if it does not exist and returns
           a boolean of whether the creation was success or not.
           Use force=True if this database exists to clear
           its contents."""
        if force or not(_os.path.exists(self._name)):
            self.clear()
            if write:
                self.write()
            return True
        else:
            print('Cannot overwrite database "' + self._name + '" because it already exists')
            return False

    def exists(self):
        """Returns True if this database exists, False otherwise"""
        return _os.path.exists(self._name)

    def get_name(self):
        """Returns the name of this database"""
        return self._name
        
    def get_empty(self):
        """Returns the empty structure for this database"""
        return self._empty

    @property
    def db(self):
        """Returns this database"""
        return self._db

    @db.setter
    def db(self, value):
        """Sets this database to the given value"""
        if not(type(value) in (dict, list)):
            raise ValueError('db must be a JSON serializable of type dict or list')
        self._db = value

    @property
    def has_read(self):
        """Returns True if read has been called for this database,
           False otherwise"""
        return self._has_read

    def prune(self, predicate):
        """Prunes entities from the database based on the given predicate
           function"""
        modified = False
        temp = self._db.copy() # prevents concurrent modification errors
        for entity in self._db:
            if predicate(entity):
                print('pruning {} from db "{}"...'.format(entity, self._name))
                if type(temp) == dict:
                    temp.pop(entity)
                else: # type(temp) == list
                    temp.remove(entity)
                modified = True
        self._db = temp
        if modified:
            self.write()

    def read(self):
        """Reads data from the disk into the database"""
        with open(self._name) as fp:
            self._db = _json.load(fp)
        self._has_read = True

    def write(self):
        """Writes this database to the disk"""
        with open(self._name, 'w') as fd:
            _json.dump(self._db, fd)

    name = property(get_name)
    empty = property(get_empty)

class CrudRepository(JsonRepository):

    def __init__(self, name, pk):
        """Initializes this CRUD repository under the given file
           using the given primary key"""
        super(CrudRepository, self).__init__(name, {})
        self._pk = pk
        self._default_model = {}

    def _ensure_exists(self, pk):
        if not(self.db is None or pk in self.db):
            self.db[pk] = self.default_model.to_dict()

    def create_if_not_exists(self, pk):
        self._ensure_connected()
        self._ensure_exists(pk)

    @property
    def default_model(self):
        """Returns the default model for this repository"""
        return self._default_model
        
    @default_model.setter
    def default_model(self, model):
        """Sets the default model for this repository"""
        self._default_model = model

    def delete(self, pk):
        """Deletes the given primary key from this repository"""
        self._ensure_connected()
        if pk in self.db:
            self.db.pop(pk)
            self.write()
            print('user entry for pk', pk, 'removed')
        else:
            print('user pk not found')

    def update(self, pk, model):
        """Updates the given primary key within this repository"""
        self._ensure_connected()
        self._ensure_exists(pk)

        for attr in model.get_attributes():
            self.db[pk][attr] = getattr(model, attr)

        print('pk', pk, 'updated')

    def update_prop(self, pk, prop, value):
        """Updates the value of the property for the given primary
           key within this repository"""
        self._ensure_connected()
        self._ensure_exists(pk)
        self.db[pk][prop] = value

    def write(self):
        self._ensure_connected()
        super(CrudRepository, self).write()
        print('database "{}" written'.format(self.name))

class UserRepository(CrudRepository):

    def __init__(self, primary_key, file='users'):
        super(UserRepository, self).__init__(file, primary_key)

    def prune(self, date_prop, date_format, days=30):
        """Prunes users based on the database date if the date is days old"""
        modified = False
        temp = self.db.copy() # prevents concurrent modification errors
        for pk in self.db:
            days_ago = _dt.datetime.now() - _dt.timedelta(days=30)
            if _dt.datetime.strptime(temp[pk][date_prop], date_format) <= days_ago:
                modified = True
                print('pruning {}...'.format(pk))
                temp.pop(pk)
        self.db = temp
        if modified:
            self.write()

class UserWhitelist(object):

    def __init__(self, file):
        """Initializes this user whitelist"""
        self._file = file
        self._users = []

    def get_file(self):
        """Returns the file for this whitelist"""
        return self._file

    def get_users(self):
        """Returns the users in this whitelist"""
        return self._users

    def is_authorized(self, user):
        """Returns True if the given user is authorized
           by this whitelist, False otherwise"""
        return user in self._users

    def read(self):
        """Reads data from the disk into the database"""
        users = []
        for line in self._file:
            if not(line.startswith('#')):
                users.append(line.strip())
        self._users = users

    file = property(get_file)
    users = property(get_users)

if __name__ == '__main__':

    from clay.tests import testif

    js1 = JsonRepository('README.md', JsonRepository.DICT)
    js2 = JsonRepository('README.mda', [])
    
    testif('initializes new json repo with correct empty structure', js1.empty, {})
    testif('fails to overwrite when already exists and not forced', js1.create(force=False, write=False), False)
    testif('creates new json repo when already exists and forced', js1.create(force=True, write=False), True)
    testif('creates new json repo if not exists and not forced', js2.create(write=False), True)
    testif('creates new json repo if not exists and forced', js2.create(force=True, write=False), True)

    whitelist = UserWhitelist(['abe', 'bob', 'caty', '# becky'])
    whitelist.read()

    testif('whitelist reads correct users', whitelist.users, ['abe', 'bob', 'caty'])
    testif('whitelist authorizes caty', whitelist.is_authorized('caty'), True)
    testif('whitelist rejects becky', whitelist.is_authorized('becky'), False)


