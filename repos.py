
"""
Custom repositories

"""

import json as _json
import os as _os

class CRUDRepository(object):

    def __init__(self, file, pk):
        """Initializes this CRUD repository under the given file
           using the given primary key"""
        self.file = file
        self.pk = pk
        self.db = None
        self.default_model = None
        self.__has_read = False

    def __ensure_connected(self):
        if not(self.__has_read):
            raise RuntimeError('database has not been read')

    def __ensure_exists(self, pk):
        if not(self.db is None or pk in self.db):
            self.db[pk] = self.get_default_model().to_dict()

    def create_if_not_exists(self, pk):
        self.__ensure_connected()
        self.__ensure_exists(pk)

    def get_default_model(self):
        return self.default_model

    def read(self):
        if not(_os.path.exists(self.file)):
            self.db = {} # dict
            self.write()
        with open(self.file) as fp:
            self.db = _json.load(fp)
        if self.db is not None:
            self.__has_read = True

    def delete(self, pk):
        self.__ensure_connected()
        if pk in self.db:
            self.db.pop(pk)
            self.write()
            print('user entry for pk', pk, 'removed')
        else:
            print('user pk not found')

    def set_default_model(self, model):
        self.default_model = model

    def update(self, pk, model):
        self.__ensure_connected()
        self.__ensure_exists(pk)

        for attr in model.get_attributes():
            self.db[pk][attr] = getattr(model, attr)

        print('pk', pk, 'updated')

        self.write()

    def update_prop(self, pk, prop, value):
        self.__ensure_connected()
        self.__ensure_exists(pk)
        self.db[pk][prop] = value

    def write(self):
        self.__ensure_connected()
        with open(self.file, 'w') as fp:
            _json.dump(self.db, fp)
        print('database written')

class UserRepository(CRUDRepository):
    def __init__(self, primary_key, file='users'):
        super(UserRepository, self).__init__(file, primary_key)

class UserWhitelist(object):
    
    def __init__(self, db_filename):
        if not(_os.path.exists(db_filename)):
            raise FileNotFoundError(db_filename)
        self.filename = db_filename
        self.users = self.read_users()

    def read_users(self):
        with open(self.filename) as fp:
            users = [user for user in fp.read().strip().split('\n') \
                         if not(user.startswith('#'))]
        return users

    def is_authorized(self, user):
        return user in self.users
