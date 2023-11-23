from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase
from src.core.user import User

from .user_repository import UserRepository


@usecase_map('/user/update')
class UserUpdate(UseCase):

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, entity: User) -> Result:
        result = Result()
        
        ###################################
        # Add your implementation here
        result.msg = 'UserGetAll Service is not implemented'
        ###################################

        try:
            updated_user = self.repository.update(entity)
            result.entities = updated_user
            return result
        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result
        ###################################

