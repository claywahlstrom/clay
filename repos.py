
"""
Custom repositories

"""

import datetime as _dt
import json as _json
import os as _os

from clay.lists import extend as _extend
from clay.models import Model as _Model, Serializable as _Serializable

class JsonRepository(object):
    """Wrapper for working with JSON database files"""

    def __init__(self, name, empty):
        """Intializes this JSON repository with the given name
           and empty database structure"""
        self.__name = name
        self.__empty = empty
        self.__has_read = False
        self.clear()

    def _ensure_connected(self):
        if not self.__has_read:
            raise RuntimeError('database has not been read')

    def clear(self):
        """Sets this database to the empty structure"""
        self.__db = self.__empty

    def create(self, force=False, write=True):
        """Creates this database if it does not exist and returns
           a boolean of whether it was successful or not. Use force=True
           if this database exists to clear its contents."""
        if _os.path.exists(self.__name) and not force:
            # could not create the database because it already exists
            return False

        self.clear()
        if write:
            self.write()
        return True

    def exists(self):
        """Returns True if this database exists, False otherwise"""
        return _os.path.exists(self.__name)

    def get_name(self):
        """Returns the name of this database"""
        return self.__name

    def get_empty(self):
        """Returns the empty structure for this database"""
        return self.__empty

    @property
    def db(self):
        """Returns this database"""
        return self.__db

    @db.setter
    def db(self, value):
        """Sets this database to the given value"""
        if type(value) not in (dict, list):
            raise TypeError('db must be a JSON serializable of type dict or list')
        self.__db = value

    @property
    def has_read(self):
        """Returns True if read has been called for this database,
           False otherwise"""
        return self.__has_read

    def prune(self, predicate):
        """Prunes entities from the database based on the given predicate
           function"""
        modified = False
        temp = self.__db.copy() # prevents concurrent modification errors
        for entity in self.__db:
            if predicate(entity):
                print('{}: pruning "{}"...'.format(self.__name, entity))
                if isinstance(temp, dict):
                    temp.pop(entity)
                else: # isinstance(temp, list)
                    temp.remove(entity)
                modified = True
        self.__db = temp
        if modified:
            self.write()

    def read(self):
        """Reads data from the disk into the database.
        Creates the database if it doesn't already exist.
        """
        if self.exists():
            with open(self.get_name()) as fp:
                self.__db = _json.load(fp)
        else:
            self.create()

        self.__has_read = True

    def write(self):
        """Writes this database to the disk"""
        with open(self.__name, 'w') as fd:
            _json.dump(self.__db, fd)

    name = property(get_name)
    empty = property(get_empty)

class CrudRepository(JsonRepository):

    def __init__(self, name):
        """Initializes this CRUD repository under the given file name"""
        super().__init__(name, [])
        self.__default_model = _Model()
        self.__index = self.build_index()

    def build_index(self):
        """Builds the index for this CrudRepository to speed up access times"""

        index = {}

        for model in self.db:
            if model.id is not None:
                if model.id in self.__index:
                    print('Warning: Model with ID {} already exists in index'
                        .format(model.id))
                    continue

                index[model.id] = model

        return index

    def __pk_not_found(self, pk):
        """Prints a generic message for an unknown primary key"""
        print('{}: pk "{}" not found'.format(self.name, pk))

    def _ensure_exists(self, pk):
        if isinstance(self.db, list) and self.get(pk) is None:
            model = self.default_model.to_json()
            # set the ID of the model
            model['id'] = pk
            # make sure the model exists
            self._insert_model(model)

    def get(self, pk):
        """Gets the model with the given primary key"""
        if pk in self.__index:
            return self.__index[pk]

        model = _extend(self.db) \
            .where(lambda a: a['id'] == pk) \
            .first_or_default()

        return model

    def create_if_not_exists(self, pk):
        self._ensure_connected()
        self._ensure_exists(pk)

    @property
    def default_model(self):
        """Returns the default model for this repository"""
        return self.__default_model

    @default_model.setter
    def default_model(self, model):
        """Sets the default model for this repository"""
        if not isinstance(model, _Serializable):
            raise TypeError('model must be of base type Serializable')
        self.__default_model = model

    def _insert_model(self, model):
        """Inserts this model into the repository and the index"""
        # insert the model
        self.db.append(model)
        # insert the model into the index
        self.__index[model['id']] = model

    def _remove_model(self, model):
        """Removes this model from the repository and the index"""
        # remove the model
        self.db.remove(model)
        # remove the model from the index
        del self.__index[model['id']]

    def insert(self, model):
        """Inserts the given model into this repository"""
        self._ensure_connected()

        pk = model['id']

        # if the model already exists, raise an exception
        if self.get(pk) is not None:
            raise RuntimeError('A model with primary key "{}" already exists'.format(pk))

        # append the model
        self._insert_model(model)

    def delete(self, pk):
        """Deletes the given primary key from this repository"""
        self._ensure_connected()

        model = self.get(pk)

        if model is not None:
            self._remove_model(model)
            self.write()
            print('{}: pk "{}" deleted'.format(self.name, pk))
        else:
            self.__pk_not_found(pk)

    def update(self, pk, model):
        """Updates the model with the given primary key"""

        self._ensure_connected()
        self._ensure_exists(pk)

        original = self.get(pk)

        if original is None:
            self.__pk_not_found(pk)
            return

        for attr in model.props:
            original[attr] = getattr(model, attr)

        print('{}: pk "{}" updated'.format(self.name, pk))

    def update_prop(self, pk, prop, value):
        """Updates the value of the property for the given primary
           key within this repository"""
        self._ensure_connected()
        self._ensure_exists(pk)

        model = self.get(pk)

        if model is None:
            self.__pk_not_found(pk)
            return

        model[prop] = value

    def write(self):
        super(CrudRepository, self).write()
        print('{}: database written'.format(self.name))

class UserRepository(CrudRepository):

    def __init__(self, file='users.json'):
        super(UserRepository, self).__init__(file)

    def prune(self, date_prop, date_format, days=30):
        """Prunes users based on the database date if the date is days old"""
        modified = False
        for model in self.db:
            pk = model['id']
            days_ago = _dt.datetime.now() - _dt.timedelta(days=30)
            if _dt.datetime.strptime(model[date_prop], date_format) <= days_ago:
                modified = True
                print('{}: pruning {}...'.format(self.name, pk))
                self._remove_model(model)

        if modified:
            self.write()

class UserWhitelist(object):

    def __init__(self, file):
        """Initializes this user whitelist"""
        self.__file = file
        self.__users = []

    def get_file(self):
        """Returns the file for this whitelist"""
        return self.__file

    def get_users(self):
        """Returns the users in this whitelist"""
        return self.__users

    def is_authorized(self, user):
        """Returns True if the given user is authorized
           by this whitelist, False otherwise"""
        return user in self.__users

    def read(self):
        """Reads data from the disk into the database"""
        users = []
        for line in self.__file:
            if not(line.startswith('#')):
                users.append(line.strip())
        self.__users = users

    file = property(get_file)
    users = property(get_users)

if __name__ == '__main__':

    from clay.tests import testif
    from clay.utils import qualify

    test_repo_name = r'test_files\test-repo.json'
    test_repo = CrudRepository(test_repo_name)
    test_repo.read()

    js1 = JsonRepository('README.md', {})
    js2 = JsonRepository('README.mda', [])

    testif('initializes new json repo with correct empty structure', js1.empty, {})
    testif('fails to overwrite when already exists and not forced', js1.create(force=False, write=False), False)
    testif('creates new json repo when already exists and forced', js1.create(force=True, write=False), True)
    testif('creates new json repo if not exists and not forced', js2.create(write=False), True)
    testif('creates new json repo if not exists and forced', js2.create(force=True, write=False), True)

    def crud_repository_insert_duplicate_model_test():
        test_repo.read()
        test_repo.db = [{'id': 0, 'name': 'docs'}]
        test_repo.insert({'id': 0, 'name': 'readme'})

    testif('Raises RuntimeError for duplicate model IDs',
        crud_repository_insert_duplicate_model_test,
        None,
        raises=RuntimeError,
        name=qualify(CrudRepository.insert))

    def crud_repository_insert_test():
        test_repo.read()
        test_repo.db.append({'id': 0, 'name': 'docs'})

    crud_repository_insert_test()
    testif('Inserts model correctly',
        test_repo.db,
        [{'id': 0, 'name': 'docs'}],
        name=qualify(CrudRepository.insert))

    def crud_repository_default_model_setter_test():
        test_repo.default_model = {}

    testif('CrudRepository.default_model setter raises TypeError for invalid base type',
        crud_repository_default_model_setter_test,
        None,
        raises=TypeError)

    whitelist = UserWhitelist(['abe', 'bob', 'caty', '# becky'])
    whitelist.read()

    testif('whitelist reads correct users', whitelist.users, ['abe', 'bob', 'caty'])
    testif('whitelist authorizes caty', whitelist.is_authorized('caty'), True)
    testif('whitelist rejects becky', whitelist.is_authorized('becky'), False)
