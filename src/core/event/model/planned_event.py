import datetime
from src.core.user import User

from src.core.shared.entity import Entity
from src.core.shared.utils import date_to_string, datetime_to_string


class PlannedEvent(Entity):

    def __init__(self, 
                 id_         : int =None,
                 created_at  : datetime.date = None,
                 updated_at  : datetime.date = None,
                 nome        : str = None,
                 tematica    : str = None,
                 data_inicio : datetime.date = None,
                 data_fim    : datetime.date = None,
                 user_id     : int = None,
                 descricao   : str = None,
                 status      : str = None):
        super().__init__(id_, created_at, updated_at)
        
        self.nome        = nome
        self.tematica    = tematica
        self.data_inicio = data_inicio
        self.data_fim    = data_fim
        self.user_id     = user_id
        self.descricao   = descricao
        self.status      = status


    def __repr__(self) -> str:
        return (
            'PlannedEvent('
                f'id_={self.id}, '
                f'created_at={self.created_at}, '
                f'updated_at={self.updated_at}, '
                f'nome={self.nome}, '
                f'tematica={self.tematica}, '
                f'data_inicio={self.data_inicio}, '
                f'data_fim={self.data_fim}, '
                f'descricao={self.descricao}, '
                f'status={self.status}, '
                f'user_id={self.user_id}'
            ')'
        )

    def data_to_dataframe(self):
        return [
            {
                'id'          : self.id,
                # 'created_at'  : self.created_at,
                # 'updated_at'  : self.updated_at,
                'nome'        : self.nome,
                'tematica'    : self.tematica,
                'data_inicio' : self.data_inicio,
                'data_fim'    : self.data_fim,
                # 'user_id'     : self.user_id,
                'descricao'   : self.descricao,
                'status'      : self.status,
            }
        ]
    
    def data_to_redis(self):
        return {
            'id'          : self.id,
            'created_at'  : date_to_string(self.created_at),
            'updated_at'  : datetime_to_string(self.updated_at),
            'nome'        : self.nome,
            'tematica'    : self.tematica,
            'data_inicio' : date_to_string(self.data_inicio),
            'data_fim'    : date_to_string(self.data_fim),
            'user_id'     : self.user_id,
            'descricao'   : self.descricao,
            'status'      : self.status,
        }

    def validate_data(self):
        messages = []

        for attr in ['nome', 'tematica', 'data_inicio', 'data_fim' ]:
            value = getattr(self, attr, None)
            if value is None:
                messages.append(
                    f'O campo "{attr}" é obrigatório o preenchimento'
                )
            else:
                value = date_to_string(value)
                value = value.strip()
                if value == '':
                    messages.append(
                        f'O campo "{attr}" é obrigatório o preenchimento'
                    )

        hoje = datetime.datetime.now().date()

        if hoje >= self.data_inicio \
                or hoje >= self.data_fim \
                or self.data_inicio > self.data_fim:
            messages.append(
                f'Inconsistências nas datas: A data início e fim não podem ser anteriores ou iguais a data atual, '
                'e a data fim não pode ser anterior a data início'
            )
        return messages
