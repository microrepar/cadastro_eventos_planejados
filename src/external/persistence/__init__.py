
"""persistence module
"""
import os
from importlib import import_module
from pathlib import Path
from src.core.shared.repository import Repository
from dotenv import load_dotenv

load_dotenv()


class RepositoryNotFoundError():
    def __init__(self):
        pass

 
repositories = {'default': RepositoryNotFoundError}


def repository_map(cls):
    repositories.update({cls.__base__.__name__: cls})
    return cls

FRAMEWORK_NAME = os.getenv('FRAMEWORK_NAME')

if FRAMEWORK_NAME is None:
    raise Exception('There is no a repository framework name defined in enviroment.')


here = Path(os.path.dirname(__file__))
for framework in here.iterdir():
    if framework.is_dir() and framework.name in FRAMEWORK_NAME:
        for repository in framework.iterdir():
            if repository.name.endswith('_repository.py') \
                    and not repository.name.startswith('_'):
                framework_name = framework.name
                repository_name = repository.name.split('.')[0]

                module = import_module('src.external.persistence.{}.{}'.format(framework_name, repository_name))
                # print('src.external.persistence.{}.{}'.format(framework_name, repository_name))
