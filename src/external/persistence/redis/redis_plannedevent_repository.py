import datetime
import json
from typing import List

import redis
import streamlit as st

from config import Config
from src.core.shared.utils import string_to_date
from src.core.event import PlannedEvent, PlannedEventRepository
from src.external.persistence import repository_map


@repository_map
class RedisPlannedEventRepository(PlannedEventRepository):
    def __init__(self):
        self.r = redis.Redis(
            host             = Config.HOST,
            port             = Config.PORT,
            password         = Config.PASSWORD,
            decode_responses = True,
        )

    def registry(self, entity: PlannedEvent) -> PlannedEvent:
        hash_main = entity.__class__.__name__

        # Get a id sequence to planned event
        entity.id = self.get_plannedevent_id_sequence()
        entity.created_at = datetime.datetime.now().date()

        plannedevent_dict = entity.data_to_redis()

        new_plannedevent = json.dumps(plannedevent_dict)

        # Register the new planned event in redis
        is_inserted = self.r.hsetnx(hash_main, entity.id, new_plannedevent)

        # Checks if a planned event was inserted
        if not is_inserted:
            raise Exception(
                f'O identificador id="{entity.id}" já existe.'
            )

        # self.set_map_id_username(entity)

        return entity

    def get_all(self, entity: PlannedEvent) -> List[PlannedEvent]:
        resp = self.r.hgetall(entity.__class__.__name__)

        plannedevent_list = list()

        for name, value in resp.items():
            data = json.loads(value)

            plannedevent_list.append(
                PlannedEvent(
                    id_=data.get("id"),
                    created_at=string_to_date(data.get("created_at")),
                    updated_at=string_to_date(data.get("updated_at")),
                    nome=data.get("nome"),
                    tematica=data.get("tematica"),
                    data_inicio=string_to_date(data.get("data_inicio")),
                    data_fim=string_to_date(data.get("data_fim")),
                    descricao=data.get("descricao"),
                    status=data.get("status"),
                    user_id=data.get("user_id"),
                )
            )
        return list(sorted(plannedevent_list, key=lambda x: x.id))

    def update(self, entity: PlannedEvent) -> PlannedEvent:
        hash_main = entity.__class__.__name__
        # Verifica se o evento planejado já existe antes de atualizá-lo
        if not self.r.hexists(hash_main, entity.id):
            raise Exception(f'O identificador id="{entity.id}" não existe. Não é possível atualizar.')

        entity.updated_at = datetime.datetime.now().date()

        plannedevent_dict = entity.data_to_redis()
        updated_plannedevent = json.dumps(plannedevent_dict)

        # Atualiza os dados do evento planejado no Redis
        self.r.hset(hash_main, entity.id, updated_plannedevent)

        return entity

    def find_by_field(self, entity: PlannedEvent) -> List[PlannedEvent]:
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

        hash_main = PlannedEvent.__name__  # Nome da classe PlannedEvent

        plannedenvet_list = []

        # Obtém todos os usuários no hash do Redis
        all_plannedevents = self.r.hgetall(hash_main)

        for name, value in all_plannedevents.items():
            plannedevent_data = json.loads(value)
            is_match = True

            # Verifica cada parâmetro de palavra-chave fornecido
            for key, expected_value in kwargs.items():
                # Verifica se o campo existe e se corresponde ao valor esperado
                if key not in plannedevent_data or plannedevent_data[key] != expected_value:
                    is_match = False
                    break  # Interrompe a verificação se houver uma não correspondência

            if is_match:
                plannedevent = PlannedEvent(
                    id_=plannedevent_data.get("id"),
                    created_at=string_to_date(plannedevent_data.get("created_at")),
                    updated_at=string_to_date(plannedevent_data.get("updated_at")),
                    nome=plannedevent_data.get("nome"),
                    tematica=plannedevent_data.get("tematica"),
                    data_inicio=string_to_date(plannedevent_data.get("data_inicio")),
                    data_fim=string_to_date(plannedevent_data.get("data_fim")),
                    descricao=plannedevent_data.get("descricao"),
                    status=plannedevent_data.get("status"),
                    user_id=plannedevent_data.get("user_id"),
                )
                
                plannedenvet_list.append(plannedevent)

        return sorted(plannedenvet_list, key=lambda x: x.id)

    def remove(self, entity: PlannedEvent) -> bool:
        raise Exception(
            '"remove" method in "SlalchemyUserRepository" is not implemented'
        )

    def get_by_id(self, entity: PlannedEvent) -> PlannedEvent:
        raise Exception(
            '"get_by_id" method in "SlalchemyUserRepository" is not implemented'
        )


    def get_plannedevent_id_sequence(self):
        key_sequence = "plannedevent_id_sequence"
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        new_id = self.r.incr(key_sequence)
        return new_id
