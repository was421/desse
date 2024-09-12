from flask import Blueprint,request
from functools import wraps
from core.Config import Config
from core.Util import *
import uuid,logging,urllib.request


class StatusServer:
    blueprint = Blueprint("STATUS_SERVER",__name__)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(StatusServer, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        conf = Config().get_conf_dict("STATUS_SERVER")
        self._host = conf.get("IP")
        self._port = int(conf.get("PORT"))
        pass
    
    def des_api_bootstrap():
        def _des_api_bootstrap(f):
            @wraps(f)
            def __des_api_bootstrap(*args, **kwargs):
                
                log_packet(request)
                
                body = decrypt(request.get_data())
                if(body is None):
                    logging.warning(f"Non DeS Request Sent To DeS Endpoint {request.url}")
                    return "You Shouldn't Be Here",401
                
                request.args = get_params(body)
                
                command,data = f(*args, **kwargs)
                
                data = convert_to_bytearray(data)
                    
                encoded = convert_to_bytearray(base64.b64encode(data))

                return encoded,200
            return __des_api_bootstrap
        return _des_api_bootstrap
    
    def _check_pulse(self) -> bool:
        try:
            ret:str = urllib.request.urlopen(f"http://{self._host}:{self._port}/heartbeat").read().decode('utf8')
            return (ret == 'online')
        except:
            return False
    
    def _build_ss_info(self,host:str,port:int,uuid4:str,online:bool = True) -> bytes:
        template = b"""
            <ss>?online?</ss>
            <lang1></lang1>
            <lang2></lang2>
            <lang3></lang3>
            <lang4></lang4>
            <lang5></lang5>
            <lang6></lang6>
            <lang7></lang7>
            <lang8></lang8>
            <lang11></lang11>
            <lang12></lang12>
            <gameurl1>http://?host?:?port?/us/?uuid?/</gameurl1>
            <gameurl2>http://?host?:?port?/eu/?uuid?/</gameurl2>
            <gameurl3>http://?host?:?port?/jp/?uuid?/</gameurl3>
            <gameurl4>http://?host?:?port?/jp/?uuid?/</gameurl4>
            <gameurl5>http://?host?:?port?/eu/?uuid?/</gameurl5>
            <gameurl6>http://?host?:?port?/eu/?uuid?/</gameurl6>
            <gameurl7>http://?host?:?port?/eu/?uuid?/</gameurl7>
            <gameurl8>http://?host?:?port?/eu/?uuid?/</gameurl8>
            <gameurl11>http://?host?:?port?/jp/?uuid?/</gameurl11>
            <gameurl12>http://?host?:?port?/jp/?uuid?/</gameurl12>
            <browserurl1>http://?host?:?port?/unk_endpoint1/</browserurl1>
            <browserurl2>http://?host?:?port?/unk_endpoint2/</browserurl2>
            <browserurl3>http://?host?:?port?/unk_endpoint3/</browserurl3>
            <interval1>120</interval1>
            <interval2>120</interval2>
            <interval3>120</interval3>
            <interval4>120</interval4>
            <interval5>120</interval5>
            <interval6>120</interval6>
            <interval7>120</interval7>
            <interval8>120</interval8>
            <interval11>120</interval11>
            <interval12>120</interval12>
            <getWanderingGhostInterval>20</getWanderingGhostInterval>
            <setWanderingGhostInterval>20</setWanderingGhostInterval>
            <getBloodMessageNum>80</getBloodMessageNum>
            <getReplayListNum>80</getReplayListNum>
            <enableWanderingGhost>1</enableWanderingGhost>
            """
        template = template.replace(b"?online?",str(int((not online))).encode())
        template = template.replace(b"?host?",host.encode())
        template = template.replace(b"?port?",str(port).encode())
        template = template.replace(b"?uuid?",uuid4.encode())
        return template
    
    @blueprint.route('/<endpoint>/ss.info', methods=['POST'])
    @des_api_bootstrap()
    def bootstrap(endpoint):
        self = StatusServer()
        uuid4 = str(uuid.uuid4())
        logging.debug(f"{request.remote_addr}|{uuid4} requested ss.info on {endpoint}")
        return 0x00,self._build_ss_info(self._host,self._port,uuid4,self._check_pulse())