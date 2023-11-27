import abc
from typing import List


class Entity(abc.ABC):

    def __init__(self, id_=None, created_at=None, updated_at=None):
        self.id = id_
        self.created_at = created_at
        self.updated_at = updated_at

    @abc.abstractmethod
    def validate_data(self) -> List[str]:
        """_summary_
        """

