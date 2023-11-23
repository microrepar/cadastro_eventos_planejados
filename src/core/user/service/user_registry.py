from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase
from src.core.user import User

from .user_repository import UserRepository


@usecase_map('/user/registry')
class UserRegistry(UseCase):

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, entity: User) -> Result:
        result = Result()
        
        if not isinstance(entity, User):
            result.msg = f'{entity.__class__.__name__} is not a User Entity.'

        result.msg = entity.validate_data()

        if result.qty_msg():
            result.entities = entity
            return result

        try:
            new_user = self.repository.registry(entity)
            result.entities = new_user
            return result
        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result
