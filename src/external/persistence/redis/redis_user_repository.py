import datetime
import json
from typing import List

import redis
from config import Config
from src.core.user import User, UserRepository
from src.external.persistence import repository_map


@repository_map
class UserRepository(UserRepository):
    def __init__(self):
        self.r = redis.Redis(
            host             = Config.HOST,
            port             = Config.PORT,
            password         = Config.PASSWORD,
            decode_responses = True,
        )

    def registry(self, entity: User) -> User:
        hash_main = entity.__class__.__name__

        # Get a id sequence to notebook
        entity.id = self.get_user_id_sequence()
        entity.created_at = datetime.datetime.now().date()

        user_dict = entity.data_to_redis()

        new_user = json.dumps(user_dict)

        # Register the new notebook in redis
        is_inserted = self.r.hsetnx(hash_main, entity.username, new_user)

        # Checks if a notebook was inserted
        if not is_inserted:
            raise Exception(
                f'O username "{entity.username}" já existe. Escolha outro username!'
            )

        self.set_map_id_username(entity)

        return entity

    def get_all(self, entity: User) -> List[User]:
        resp = self.r.hgetall(entity.__class__.__name__)

        user_list = list()

        for name, value in resp.items():
            data = json.loads(value)

            user_list.append(
                User(
                    id_=data.get("id"),
                    created_at=data.get("created_at"),
                    updated_at=data.get("updated_at"),
                    status=data.get("status"),
                    name=data.get("name"),
                    age=data.get("age"),
                    email=data.get("email"),
                    username=data.get("username"),
                    password=data.get("password"),
                    repeat_password=data.get("repeat_password"),
                )
            )
        return list(sorted(user_list, key=lambda x: x.id))

    def update(self, entity: User) -> User:
        hash_main = entity.__class__.__name__

        # Verifica se o usuário já existe antes de atualizá-lo
        if not self.r.hexists(hash_main, entity.username):
            raise Exception(
                f'O username "{entity.username}" não existe. Não é possível atualizar.'
            )
        entity.updated_at = datetime.datetime.now()
        user_dict = entity.data_to_redis()
        updated_user = json.dumps(user_dict)

        # Atualiza os dados do usuário no Redis
        self.r.hset(hash_main, entity.username, updated_user)

        return entity

    def find_by_field(self, entity: User) -> List[User]:
        filters = dict(
            [
                v
                for v in vars(entity).items()
                if not v[0].startswith("_") and bool(v[-1])
            ]
        )

        kwargs = {}

        entity_list = []
        for attr, value in filters.items():
            if bool(value) is False:
                continue
            elif attr in "username email id":
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find Users!')

            kwargs[attr] = value

        hash_main = User.__name__  # Nome da classe User

        user_list = []

        # Obtém todos os usuários no hash do Redis
        all_users = self.r.hgetall(hash_main)

        for name, value in all_users.items():
            user_data = json.loads(value)
            is_match = True

            # Verifica cada parâmetro de palavra-chave fornecido
            for key, expected_value in kwargs.items():
                # Verifica se o campo existe e se corresponde ao valor esperado
                if key not in user_data or user_data[key] != expected_value:
                    is_match = False
                    break  # Interrompe a verificação se houver uma não correspondência

            if is_match:
                user = User(
                    id_=user_data["id"],
                    created_at=user_data["created_at"],
                    status=user_data["status"],
                    name=user_data["name"],
                    age=user_data["age"],
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                    repeat_password=user_data["repeat_password"],
                )
                user_list.append(user)

        return sorted(user_list, key=lambda x: x.id)

    def remove(self, entity: User) -> bool:
        raise Exception(
            '"remove" method in "SlalchemyUserRepository" is not implemented'
        )

    def get_by_id(self, entity: User) -> User:
        raise Exception(
            '"get_by_id" method in "SlalchemyUserRepository" is not implemented'
        )

    def get_user_id_sequence(self):
        key_sequence = "user_id_sequence"
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        new_id = self.r.incr(key_sequence)
        return new_id

    def set_map_id_username(self, entity: User):
        hash_main = f"{entity.__class__.__name__}_id"
        self.r.hsetnx(hash_main, entity.id, entity.username)
