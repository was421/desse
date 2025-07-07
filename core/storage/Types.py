from dataclasses import dataclass
import struct,time
from flask_login import UserMixin
from datetime import datetime
from core.Util import *
from typing import List, Tuple, Required

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
#--Game Message Types----------------------------------------------------------
class Player(object):
    #--keys--
    characterID:str = ""
    region:str = ""
    #--misc data--
    ip:str = ""
    banned:bool = False
    #--settings--
    mm_password = ""
    slmm:bool = True
    rpcs3:bool = False
    desired_tendency:int = 0
    #--ratings--
    gradeS:int = 0
    gradeA:int = 0
    gradeB:int = 0
    gradeC:int = 0
    gradeD:int = 0
    #--stored tendancy--
    wb1:int = 0
    wb2:int = 0
    wb3:int = 0
    wb4:int = 0
    wb5:int = 0
    wb6:int = 0
    wb7:int = 0
    #--stats--
    numsessions:int = 0
    messagerating:int = 0
    
    def as_tuple(self) -> tuple[str,int,int,int,int,int,int,int,int]:
        return (self.characterID,self.gradeS,self.gradeA,self.gradeB,self.gradeC,self.gradeD,self.numsessions,self.messagerating,self.desired_tendency)
    
    def from_tuple(self,data:tuple[str,int,int,int,int,int,int,int,int]):
        self.characterID = data[0]
        self.gradeS = data[1]
        self.gradeA = data[2]
        self.gradeB = data[3]
        self.gradeC = data[4]
        self.gradeD = data[5]
        self.numsessions = data[6]
        self.messagerating = data[7]
        self.desired_tendency = data[8]
    
    def get_stats(self) -> tuple[int,int,int,int,int,int]:
        return (self.gradeS,self.gradeA,self.gradeB,self.gradeC,self.gradeD,self.numsessions)
    
    def __repr__(self) -> str:
        return f"Player {self.characterID}"
 
class Replay(object):

    ghostID:int = 0
    characterID:str = ""
    blockID:int = 0
    posx:float = 0.0
    posy:float = 0.0
    posz:float = 0.0
    angx:float = 0.0
    angy:float = 0.0
    angz:float = 0.0
    messageID:int = 0
    mainMsgID:int = 0
    addMsgCateID:int = 0
    replayBinary:bytes = b""
    legacy:int = 0

    def unserialize(self, data):
        sio = io.BytesIO(data)
        self.ghostID = struct.unpack("<I", sio.read(4))[0]
        self.characterID = readcstring(sio)
        self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz = struct.unpack("<iffffff", sio.read(28))
        self.messageID, self.mainMsgID, self.addMsgCateID = struct.unpack("<iii", sio.read(12))
        self.replayBinary = readcstring(sio)
        assert sio.read() == "".encode()
        self.legacy = 1
    
    def from_params(self, params, ghostID, rawReplay):
        self.ghostID = ghostID
        self.characterID = params["characterID"]
        self.blockID = make_signed(int(params["blockID"]))
        self.posx = float(params["posx"])
        self.posy = float(params["posy"])
        self.posz = float(params["posz"])
        self.angx = float(params["angx"])
        self.angy = float(params["angy"])
        self.angz = float(params["angz"])
        self.messageID = int(params["messageID"])
        self.mainMsgID = int(params["mainMsgID"])
        self.addMsgCateID = int(params["addMsgCateID"])
        self.replayBinary = base64.b64encode(rawReplay).replace(b"+", b" ")
        self.legacy = 0

    def from_db_row(self, row):
        self.ghostID, self.characterID, self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz, self.messageID, self.mainMsgID, self.addMsgCateID, self.replayBinary, self.legacy = row
        self.characterID = convert_to_bytearray(self.characterID)
        self.replayBinary = convert_to_bytearray(self.replayBinary)

    def to_db_row(self):
        return (self.ghostID, self.characterID, self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz, self.messageID, self.mainMsgID, self.addMsgCateID, self.replayBinary, self.legacy)

    def serialize_header(self):
        res:bytearray = bytearray()
        res += struct.pack("<I", self.ghostID)
        if(isinstance(self.characterID,str)):
            self.characterID = self.characterID.encode()
        res += self.characterID + b"\x00"
        res += struct.pack("<iffffff", self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz)
        res += struct.pack("<iii", self.messageID, self.mainMsgID, self.addMsgCateID)
        return res

    def __str__(self):
        return "<Replay: ghostID %d player %r block %s>" % (self.ghostID, self.characterID, BLOCK_NAMES[self.blockID])
    
class SOSData(object):
    def __init__(self, params, sosID:int):
        self.sosID = sosID
        self.blockID = make_signed(int(params["blockID"]))
        self.characterID:str = params["characterID"]
        self.posx = float(params["posx"])
        self.posy = float(params["posy"])
        self.posz = float(params["posz"])
        self.angx = float(params["angx"])
        self.angy = float(params["angy"])
        self.angz = float(params["angz"])
        self.messageID = int(params["messageID"])
        self.mainMsgID = int(params["mainMsgID"])
        self.addMsgCateID = int(params["addMsgCateID"])
        self.playerInfo = params["playerInfo"]
        self.qwcwb = int(params["qwcwb"])
        self.qwclr = int(params["qwclr"])
        self.isBlack = int(params["isBlack"])
        self.playerLevel = int(params["playerLevel"])
        self.ratings = (1, 2, 3, 4, 5) # S, A, B, C, D
        self.totalsessions:int = 123
        
        self.updatetime = time.time()
    
    def get_characterID(self)->str:
        if isinstance(self.characterID,bytes):
            return bytes(self.characterID).decode()
        if isinstance(self.characterID,bytearray):
            return bytes(self.characterID).decode()
        return self.characterID
        
    def serialize(self) -> bytes:
        res:bytearray = bytearray()
        res += struct.pack("<I", self.sosID)
        self.characterID = convert_to_bytearray(self.characterID)
        res += self.characterID + b"\x00"
        res += struct.pack("<fff", self.posx, self.posy, self.posz)
        res += struct.pack("<fff", self.angx, self.angy, self.angz)
        res += struct.pack("<III", self.messageID, self.mainMsgID, self.addMsgCateID)
        res += struct.pack("<I", 0) # unknown1
        for r in self.ratings:
            res += struct.pack("<I", r)
        res += struct.pack("<I", 0) # unknown2
        res += struct.pack("<I", self.totalsessions)
        res += convert_to_bytearray(self.playerInfo) + b"\x00"
        res += struct.pack("<IIb", self.qwcwb, self.qwclr, self.isBlack)
        
        return res
        
    def __repr__(self):
        if self.isBlack == 1:
            summontype = "Red"
        elif self.isBlack == 2:
            summontype = "Blue"
        elif self.isBlack == 3:
            summontype = "Invasion"
        else:
            summontype = "Unknown (%d)" % self.isBlack
            
        return "<SOS id#%d %s %r %s lv%d>" % (self.sosID, BLOCK_NAMES[self.blockID], self.characterID, summontype, self.playerLevel)

class Ghost(object):
    characterID:str = ""
    ghostBlockID:int = 0
    replayData:bytes = b""
    region:str = ""
    timestamp:int = 0

    def __init__(self, characterID, ghostBlockID, replayData):
        self.characterID = characterID
        self.ghostBlockID = ghostBlockID
        self.replayData = replayData
        self.region = ""
        self.timestamp = time.monotonic_ns()

class Message(object):
    bmID:int = 0
    characterID:str = ""
    blockID:int = 0
    posx:float = 0.0
    posy:float = 0.0
    posz:float = 0.0
    angx:float = 0.0
    angy:float = 0.0
    angz:float = 0.0
    messageID:int = 0
    mainMsgID:int = 0
    addMsgCateID:int = 0
    rating:int = 0
    legacy:int = 0

    def __init__(self):
        pass
        
    def unserialize(self, data):
        sio = io.BytesIO(data)
        self.bmID = struct.unpack("<I", sio.read(4))[0]
        self.characterID = readcstring(sio)
        self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz = struct.unpack("<iffffff", sio.read(28))
        self.messageID, self.mainMsgID, self.addMsgCateID, self.rating = struct.unpack("<iiii", sio.read(16))
        assert sio.read() == "".encode()
        self.legacy = 1
        
    def from_params(self, params, bmID):
        self.bmID = bmID
        self.characterID = params["characterID"]
        self.blockID = make_signed(int(params["blockID"]))
        self.posx = float(params["posx"])
        self.posy = float(params["posy"])
        self.posz = float(params["posz"])
        self.angx = float(params["angx"])
        self.angy = float(params["angy"])
        self.angz = float(params["angz"])
        self.messageID = int(params["messageID"])
        self.mainMsgID = int(params["mainMsgID"])
        self.addMsgCateID = int(params["addMsgCateID"])
        self.rating = 0
        self.legacy = 0

    def from_db_row(self, row):
        self.bmID, self.characterID, self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz, self.messageID, self.mainMsgID, self.addMsgCateID, self.rating, self.legacy = row
        self.characterID = ensure_is_bytes(self.characterID)
        
    def to_db_row(self):
        return (self.bmID, self.characterID, self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz, self.messageID, self.mainMsgID, self.addMsgCateID, self.rating, self.legacy)
        
    def serialize(self):
        res:bytearray = bytearray()
        res += struct.pack("<I", self.bmID)
        self.characterID = ensure_is_bytes(self.characterID)
        res += self.characterID + b"\x00"
        res += struct.pack("<iffffff", self.blockID, self.posx, self.posy, self.posz, self.angx, self.angy, self.angz)
        res += struct.pack("<iiii", self.messageID, self.mainMsgID, self.addMsgCateID, self.rating)
        return res

    def __str__(self):
        if self.mainMsgID in MESSAGE_IDS:
            if self.messageID in MESSAGE_IDS:
                extra = MESSAGE_IDS[self.messageID]
            else:
                extra = "[%d]" % self.messageID
                
            message = MESSAGE_IDS[self.mainMsgID].replace("***", extra)
            prettymessage = "%d %s %r %s %d" % (self.bmID, BLOCK_NAMES[self.blockID], self.characterID, message, self.rating)
            
        else:
            prettymessage = "%d %s %r [%d] [%d] %d" % (self.bmID, BLOCK_NAMES[self.blockID], self.characterID, self.messageID, self.mainMsgID, self.rating)

        return prettymessage

class ActiveConnection(object):
    _characterID:str = ""
    _ip:str = ""
    _connection_uuid4:str = ""
    _db_uuid4:str = ""
    _region:str = ""
    _last_seen:datetime
    
    def __init__(self) -> None:
        self.update_time()
    
    def init_from_player_logon(self,uuid4:str,characterID:str,ip:str,region:str):
        self._connection_uuid4 = uuid4
        self._characterID = characterID
        self._ip = ip
        self._region = region
    
    def update_time(self):
        self._last_seen = datetime.now()
        
    def get_npid(self)->str:
        return self._characterID
#------------------------------------------------------------------------------

#--Website Message Types-------------------------------------------------------

class Account(object):
    id:str
    username:str
    password_hash:str
    characters:List[tuple[str,str]]#list of (characterID,region)


#------------------------------------------------------------------------------

#--SQLAlchemy Models-----------------------------------------------------------
class Base(DeclarativeBase):
    pass

class PlayerModel(Base):
    __tablename__ = 'players'
    #--keys--
    id: Mapped[int] = mapped_column(primary_key=True)
    characterID: Mapped[str] = mapped_column()
    #--misc data--
    region: Mapped[str] = mapped_column()
    ip: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column()
    banned: Mapped[bool] = mapped_column()
    #--settings--
    mm_password: Mapped[str] = mapped_column()
    slmm: Mapped[bool] = mapped_column()
    rpcs3: Mapped[bool] = mapped_column()
    desired_tendency: Mapped[int] = mapped_column()
    #--ratings--
    gradeS: Mapped[int] = mapped_column()
    gradeA: Mapped[int] = mapped_column()
    gradeB: Mapped[int] = mapped_column()
    gradeC: Mapped[int] = mapped_column()   
    gradeD: Mapped[int] = mapped_column()
    #--stored tendancy--
    wb1: Mapped[int] = mapped_column()
    wb2: Mapped[int] = mapped_column()
    wb3: Mapped[int] = mapped_column()
    wb4: Mapped[int] = mapped_column()
    wb5: Mapped[int] = mapped_column()
    wb6: Mapped[int] = mapped_column()
    wb7: Mapped[int] = mapped_column()
    #--stats--
    numsessions: Mapped[int] = mapped_column()
    messagerating: Mapped[int] = mapped_column()

    @classmethod
    def to_player(self):
        player = Player()
        player.characterID = self.characterID
        player.region = self.region
        player.ip = self.ip
        player.banned = self.banned
        player.mm_password = self.mm_password
        player.slmm = self.slmm
        player.rpcs3 = self.rpcs3
        player.desired_tendency = self.desired_tendency
        player.gradeS = self.gradeS
        player.gradeA = self.gradeA
        player.gradeB = self.gradeB
        player.gradeC = self.gradeC
        player.gradeD = self.gradeD
        player.wb1 = self.wb1
        player.wb2 = self.wb2
        player.wb3 = self.wb3
        player.wb4 = self.wb4
        player.wb5 = self.wb5
        player.wb6 = self.wb6
        player.wb7 = self.wb7
        player.numsessions = self.numsessions
        player.messagerating = self.messagerating
        return player

class ReplayModel(Base):
    __tablename__='replays'
    ghostID: Mapped[int] = mapped_column(primary_key=True)
    characterID: Mapped[str] = mapped_column()
    blockID: Mapped[int] = mapped_column()
    posx: Mapped[float] = mapped_column()
    posy: Mapped[float] = mapped_column()
    posz: Mapped[float] = mapped_column()
    angx: Mapped[float] = mapped_column()
    angy: Mapped[float] = mapped_column()
    angz: Mapped[float] = mapped_column()
    messageID: Mapped[int] = mapped_column()
    mainMsgID: Mapped[int] = mapped_column()
    addMsgCateID: Mapped[int] = mapped_column()
    replayBinary: Mapped[bytes] = mapped_column()
    legacy: Mapped[int] = mapped_column()

    @classmethod
    def to_replay(self):
        replay = Replay()
        replay.ghostID = self.ghostID
        replay.characterID = self.characterID
        replay.blockID = self.blockID
        replay.posx = self.posx
        replay.posy = self.posy
        replay.posz = self.posz
        replay.angx = self.angx
        replay.angy = self.angy
        replay.angz = self.angz
        replay.messageID = self.messageID
        replay.mainMsgID = self.mainMsgID
        replay.addMsgCateID = self.addMsgCateID
        replay.replayBinary = self.replayBinary
        replay.legacy = self.legacy
        return replay

class SOSModel(Base):
    __tablename__='sos'
    sosID: Mapped[int] = mapped_column(primary_key=True)
    blockID: Mapped[int] = mapped_column()
    characterID: Mapped[str] = mapped_column()
    posx: Mapped[float] = mapped_column()
    posy: Mapped[float] = mapped_column()
    posz: Mapped[float] = mapped_column()
    angx: Mapped[float] = mapped_column()
    angy: Mapped[float] = mapped_column()
    angz: Mapped[float] = mapped_column()
    messageID: Mapped[int] = mapped_column()
    mainMsgID: Mapped[int] = mapped_column()
    addMsgCateID: Mapped[int] = mapped_column()
    playerInfo: Mapped[str] = mapped_column()
    qwcwb: Mapped[int] = mapped_column()
    qwclr: Mapped[int] = mapped_column()
    isBlack: Mapped[int] = mapped_column()
    playerLevel: Mapped[int] = mapped_column()
    ratings: Mapped[Tuple[int]] = mapped_column()
    totalsessions: Mapped[int] = mapped_column()
    updatetime: Mapped[float] = mapped_column()

    @classmethod
    def to_sos(self):
        sos = SOSData()
        sos.sosID = self.sosID
        sos.blockID = self.blockID
        sos.characterID = self.characterID
        sos.posx = self.posx
        sos.posy = self.posy
        sos.posz = self.posz
        sos.angx = self.angx
        sos.angy = self.angy
        sos.angz = self.angz
        sos.messageID = self.messageID
        sos.mainMsgID = self.mainMsgID
        sos.addMsgCateID = self.addMsgCateID
        sos.playerInfo = self.playerInfo
        sos.qwcwb = self.qwcwb
        sos.qwclr = self.qwclr
        sos.isBlack = self.isBlack
        sos.playerLevel = self.playerLevel
        sos.ratings = self.ratings
        sos.totalsessions = self.totalsessions
        sos.updatetime = self.updatetime
        return sos
    

class GhostModel(Base):
    __tablename__='ghosts'
    characterID: Mapped[str] = mapped_column()
    ghostBlockID: Mapped[int] = mapped_column()
    replayData: Mapped[bytes] = mapped_column()
    region: Mapped[str] = mapped_column()
    timestamp: Mapped[int] = mapped_column()
    
    @classmethod
    def to_ghost(self):
        ghost = Ghost()
        ghost.characterID = self.characterID
        ghost.ghostBlockID = self.ghostBlockID
        ghost.replayData = self.replayData
        ghost.region = self.region
        ghost.timestamp = self.timestamp
        return ghost


class MessageModel(Base):
    __tablename__='messages'
    bmID: Mapped[int] = mapped_column(primary_key=True)
    characterID: Mapped[str] = mapped_column()
    blockID: Mapped[int] = mapped_column()
    posx: Mapped[float] = mapped_column()
    posy: Mapped[float] = mapped_column()
    posz: Mapped[float] = mapped_column()
    angx: Mapped[float] = mapped_column()
    angy: Mapped[float] = mapped_column()
    angz: Mapped[float] = mapped_column()
    messageID: Mapped[int] = mapped_column()
    mainMsgID: Mapped[int] = mapped_column()
    addMsgCateID: Mapped[int] = mapped_column()
    rating: Mapped[int] = mapped_column()
    legacy: Mapped[int] = mapped_column()

    @classmethod
    def to_message(self):
        message = Message()
        message.bmID = self.bmID
        message.characterID = self.characterID
        message.blockID = self.blockID
        message.posx = self.posx
        message.posy = self.posy
        message.posz = self.posz
        message.angx = self.angx
        message.angy = self.angy
        message.angz = self.angz
        message.messageID = self.messageID
        message.mainMsgID = self.mainMsgID
        message.addMsgCateID = self.addMsgCateID
        message.rating = self.rating
        message.legacy = self.legacy
        return message
    
class ActiveConnectionModel(Base):
    __tablename__='active_connections'
    characterID: Mapped[str] = mapped_column()
    ip: Mapped[str] = mapped_column()
    connection_uuid4: Mapped[str] = mapped_column(primary_key=True)
    region: Mapped[str] = mapped_column()
    last_seen: Mapped[datetime] = mapped_column()
    
    @classmethod
    def to_active_connection(self):
        connection = ActiveConnection()
        connection._characterID = self.characterID
        connection._ip = self.ip
        connection._connection_uuid4 = self.connection_uuid4
        connection._region = self.region
        connection._last_seen = self.last_seen
        return connection
    

#--- Website Models -----------------------------------------------------------

class AccountModel(Base):
    __tablename__ = 'accounts'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    password_hash: Mapped[str] = mapped_column()

    @classmethod
    def to_account(self):
        account = Account()
        account.id = self.id
        account.username = self.username
        account.password_hash = self.password_hash
        return account

#------------------------------------------------------------------------------