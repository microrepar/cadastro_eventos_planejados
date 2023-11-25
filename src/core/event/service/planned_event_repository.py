import abc
from typing import List, Protocol, runtime_checkable

from src.core.event import PlannedEvent
from src.core.shared.repository import Repository


@runtime_checkable
class PlannedEventRepository(Repository, Protocol):
    
    @abc.abstractmethod
    def registry(self, entity: PlannedEvent) -> PlannedEvent:
        """Registry a event into database
        """

    @abc.abstractmethod
    def get_all(self, entity: PlannedEvent = None) -> List[PlannedEvent]:
        """Get all registred events in database
        """
    
    @abc.abstractmethod
    def get_by_id(self, entity: PlannedEvent) -> PlannedEvent:
        """Get by id registred events in database
        """
    
    @abc.abstractmethod
    def find_by_field(self, entity: PlannedEvent) -> List[PlannedEvent]:
        """Find by id registred events in database
        """

    @abc.abstractmethod
    def update(self, entity: PlannedEvent) -> PlannedEvent:
        """_summary_
        """