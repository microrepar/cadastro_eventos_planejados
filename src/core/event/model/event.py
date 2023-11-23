import datetime

from src.core.shared.entity import Entity


class Event(Entity):

    def __init__(self, 
                 id_: int =None, 
                 created_at: datetime.date = None, 
                 updated_at: datetime.date = None,
                 nome        : str = None,
                 tematica    : str = None,
                 data_inicio : datetime.date = None,
                 data_fim    : datetime.date = None,
                 descricao   : str = None):
        super().__init__(id_, created_at, updated_at)
        
        self.nome = nome
        self.tematica = tematica
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.descricao = descricao


    def data_to_dataframe(self):
        return [
            {
                'id'          : self.id,
                'created_at'  : self.created_at,
                'updated_at'  : self.updated_at,
                'nome'        : self.nome,
                'tematica'    : self.tematica,
                'data_inicio' : self.data_inicio,
                'data_fim'    : self.data_fim,
                'descricao'   : self.descricao,
            }
        ]