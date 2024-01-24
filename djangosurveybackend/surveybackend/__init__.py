from . import settings
from .container import Container

container = Container()
container.config.from_dict(settings.__dict__)
