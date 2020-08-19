
"""
Custom repositories

"""

import datetime as _dt
import json as _json
import os as _os

from clay.lists import extend as _extend
from clay.models import Model as _Model, \
    Serializable as _Serializable, \
    json2model as _json2model, \
    Abstract as _Abstract

class IRepository(_Abstract):

    def read(self):
        raise NotImplementedError('read')

    def write(self):
        raise NotImplementedError('write')

class BaseRepository(_Abstract):

    def __init__(self, name, empty):
        """Intializes this repository with the given name
           and empty database structure"""
        if type(self) is BaseRepository:
            super().__init__()
        self.__name = name
        self.__empty = empty
        self.__has_read = False
        self.clear()

    def _ensure_connected(self):
        if not self.has_read:
            raise RuntimeError('database has not been read')

    def clear(self):
        """Sets the database to the empty structure"""
        self._db = self.__empty

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
        """Returns True if the database exists, False otherwise"""
        return _os.path.exists(self.__name)

    def read(self):
        """Reads data from the disk into the database.
        Creates the database if it doesn't already exist.
        """
        if self.exists():
            with open(self.name) as fp:
                self._db = _json.load(fp)
        else:
            self.create()

        self.__has_read = True

    @property
    def name(self):
        """The name of this repository"""
        return self.__name

    @property
    def empty(self):
        """An empty structure for this repository"""
        return self.__empty

    @property
    def has_read(self):
        """Returns True if read has been called for this database,
           False otherwise"""
        return self.__has_read

class JsonRepository(BaseRepository, IRepository):
    """Wrapper for working with JSON databases"""

    def prune(self, predicate):
        """Prunes entities from the database based on the given predicate
           function"""
        modified = False
        temp = self.db.copy() # prevents concurrent modification errors
        for entity in self.db:
            if predicate(entity):
                print('{}: pruning "{}"...'.format(self.name, entity))
                if isinstance(temp, dict):
                    temp.pop(entity)
                else: # isinstance(temp, list)
                    temp.remove(entity)
                modified = True
        self._db = temp
        if modified:
            self.write()

    def write(self):
        """Writes this database to the disk"""
        with open(self.name, 'w') as fd:
            _json.dump(self.db, fd)

    @property
    def db(self):
        """Returns the database for this repository"""
        return self._db

    @db.setter
    def db(self, value):
        """Sets this database to the given value"""
        if not isinstance(value, (dict, list)):
            raise TypeError('db must be a JSON serializable of base type dict or list')
        self._db = value

class CrudRepository(BaseRepository, IRepository):
    """Wrapper for working with CRUD databases"""

    def __init__(self, name):
        """Initializes this CRUD repository under the given file name"""
        super().__init__(name, [])
        self.__default_model = _Model()
        self.__model = object
        self.__index = {}

    def build_index(self):
        """Builds the index for this CrudRepository to speed up access times"""
        for model in self._db:
            if model['id'] is not None and model['id'] not in self.__index:
                self.__index[model['id']] = model

    def __pk_not_found(self, pk):
        """Prints a generic message for an unknown primary key"""
        print('{}: pk "{}" not found'.format(self.name, pk))

    def _ensure_exists(self, pk):
        if isinstance(self.read(), list) and self.get(pk) is None:
            model = self.default_model.to_json()
            # set the ID of the model
            model['id'] = pk
            # make sure the model exists
            self._insert_model(model)

    def get(self, pk):
        """Gets the model with the given primary key"""
        if pk in self.__index:
            return self.__index[pk]

        model = self.read() \
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
        self._db.append(model)
        # insert the model into the index
        self.__index[model['id']] = model

    def _remove_model(self, model):
        """Removes this model from the repository and the index"""
        # remove the model
        self._db.remove(model)
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

        props = model.props if model.is_model_based else model.keys()

        for attr in props:
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

    def read(self, fetch_if_read=False):
        """Reads data from the disk into the database.
        Creates the database if it doesn't already exist.
        """
        if not self.has_read or fetch_if_read:
            super().read()

            # convert the database to an enumerable
            self._db = _extend(self._db)

            if self.is_model_based:
                self._db = self._db.select(lambda x: _json2model(x, self.model))

            self.build_index()

        return self._db

    def write(self, name=None):
        """Writes this database to the disk"""
        # create a copy of the repo
        models = self._db.copy()

        # check if this repo is model-based
        # only convert if this database is not being created
        if self.has_read and self.is_model_based:
            # serialize the models

            models = models.select(lambda x: x.to_json())

        filename = name or self.name

        with open(filename, 'w') as fd:
            _json.dump(models, fd)

        print('{}: database written'.format(filename))

    def set_model(self, model: _Model):
        """Sets the model type for this repository"""
        if not issubclass(model, _Model):
            raise TypeError('model must of base type clay.models.Model')
        self.__model = model

    @property
    def model(self) -> type:
        """Returns the model type for this repository"""
        return self.__model

    @property
    def is_model_based(self):
        """Returns True if this repository is model-based, False otherwise"""
        return self.model != object

class UserRepository(CrudRepository):

    def __init__(self, file='users.json'):
        super(UserRepository, self).__init__(file)

    def prune(self, date_prop, date_format, days=30):
        """Prunes users based on the database date if the date is days old"""
        modified = False
        for model in self.read():
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
