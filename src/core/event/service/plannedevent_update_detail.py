from src.core import usecase_map
from src.core.event import PlannedEvent
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from .plannedevent_repository import PlannedEventRepository


@usecase_map('/plannedevent/update_detail')
class PlannedEventUpdateDetail(UseCase):
    
    def __init__(self, repository: PlannedEventRepository):
        self.repository = repository

    def execute(self, entity: PlannedEvent) -> Result:
        result = Result()

        if entity.id is None:
            result.msg = f'Não foi infomando o identificador do evento a ser atualizado.'
        
        plannedevent_filter = PlannedEvent(id_=entity.id)
        plannedevent_exists: PlannedEvent = self.repository.find_by_field(plannedevent_filter)

        if not plannedevent_exists:
            result.msg = f'Não foi encontrado nenhum evento cadastrado para o id={entity.id}'
            result.entities = entity
            return result
        else:
            plannedevent_exists = plannedevent_exists[-1]

        filters = dict([v for v in vars(entity).items() if not v[0].startswith('_') and v[-1] is not None])        
        
        kwargs = {}
        for attr, value in filters.items():
            if attr in 'nome tematica data_inicio data_fim descricao':
                kwargs[attr] = value

        if len(kwargs) == 0:
            result.msg = f'Field is empty.'
            result.entities = entity
            return result
        
        count = 0
        same_value = []
        for attr, value in kwargs.items():
            if getattr(plannedevent_exists, attr) != value:
                setattr(plannedevent_exists, attr, value)
            else:
                same_value.append(attr)
                count += 1
        
        if count == len(kwargs):
            result.msg = f'Os valores novos e atuais para os campos={same_value} são os mesmos ou há algum campo vazio na tabela.'

        result.msg = plannedevent_exists.validate_data()

        if result.qty_msg() != 0:
            result.entities = entity
            return result
        
        try:
            updated_plannedevent = self.repository.update(plannedevent_exists)
            result.entities = updated_plannedevent
            return result
        except Exception as error:
            result.msg = f'PlannedEventRemoveError:{error}'
            result.entities = entity
            return result
        