from src.core import usecase_map
from src.core.event import PlannedEvent
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from .plannedevent_repository import PlannedEventRepository


@usecase_map('/planned_event/get_all_tematicas')
class PlannedEventGetAllTematicas(UseCase):
    
    def __init__(self, repository: PlannedEventRepository):
        self.repository = repository

    def execute(self, entity: PlannedEvent) -> Result:
        result = Result()

        if not isinstance(entity, PlannedEvent):
            result.msg = f'{entity.__class__.__name__} is not a PlannedEvent Entity.'

        try:
            plannedevent_list = self.repository.get_all(entity)            
            
            tematica_list = [f"{ev.tematica.upper()}" for ev in plannedevent_list if ev.tematica]
            sorted_tematica_list = sorted(list(set(tematica_list)))
            result.objects = sorted_tematica_list
            
            return result
        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result