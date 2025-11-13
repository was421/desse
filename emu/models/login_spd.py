from emu.models._base import SpdRequest, SpdResponse
from pydantic import Field
from enum import Enum

class LoginRequest(SpdRequest):
    NPID: str = Field("")
    rang: str = Field("")
    region: str = Field("")
    ver: int = Field(100)
    
class LoginMessage(Enum):
    PRESENT_EULA = b'\x00'
    PRESENT_MOTD = b'\x01'
    LOGIN_SUCCESS = PRESENT_MOTD
    ACCOUNT_SUSPENDED = b'\x02'
    ACCOUNT_BANNED = b'\x03'
    SERVER_MAINTENANCE = b'\x05'
    SERVICE_TERMINATED = b'\x06'
    VERSION_MISMATCH = b'\x07'
    
    
class LoginResponse(SpdResponse):
    message_type: LoginMessage = Field(LoginMessage.LOGIN_SUCCESS)
    motds:list[str] = Field(default_factory=list)