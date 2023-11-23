import abc
from ast import List
from typing import Protocol, runtime_checkable

from src.core.event import Event
from src.core.shared.repository import Repository


@runtime_checkable
class EventRepository(Repository, Protocol):
    @abc.abstractmethod
    def registry(self, entity: Event) -> Event:
        """Registry a event into database
        """

    @abc.abstractmethod
    def get_all(self, entity: Event = None) -> List[Event]:
        """Get all registred events in database
        """
    
    @abc.abstractmethod
    def get_by_id(self, entity: Event) -> Event:
        """Get by id registred events in database
        """
    
    @abc.abstractmethod
    def find_by_field(self, entity: Event) -> List[Event]:
        """Find by id registred events in database
        """
