from typing import TypeVar, Any

NULL: object = ...

T = TypeVar('T')

def from_buffer(_type: str, data: bytes) -> Any: ...
def buffer(data: Any, size: int) -> Any: ...
def gc(obj: T, func: Any, size: int) -> T: ...
