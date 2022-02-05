
"""
Database helpers

"""

from clay.linq import extend
from clay.models import Abstract, Model
from clay.text import uncapitalize
from clay.utils import qualify
from clay_common.strings import consume_next

db_repos = extend([])

class RelationalModel(Model, Abstract):

    def __init__(self, *initial_data, **kwargs):
        self.raise_if_base(RelationalModel)
        super().__init__(*initial_data, **kwargs)

    def can_delete(self):
        child_name = self._child_name(self)
        navigation = child_name + 'Id'
        # check all tables to see if the ID is referenced
        # TODO: improve performance
        has_records = any(db_repos \
            .where(lambda repo:
                repo.read().where(lambda x: navigation in x and \
                    x[navigation] == self['id'])
            )
        )
        return not has_records

    def _child_name(self, model):
        model_name = qualify(model)
        if '.' in model_name:
            model_name = consume_next(model_name, '.')
        child_name = uncapitalize(model_name)
        return child_name

    def child_name(self, repo):
        return self._child_name(repo.model)

    def foreign_key(self, repo):

        child_name = self.child_name(repo)

        model = repo.read() \
            .where(lambda x: x['id'] == self[child_name + 'Id']) \
            .first_or_default()

        return model

    def inverse_prop(self, repo):

        child_name = uncapitalize(qualify(self))

        # try and read the entities
        return repo.read() \
            .where(lambda x: x[child_name + 'Id'] == self['id'])
