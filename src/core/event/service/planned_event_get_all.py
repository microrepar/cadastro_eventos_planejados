from src.core import usecase_map
from src.core.event import PlannedEvent
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from .planned_event_repository import PlannedEventRepository


@usecase_map('/planned_event')
@usecase_map('/planned_event/get_all')
class PlannedEventGetAll(UseCase):
    
    def __init__(self, repository: PlannedEventRepository):
        self.repository = repository

    def execute(self, entity: PlannedEvent) -> Result:
        result = Result()

        if not isinstance(entity, PlannedEvent):
            result.msg = f'{entity.__class__.__name__} is not a PlannedEvent Entity.'

        try:
            plannedevent_list = self.repository.get_all(entity)
            
            if entity.user_id is not None:
                plannedevent_list = [ev for ev in plannedevent_list if ev.user_id == entity.user_id and ev.status != 'removed']
            
            if len(plannedevent_list) > 0:
                result.entities = plannedevent_list
            else:
                result.entities = plannedevent_list
                result.msg = 'There are no users in database.'

            return result
        except Exception as error:
            result.msg = str(error)
            result.entities = entity
            return result