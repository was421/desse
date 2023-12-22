import struct,time
from flask_login import UserMixin
from datetime import datetime
from core.Util import *

class Player(object):
    #--keys--
    characterID:str = ""
    region:str = ""
    #--misc data--
    ip:str = ""
    banned:bool = False
    #--settings--
    mm_password = ""
    slmm:bool = False
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
    
    
    def __init__(self, characterID:str = "") -> None:
        self.characterID = characterID
    
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
    def __init__(self):
        pass
        
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
    def __init__(self, characterID, ghostBlockID, replayData):
        self.characterID = characterID
        self.ghostBlockID = ghostBlockID
        self.replayData = replayData
        self.region = ""
        self.timestamp = time.time()

class Message(object):
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
    
 
class Account(UserMixin):
    _id:str
    _characterID:str
    _region:str
    _rpcs3:bool
    _banned:bool
    _connection_uuid4:str
    _ip:str
    _last_login:datetime
    _mm_password:str
    _slmm:bool
    _player:Player
    
    def init_from_player_logon(self,uuid4:str,characterID:str,ip:str,region:str):
        self._connection_uuid4 = uuid4
        self._characterID = characterID
        self._ip = ip
        self._region = region
    
    def get_id(self):
        return self._id
    
    def get_npid(self)->str:
        return self._characterID
    
    def _as_db_tuple(self):
        return (self._characterID,
                self._region,
                self._ip,
                self._last_login,
                int(self._banned),
                self._mm_password,
                int(self._slmm),
                int(self._rpcs3))