import base64, traceback, logging, zlib, io, struct, json, logging

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes 

SERVER_PORT_BOOTSTRAP = 18000
SERVER_PORT_US = 18666
SERVER_PORT_EU = 18667
SERVER_PORT_JP = 18668

SERVER_TO_PORT = {'us':SERVER_PORT_US,'eu':SERVER_PORT_EU,'jp':SERVER_PORT_JP}

LEGACY_MESSAGE_THRESHOLD = 5
LEGACY_REPLAY_THRESHOLD = 5

def load_static_data(file_path:str) -> dict[int,str]:
    data:dict[int,str] = {}
    try:
        file_data = open(file_path, "r")
        file_json:dict = json.loads(file_data.read())
        file_data.close()
        for key,value in file_json.items():
            try:
                data[int(key)] = value
            except:
                logging.warning(f"While parsing {file_path} key:{key} and value:{value} could not be parsed")
    except Exception as e:
        logging.error(f"Cannot parse {file_path}: {e}")
    return data

def make_signed(n:int) -> int:
    if n >= (1 << 31):
        return n - (1 << 32)
    else:
        return n
        
def decrypt(ct) -> bytes:
    cipher = Cipher(algorithms.AES(b"11111111222222223333333344444444"),modes.CBC(bytes(ct[0:16])))
    decryptor = cipher.decryptor()
    pt = decryptor.update(bytes(ct[16:])) + decryptor.finalize()
    #pt = pt[:-ord(pt[-1])]
    return pt

def get_params(data:bytes) -> dict[str,str]:
    params = {}
    for param in data.split(b"&"):
        if param == b"\x00" or param == b"":
            continue
            
        if b"=" in param:
            key, value = param.split(b"=", 1)
            #we ignore here since it looks like the last byte tends to be garbage
            params[key.decode(errors='ignore')] = value.decode(errors='ignore')
            
    return params
        
def decode_broken_base64(data) -> bytes:
    s = ""
    for c in data:
        if c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/+":
            s += c
        else:
            if c == " ":
                s += "+"
            else:
                break
    
    if len(s) % 4 == 3:
        s += "="
    elif len(s) % 4 == 2:
        s += "=="
    elif len(s) % 4 == 1:
        s += "A=="

    return base64.b64decode(s)

def readcstring(sio:io.BytesIO) -> str:
    res:bytearray = bytearray([])
    while True:
        c:bytes = sio.read(1)
        assert len(c) == 1
        if c == b"\x00":
            break
            
        res += c
    return res.decode()

def validate_replayData(replayData):
    try:
        z = zlib.decompressobj()
        data = z.decompress(replayData)
        assert z.unconsumed_tail == b""
        
        sio = io.BytesIO(data)
        
        poscount, num1, num2 = struct.unpack(">III", sio.read(12))
        for i in range(poscount):
            posx, posy, posz, angx, angy, angz, num3, num4 = struct.unpack(">ffffffII", sio.read(32))
            
        unknowns = struct.unpack(">iiiiiiiiiiiiiiiiiiii", sio.read(4 * 20))
        playername = sio.read(34).decode("utf-16be").rstrip("\x00")
        assert sio.read() == "".encode()
        
        return True
        
    except:
        tb = traceback.format_exc()
        logging.warning("bad ghost/replay data %r %r\n%s" % (replayData, data, tb))
        return False


BLOCK_NAMES:dict[int,str] = load_static_data("data/blocknames.json")
MESSAGE_IDS:dict[int,str] = load_static_data("data/messageids.json")