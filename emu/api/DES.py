from flask import blueprints, request, g
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes 

from emu.models.login_spd import LoginRequest, LoginResponse

AES_KEY = b"11111111222222223333333344444444" #yes, this is the one used by DES

def get_parsed_request_data() -> dict[str,str]:
    return g.request_data

des_bp = blueprints.Blueprint('des', __name__, url_prefix='/api/des')
@des_bp.before_request
def before_request_func():
    #decrypt incoming data
    data = request.get_data()
    ct = data[16:]
    cipher = Cipher(algorithms.AES(AES_KEY),modes.CBC(bytes(data[0:16])))
    decryptor = cipher.decryptor()
    pt = decryptor.update(bytes(ct)) + decryptor.finalize()
    #parse params
    g.request_data = {}
    for param in pt.split(b"&"):
        if param == b"\x00" or param == b"":
            continue
            
        if b"=" in param:
            key, value = param.split(b"=", 1)
            #we ignore here since it looks like the last byte tends to be garbage
            g.request_data[key.decode(errors='ignore')] = value.decode(errors='ignore')
    #
    pass

@des_bp.after_request
def after_request_func(response):
    return response

@des_bp.route('/<region>/<uuid>/login.spd', methods=['POST'])
def login(region:str, uuid:str):
    req = LoginRequest(**get_parsed_request_data())
    #for now we just always return success
    resp = LoginResponse()
    return resp.make_response()