# -*- coding: utf-8 -*-
from importlib import metadata

__title__ = metadata.metadata(__package__)['name']
__author__ = metadata.metadata(__package__)['author']
__version__ = metadata.version(__package__)

del metadata

from .config import Config  # noqa: F401,E402
from .subtitle import Subtitle  # noqa: F401,E402
