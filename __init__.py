from .utils.version import version
from .src.main import VideoStream
from .src.getter import BaseGetterVideoStream

__all__ = [
    'VideoStream',
    'BaseGetterVideoStream',
]

__version__ = version()