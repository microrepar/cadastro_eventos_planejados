from src.core import usecase_map
from src.core.event import PlannedEvent
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from .plannedevent_repository import PlannedEventRepository


@usecase_map('/planned_event/delete')
class PlannedEventDelete(UseCase):
    
    def __init__(self, repository: PlannedEventRepository):
        self.repository = repository

    def execute(self, entity: PlannedEvent) -> Result:
        result = Result()

        if entity.id is None:
            result.msg = f'Não foi infomando o identificador do evento a ser apagado.'
        
        plannedevent_exists = self.repository.find_by_field(entity)

        if not plannedevent_exists:
            result.msg = f'Não foi encontrado nenhum evento cadastrado para o id={entity.id}'
            result.entities = entity
            return result
        else:
            planned_event = plannedevent_exists[-1]
            planned_event.status = 'removed'
                
        try:
            updated_plannedevent = self.repository.update(planned_event)
            result.entities = updated_plannedevent
            return result
        except Exception as error:
            result.msg = f'PlannedEventRemoveError:{error}'
            result.entities = entity
            return result

        