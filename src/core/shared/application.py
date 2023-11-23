"""application module
"""

from typing import List
from collections.abc import Sequence

from .entity import Entity


entity_list = List[Entity]
list_str = List[str]


class Result:

    def __init__(self):
        self._msg = list()
        self._entities: entity_list = list()
        self.form = None

    @property
    def msg(self) -> list_str:
        return self._msg

    @msg.setter
    def msg(self, message: str):
        if isinstance(message, str):
            self._msg += list([message])
        elif isinstance(message, Sequence):
            self._msg += list(message)

    @property
    def entities(self) -> entity_list:
        return self._entities

    @entities.setter
    def entities(self, entities: List[Entity]):
        if isinstance(entities, Entity):
            self._entities += list([entities])
        elif isinstance(entities, Sequence):
            for entity in entities:
                if not isinstance(entity, Entity):
                    raise Exception(f'This {entity} is not Entity.')
            self._entities += list(entities)

    def qty_entities(self):
        return len(self._entities)

    def qty_msg(self):
        return len(self.msg)
    
    def to_dict(self):
        return {
            'messages': self._msg,
            'entities': self._entities,
        }