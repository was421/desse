from pydantic import BaseModel
import struct
from enum import Enum
from typing import Any

def is_enum(field_type)->bool:
    return issubclass(field_type, Enum)

def get_value_from_enum(enum_value:Enum)->tuple[type, Any]:
    return type(enum_value.value), enum_value.value
    

class Endianness(Enum):
    LITTLE = "<"      # Little-endian
    BIG = ">"         # Big-endian  
    NETWORK = "!"     # Network (big-endian)
    SYSTEM = "="      # System (native)

class BaseSpdModel(BaseModel):
    pass

class SpdRequest(BaseSpdModel):
    pass

#------------------------------------------------------------------------------

class SpdSerializable(BaseSpdModel):
    _endianness: Endianness = Endianness.LITTLE
    
    def to_bytes(self) -> bytes:
        result = bytearray()
        endian_char = self._endianness.value
        
        for field_name, field_info in self.__class__.model_fields.items():
            field_value = getattr(self, field_name)
            
            if field_value is None:
                continue
                
            field_type = field_info.annotation
            
            #handle "complex" types
            if issubclass(field_type, SpdSerializable):
                field_value = field_value.to_bytes()
                field_type = bytes
            elif issubclass(field_type, Enum):
                field_type, field_value = get_value_from_enum(field_value)
            
            #handle basic types
            if field_type == int:
                result += struct.pack(f"{endian_char}I", field_value)
            elif field_type == float:
                result += struct.pack(f"{endian_char}f", field_value)
            elif field_type == str:
                if isinstance(field_value, str):
                    result += field_value.encode('utf-8') + b'\x00'
                else:
                    result += b'\x00'
            elif field_type == bytes:
                result += field_value
            elif field_type == bool:
                result += struct.pack(f"{endian_char}B", 1 if field_value else 0)
            else:
                result += str(field_value).encode('utf-8') + b'\x00'
        
        return bytes(result + b'\x00')
    
class SpdResponse(SpdSerializable):
    pass