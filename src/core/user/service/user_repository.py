from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from src.core.shared.repository import Repository
from src.core.user import User


@runtime_checkable
class UserRepository(Repository, Protocol):
    
    @abstractmethod
    def registry(self, entity: User) -> User:
        """_summary_
        """

    @abstractmethod
    def get_all(self, entity: User) -> List[User]:
        """_summary_
        """

    @abstractmethod
    def update(self, entity: User) -> User:
        """_summary_
        """
    
    @abstractmethod
    def find_by_field(self, entity: User) -> List[User]:
        """_summary_
        """
    
    @abstractmethod
    def get_by_id(self, entity: User) -> User:
        """_summary_
        """
    
    @abstractmethod
    def remove(self, entity: User) -> bool:
        """_summary_
        """