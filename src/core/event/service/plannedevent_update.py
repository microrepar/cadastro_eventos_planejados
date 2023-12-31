from src.core.event import PlannedEvent
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from .plannedevent_repository import PlannedEventRepository


class PlannedEventUpdate(UseCase):
    
    def __init__(self, repository: PlannedEventRepository):
        super().__init__(repository)

    def execute(self, entity: PlannedEvent) -> Result:
        return super().execute(entity)