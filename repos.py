
"""
Custom repositories

"""

import datetime as _dt
import json as _json
import os as _os

from clay.linq import extend as _extend, \
    query as _query
from clay.lists import rmdup as _rmdup
from clay.models import Model as _Model, \
    json2model as _json2model, \
    Abstract as _Abstract

class RecordNotFoundError(Exception):
    """Error type for when a record is not found"""
    pass

class IRepository(_Abstract):

    def read(self):
        raise NotImplementedError('read')

    def write(self):
        raise NotImplementedError('write')

class BaseRepository(_Abstract):
    """Base repository for working with databases"""

    def __init__(self, name, empty):
        """
        Intializes this repository with the given name
        and empty database structure

        """
        self.raise_if_base(BaseRepository)
        self.__name = name
        self.__empty = empty
        self.__has_read = False
        self.clear()
        self._update_context()

    def _ensure_connected(self):
        """Ensures the database has been read from the disk"""
        if not self.has_read:
            _ = self.read()

    def _update_context(self):
        """Updates the context to be the current database snapshot"""
        self.__context = self._db.copy()

    def clear(self):
        """Sets the database to the empty structure"""
        self._db = self.__empty
        self._update_context()

    def create(self, force=False, write=True):
        """
        Creates this database if it does not exist and returns
        a boolean of whether it was successful or not. Use force=True
        if this database exists to clear its contents.

        """
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
        """
        Reads data from the disk into the database.
        Creates the database if it doesn't already exist.

        """
        if self.exists():
            with open(self.name) as fp:
                self._db = _json.load(fp)
            self._update_context()
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
        """
        Returns True if read has been called for this database,
        False otherwise

        """
        return self.__has_read

    @property
    def has_context_changed(self):
        """
        Returns True if the database context has changed since last
        read/write, False otherwise

        """
        return self.__context != self._db

class JsonRepository(BaseRepository, IRepository):
    """Wrapper for working with JSON databases"""

    def prune(self, predicate):
        """
        Prunes entities from the database based on the given predicate
        function

        """
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
        self._update_context()

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

class ListRepository(JsonRepository):
    """Wrapper for working with list databases"""

    def __init__(self, name):
        """Initializes this list repository"""
        super().__init__(name, [])

    def uniquify(self):
        """Removes duplicates from the database"""
        self.db = _rmdup(self.db) # remove duplicates

class CrudRepository(ListRepository):
    """Wrapper for working with CRUD databases"""

    def __init__(self, name):
        """Initializes this CRUD repository under the given file name"""
        super().__init__(name)
        self.__model = object
        self.clear_index()

    def clear(self):
        """Sets the database to the empty structure and clears the index"""
        self._db = _extend(self.empty)
        self.clear_index()

    def build_index(self):
        """Builds the index for this CrudRepository to speed up access times"""
        for model in self._db:
            model_id = model['id']
            if model_id is not None and model_id not in self.__index:
                self.__index[model_id] = model

    def clear_index(self):
        """Clears the index for this CrudRepository"""
        self.__index = {}

    def __pk_not_found(self, pk):
        """Raises a RecordNotFoundError for a primary key"""
        raise RecordNotFoundError('{}: pk "{}" not found'.format(self.name, pk))

    def _ensure_exists(self, pk):
        """Ensures the given primary key exists"""
        if isinstance(self.read(), list) and self.get(pk) is None:
            model = self.model()
            if not self.is_model_based:
                model = model.to_json()

            # set the ID of the model
            model['id'] = pk
            # make sure the model exists
            self.insert(model)

    def get(self, pk):
        """Gets the model with the given primary key"""
        self._ensure_connected()

        if pk in self.__index:
            return self.__index[pk]

        model = self.read() \
            .where(lambda a: a['id'] == pk) \
            .first_or_default()

        if model:
            self.__index[pk] = model

        return model

    def create_if_not_exists(self, pk):
        """Creates the given primary key if it does not exist"""
        self._ensure_exists(pk)

    def _insert_model(self, model):
        """Inserts this model into the repository and the index"""
        # insert the model
        self._db.append(model)
        # insert the model into the index
        self.__index[model['id']] = model

    def _remove_model(self, model):
        """Removes this model from the repository and the index"""
        # remove the model
        try:
            # try ordinary list removal
            self._db.remove(model)
        except ValueError:
            # remove the model based on ID as object equality did not work
            for i, j in enumerate(self._db):
                if j['id'] == model['id']:
                    del self._db[i]
                    break

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

    def insert_range(self, models):
        """Inserts the given models into this repository"""
        for model in models:
            self.insert(model)

    def delete(self, pk):
        """Deletes the given primary key from this repository"""
        self._ensure_connected()

        model = self.get(pk)

        if model is not None:
            self._remove_model(model)
            print('{}: pk "{}" deleted'.format(self.name, pk))
        else:
            self.__pk_not_found(pk)

    def update(self, model):
        """Updates the model by inferring the primary key"""

        # infer pk from model
        pk = model['id']

        self._ensure_exists(pk)

        original = self.get(pk)

        if original is None:
            self.__pk_not_found(pk)
            return

        props = model.props if model.is_model_based else model.keys()

        for attr in [prop for prop in props if prop != 'id']:
            original[attr] = getattr(model, attr)

        print('{}: pk "{}" updated'.format(self.name, pk))

    def update_prop(self, pk, prop, value):
        """
        Updates the value of the property for the given primary
        key within this repository

        """
        self._ensure_exists(pk)

        model = self.get(pk)

        if model is None:
            self.__pk_not_found(pk)
            return

        model[prop] = value

    def read(self, fetch_if_read=False):
        """
        Reads data from the disk into the database.
        Creates the database if it doesn't already exist.

        """
        if not self.has_read or fetch_if_read:
            super().read()

            # convert the database to an enumerable
            self._db = _extend(self._db)

            if self.is_model_based:
                self._db = self._db.select(lambda x: _json2model(x, self.model))

            self.build_index()
            self._update_context()

        return self._db

    def read_queryable(self, fetch_if_read=False):
        """
        Reads data from the disk into the database.
        Creates the database if it doesn't already exist.

        """
        return _query(self.read(fetch_if_read=fetch_if_read))

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

        self._update_context()

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

class CrudRepositoryMigrator:

    """Used to migrate CRUD repositories"""

    def __init__(self, name):
        """Initializes this CRUD repository migrator"""
        self.repo = CrudRepository(name)

    def add_column(self, name, default_value=None):
        """Adds a column with the given name and default value"""
        for entity in self.repo.read():
            if name in entity:
                raise RuntimeWarning('column "{}" already exists'.format(name))
            entity[name] = default_value

    def drop_column(self, name):
        """Drops a column with the given name"""
        if self.repo.read().any(lambda entity: entity.get(name) is not None):
            print('Data from column {} will be lost.'.format(name))
            sure = input('Are you sure (y/n)? ').lower() == 'y'
            if not sure:
                return print('Aborting...')

        for entity in self.repo.read():
            if name in entity:
                del entity[name]

    def commit(self):
        """Commits pending CRUD repository changes"""
        self.repo.write()

class UserRepository(CrudRepository):

    """Used to manage a repository of users"""

    def __init__(self, file='users.json'):
        """Initializes this user repository"""
        super().__init__(file)

    def prune(self, date_prop, date_format, days=30):
        """Prunes users based on the database date if the date is days old"""
        modified = False
        for model in self.read():
            pk = model['id']
            days_ago = _dt.datetime.now() - _dt.timedelta(days=days)
            if _dt.datetime.strptime(model[date_prop], date_format) <= days_ago:
                modified = True
                print('{}: pruning {}...'.format(self.name, pk))
                self._remove_model(model)

        if modified:
            self.write()

class UserWhitelist(object):

    """Used to whilelist users for secret access"""

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
        """
        Returns True if the given user is authorized
        by this whitelist, False otherwise

        """
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

    from clay.tests import testif, testraises
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

    testraises('base repository is initialized directly',
        lambda: BaseRepository('name', []),
        NotImplementedError,
        name=qualify(BaseRepository.__init__))

    def crud_repository_insert_duplicate_model_test():
        test_repo.read()
        test_repo._db = _extend([{'id': 0, 'name': 'docs'}])
        test_repo.insert({'id': 0, 'name': 'readme'})

    testif('Raises RuntimeError for duplicate model IDs',
        crud_repository_insert_duplicate_model_test,
        None,
        raises=RuntimeError,
        name=qualify(CrudRepository.insert))

    def crud_repository_insert_test():
        test_repo.read()
        test_repo.clear()
        test_repo.insert({'id': 0, 'name': 'docs'})

    crud_repository_insert_test()
    testif('Inserts model correctly',
        test_repo.read(),
        [{'id': 0, 'name': 'docs'}],
        name=qualify(CrudRepository.insert))

    def crud_repository_delete_raises_test():
        test_repo.read()
        test_repo.clear()
        test_repo.delete('non-existent-id')

    testraises('record not found',
        lambda: crud_repository_delete_raises_test(),
        RecordNotFoundError,
        name=qualify(CrudRepository.delete))

    def crud_repository_set_model_test():
        test_repo.set_model({})

    testif('Raises TypeError for invalid base type',
        crud_repository_set_model_test,
        None,
        raises=TypeError,
        name=qualify(CrudRepository.set_model))

    whitelist = UserWhitelist(['abe', 'bob', 'caty', '# becky'])
    whitelist.read()

    testif('whitelist reads correct users', whitelist.users, ['abe', 'bob', 'caty'])
    testif('whitelist authorizes caty', whitelist.is_authorized('caty'), True)
    testif('whitelist rejects becky', whitelist.is_authorized('becky'), False)
