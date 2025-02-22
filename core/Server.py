from flask import request,Request
from functools import wraps
import base64,struct,time,uuid

from core.Admin import Admin
from core.Config import Config
from core.FlaskContainer import FlaskContainer as FC
from core.storage.Types import ConnectionInformation

from core.emu.GhostManager import GhostManager
from core.emu.MessageManager import MessageManager
from core.emu.PlayerManager import PlayerManager
from core.emu.ReplayManager import ReplayManager
from core.emu.SOSManager import SOSManager
from core.Util import *

class Server:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Server, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        self._packet_logging = Config().get_flag("packet_logging")
        self._packet_logger = logging.getLogger(__name__)
        self._packet_logger.setLevel(logging.DEBUG)
        self._packet_logger.addHandler(logging.FileHandler(filename='packetlog.log'))
        
        self.GhostManager = GhostManager()
        self.MessageManager = MessageManager()
        self.SOSManager = SOSManager()
        self.PlayerManager = PlayerManager()
        self.ReplayManager = ReplayManager()
        self.Admin = Admin()
        self.players:dict[str,ConnectionInformation] = {}
    
    def log_packet(self,request:Request):
        if(self._packet_logging):
            self._packet_logger.debug("%r %r",request.headers,request.get_data())
    
    def des_api(bootstrap:bool = False):
        def _des_api(f):
            @wraps(f)
            def __des_api(*args, **kwargs):
                _bootstrap = bootstrap
                
                Server().log_packet(request)
                
                body = decrypt(request.get_data())
                if(body is None):
                    logging.warn(f"Non DeS Request Sent To DeS Endpoint {request.url}")
                    return "You Shouldn't Be Here",401
                
                request.args = get_params(body)
                
                command,data = f(*args, **kwargs)
                
                data = convert_to_bytearray(data)
                
                if(not _bootstrap):
                    data = chr(command).encode() + struct.pack("<I", len(data) + 5) + data
                    
                encoded = convert_to_bytearray(base64.b64encode(data))
                
                if(not _bootstrap):
                    encoded += b'\n'
                
                return encoded,200
            return __des_api
        return _des_api
    
    @FC().route('/<info_endpoint>/ss.info', methods=['POST'])
    @des_api(bootstrap=True)
    def bootstrap(info_endpoint):
        uuid4 = str(uuid.uuid4())
        logging.debug(f"{request.remote_addr}|{uuid4} requested ss.info on {info_endpoint}")
        return 0x00,Config().get_info_ss(uuid4)
    
    @FC().route('/<region>/<uuid4>/login.spd', methods=['POST'])
    @des_api()
    def login(region:str,uuid4:str):
        self = Server()
        logging.debug(f"login {request.args}")
        #the zero isn't here for some reason but ok
        characterID = request.args.get("NPID") + "0"
        
        #
        match(self.Admin.update_player_data_and_check_banned(request.remote_addr,characterID)):
            case 'banned':
                return 0x02, b"\x03\x00"
            case 'new':
                return 0x02, b"\x00\x00"
        
        
        #      
        motd_output:str = ""
        motds:list = []
        perosnal_motd = self.Admin.get_player_specific_motd(characterID)
        if(perosnal_motd is not None):
            motds.append(perosnal_motd)
        motds += self.Admin.get_motd_list()
        for motd in motds:
            motd_output += self.Admin.render_motd(characterID,region,motd[0],self.GhostManager) + "\x00"
            
        
             
        # first byte
        # 0x00 - present EULA, create account (not working)
        # 0x01 - present MOTD, can be multiple
        # 0x02 - "Your account is currently suspended."
        # 0x03 - "Your account has been banned."
        # 0x05 - undergoing maintenance
        # 0x06 - online service has been terminated
        # 0x07 - network play cannot be used with this version
        
        return 0x02, b"\x01" + len(motds).to_bytes(1,'big') + bytearray(motd_output,encoding="UTF-8")
    
    @FC().route('/<region>/<uuid4>/getAgreement.spd', methods=['POST'])
    @des_api()
    def getAgreement(region,uuid4:str):
        logging.debug(f"{region} getAgreement {request.args}")
        characterID = request.args.get("NPID") + "0"
        self = Server()
        tos = self.Admin.get_player_specific_motd("tos")
        if(tos is None):
            tos = ["Be Nice\r\nNo Cheating"]
        return 0x01, "\x01\x01" + self.Admin.render_motd(characterID,region,tos[0],self.GhostManager) + "\x00"
    
    @FC().route('/<region>/<uuid4>/addNewAccount.spd', methods=['POST'])
    @des_api()
    def addNewAccount(region,uuid4:str):
        logging.debug(f"{region} addNewAccount {request.args}")
        characterID = request.args.get("NPID") + "0"
        #the response needs to be at least two bytes and the last being \x00
        res = characterID + "\x00"
        #any command works?
        return 0x00, res
    
    @FC().route('/<region>/<uuid4>/initializeCharacter.spd', methods=['POST'])
    @des_api()
    def initializeCharacter(region,uuid4:str):
        self = Server()
        cmd, data, characterID = self.PlayerManager.handle_initializeCharacter(request.args)
        self.players[uuid4] = ConnectionInformation(uuid4,characterID,request.remote_addr,region)
        return cmd,data
    
    @FC().route('/<region>/<uuid4>/getQWCData.spd', methods=['POST'])
    @des_api()
    def getQWCData(region,uuid4:str):
        self = Server()
        characterID = self.players.get(uuid4).get_npid()
        return self.PlayerManager.handle_getQWCData(request.args, characterID)
    
    @FC().route('/<region>/<uuid4>/addQWCData.spd', methods=['POST'])
    @des_api()
    def addQWCData(region,uuid4:str):
        logging.debug(f"ADDQWC {request.args}")
        return 0x09, "\x01"
    
    @FC().route('/<region>/<uuid4>/getMultiPlayGrade.spd', methods=['POST'])
    @des_api()
    def getMultiPlayGrade(region,uuid4:str):
        self = Server()
        return self.PlayerManager.handle_getMultiPlayGrade(request.args)
    
    @FC().route('/<region>/<uuid4>/getBloodMessageGrade.spd', methods=['POST'])
    @des_api()
    def getBloodMessageGrade(region,uuid4:str):
        self = Server()
        return self.PlayerManager.handle_getBloodMessageGrade(request.args)
    
    @FC().route('/<region>/<uuid4>/getTimeMessage.spd', methods=['POST'])
    @des_api()
    def getTimeMessage(region,uuid4:str):
        # first byte
        # 0x00 - nothing
        # 0x01 - undergoing maintenance
        # 0x02 - online service has been terminated

        return 0x22, "\x00\x00\x00"
    
    @FC().route('/<region>/<uuid4>/getBloodMessage.spd', methods=['POST'])
    @des_api()
    def getBloodMessage(region,uuid4:str):
        self = Server()
        return self.MessageManager.handle_getBloodMessage(request.args)
    
    @FC().route('/<region>/<uuid4>/addBloodMessage.spd', methods=['POST'])
    @des_api()
    def addBloodMessage(region,uuid4:str):
        self = Server()
        return self.MessageManager.handle_addBloodMessage(request.args)
    
    @FC().route('/<region>/<uuid4>/updateBloodMessageGrade.spd', methods=['POST'])
    @des_api()
    def updateBloodMessageGrade(region,uuid4:str):        
        self = Server()
        return self.MessageManager.handle_updateBloodMessageGrade(request.args)
    
    @FC().route('/<region>/<uuid4>/deleteBloodMessage.spd', methods=['POST'])
    @des_api()
    def deleteBloodMessage(region,uuid4:str):
        self = Server()
        return self.MessageManager.handle_deleteBloodMessage(request.args)
        
    @FC().route('/<region>/<uuid4>/getReplayList.spd', methods=['POST'])
    @des_api()
    def getReplayList(region,uuid4:str):
        self = Server()
        return self.ReplayManager.handle_getReplayList(request.args)
    
    @FC().route('/<region>/<uuid4>/getReplayData.spd', methods=['POST'])
    @des_api()
    def getReplayData(region,uuid4:str):
        self = Server()
        return self.ReplayManager.handle_getReplayData(request.args)
    
    @FC().route('/<region>/<uuid4>/addReplayData.spd', methods=['POST'])
    @des_api()
    def addReplayData(region,uuid4:str):
        self = Server()
        return self.ReplayManager.handle_addReplayData(request.args)
    
    @FC().route('/<region>/<uuid4>/getWanderingGhost.spd', methods=['POST'])
    @des_api()
    def getWanderingGhost(region,uuid4:str):
        self = Server()
        return self.GhostManager.handle_getWanderingGhost(request.args)
    
    @FC().route('/<region>/<uuid4>/setWanderingGhost.spd', methods=['POST'])
    @des_api()
    def setWanderingGhost(region,uuid4:str):
        self = Server()
        return self.GhostManager.handle_setWanderingGhost(request.args, region)
    
    @FC().route('/<region>/<uuid4>/getSosData.spd', methods=['POST'])
    @des_api()
    def getSosData(region,uuid4:str):            
        self = Server()
        #
        return self.SOSManager.handle_getSosData(request.args, region)
    
    @FC().route('/<region>/<uuid4>/addSosData.spd', methods=['POST'])
    @des_api()
    def addSosData(region,uuid4:str):             
        self = Server()
        #
        return self.SOSManager.handle_addSosData(request.args, region)
    
    @FC().route('/<region>/<uuid4>/checkSosData.spd', methods=['POST'])
    @des_api()
    def checkSosData(region,uuid4:str):            
        self = Server()
        #
        return self.SOSManager.handle_checkSosData(request.args, region)
    
    @FC().route('/<region>/<uuid4>/outOfBlock.spd', methods=['POST'])
    @des_api()
    def outOfBlock(region,uuid4:str):             
        self = Server()
        #
        return self.SOSManager.handle_outOfBlock(request.args, region)
    
    @FC().route('/<region>/<uuid4>/summonOtherCharacter.spd', methods=['POST'])
    @des_api()
    def summonOtherCharacter(region,uuid4:str):              
        self = Server()
        #
        characterID = self.players.get(uuid4).get_npid()
        return self.SOSManager.handle_summonOtherCharacter(request.args, region, characterID)
    
    @FC().route('/<region>/<uuid4>/summonBlackGhost.spd', methods=['POST'])
    @des_api()
    def summonBlackGhost(region,uuid4:str):            
        self = Server()
        #
        characterID = self.players.get(uuid4).get_npid()
        return self.SOSManager.handle_summonBlackGhost(request.args, region, characterID)
    
    @FC().route('/<region>/<uuid4>/initializeMultiPlay.spd', methods=['POST'])
    @des_api()
    def initializeMultiPlay(region,uuid4:str):              
        self = Server()
        return self.PlayerManager.handle_initializeMultiPlay(request.args)
    
    @FC().route('/<region>/<uuid4>/finalizeMultiPlay.spd', methods=['POST'])
    @des_api()
    def finalizeMultiPlay(region,uuid4:str):              
        self = Server()
        return self.PlayerManager.handle_finalizeMultiPlay(request.args)
    
    @FC().route('/<region>/<uuid4>/updateOtherPlayerGrade.spd', methods=['POST'])
    @des_api()
    def updateOtherPlayerGrade(region,uuid4:str):             
        self = Server()
        characterID = self.players.get(uuid4).get_npid()
        return self.PlayerManager.handle_updateOtherPlayerGrade(request.args, characterID)
    
    # #any rouge endpoint calls should appear here
    # @FC().route('/', defaults={'path': ''}, methods=['POST'])
    # @FC().route('/<path:path>', methods=['POST'])
    # @des_api()
    # def catch_all(path):
    #     #logging.error(f"Unknown Endpoint Called! Region:{region} Endpoint:{endpoint} Args:{request.args}")
    #     logging.error(f"UNK {path}")
    #     return 0x01, "\x01\x01catch_all\r\n\x00"