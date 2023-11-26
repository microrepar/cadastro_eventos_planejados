from src.core import usecase_map
from src.core.event import PlannedEvent
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from .plannedevent_repository import PlannedEventRepository


@usecase_map('/planned_event/registry')
class PlannedEventRegistry(UseCase):
    
    def __init__(self, repository: PlannedEventRepository):
        self.repository = repository

    def execute(self, entity: PlannedEvent) -> Result:
        result = Result()
        
        if not isinstance(entity, PlannedEvent):
            result.msg = f'{entity.__class__.__name__} is not a PlannedEvent Entity.'

        entity.status = 'active'
        result.msg = entity.validate_data()

        if result.qty_msg():
            result.entities = entity
            return result
        
        entity.nome = entity.nome.upper()
        entity.tematica = entity.tematica.upper()
        entity.descricao = entity.descricao.upper()

        try:
            new_user = self.repository.registry(entity)
            result.entities = new_user
            return result
        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result