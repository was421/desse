from flask import request
from functools import wraps
import base64,struct

from core.Config import Config
from core.FlaskContainer import FlaskContainer as FC

from emu.GhostManager import *
from emu.MessageManager import *
from emu.PlayerManager import *
from emu.ReplayManager import *
from emu.SOSManager import *
from emu.Util import *
    
class Server:
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Server, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        self.text_conf = Config().get_conf_dict("TEXT")
        self.GhostManager = GhostManager()
        self.MessageManager = MessageManager()
        self.SOSManager = SOSManager()
        self.PlayerManager = PlayerManager()
        self.ReplayManager = ReplayManager()
        self.players = {}
    
    # this is an awful thing but it should get self working as the first param
    # def this():
    #     def _this(f):
    #         @wraps(f)
    #         def __this(*args, **kwargs):
    #             result = f(Server(),*args, **kwargs)
    #             print(result)
    #             return result
    #         return __this
    #     return _this
    
    def des_api(bootstrap:bool = False):
        def _des_api(f):
            @wraps(f)
            def __des_api(*args, **kwargs):
                
                request.args = get_params(decrypt(request.get_data()))
                
                command,data = f(*args, **kwargs)

                #if(not isinstance(data,bytes)):
                #    data = bytes(data,encoding='UTF-8')
                try:
                    data = bytearray(data)
                except:
                    data = bytearray(data,"UTF-8")
                
                if(not bootstrap):
                    data = chr(command).encode() + struct.pack("<I", len(data) + 5) + data
                    
                encoded = bytearray(base64.b64encode(data))
                
                if(not bootstrap):
                    encoded += b'\n'
                
                return encoded,200
            return __des_api
        return _des_api
    
    @FC().route('/<info_endpoint>/ss.info', methods=['POST'])
    @des_api(bootstrap=True)
    def bootstrap(info_endpoint):
        logging.debug(f"{request.remote_addr} requested ss.info on {info_endpoint}")
        return 0x00,Config().get_info_ss()
    
    @FC().route('/<region>/login.spd', methods=['POST'])
    @des_api()
    def login(region:str):
        self = Server()
        serverport = SERVER_TO_PORT[region]
        
        motd = self.text_conf.get("motd")
        
        regiontotal, blockslist = self.GhostManager.get_current_players(serverport)
        motd2  = "Current players online: %d\r\n" % sum(regiontotal.values())
        motd2 += "US %d  EU %d  JP %d\r\n" % (regiontotal[SERVER_PORT_US], regiontotal[SERVER_PORT_EU], regiontotal[SERVER_PORT_JP])
        motd2 += "Popular areas in your region:\r\n"
        for count, blockID in blockslist[::-1][0:5]:
             motd2 += "%4d %s\r\n" % (count, BLOCK_NAMES[blockID])
             
        # first byte
        # 0x00 - present EULA, create account (not working)
        # 0x01 - present MOTD, can be multiple
        # 0x02 - "Your account is currently suspended."
        # 0x03 - "Your account has been banned."
        # 0x05 - undergoing maintenance
        # 0x06 - online service has been terminated
        # 0x07 - network play cannot be used with this version
        
        return 0x02, bytes("\x01" + "\x02" + motd + "\x00" + motd2 + "\x00",encoding="UTF-8")
    
    @FC().route('/<region>/initializeCharacter.spd', methods=['POST'])
    @des_api()
    def initializeCharacter(region):
        self = Server()
        cmd, data, characterID = self.PlayerManager.handle_initializeCharacter(request.args)
        self.players[request.remote_addr] = characterID
        return cmd,data
    
    @FC().route('/<region>/getQWCData.spd', methods=['POST'])
    @des_api()
    def getQWCData(region):
        self = Server()
        characterID = self.players[request.remote_addr]
        return self.PlayerManager.handle_getQWCData(request.args, characterID)
    
    @FC().route('/<region>/addQWCData.spd', methods=['POST'])
    @des_api()
    def addQWCData(region):
        return 0x09, "\x01"
    
    @FC().route('/<region>/getMultiPlayGrade.spd', methods=['POST'])
    @des_api()
    def getMultiPlayGrade(region):
        self = Server()
        return self.PlayerManager.handle_getMultiPlayGrade(request.args)
    
    @FC().route('/<region>/getBloodMessageGrade.spd', methods=['POST'])
    @des_api()
    def getBloodMessageGrade(region):
        self = Server()
        return self.PlayerManager.handle_getBloodMessageGrade(request.args)
    
    @FC().route('/<region>/getTimeMessage.spd', methods=['POST'])
    @des_api()
    def getTimeMessage(region):
        # first byte
        # 0x00 - nothing
        # 0x01 - undergoing maintenance
        # 0x02 - online service has been terminated

        return 0x22, "\x00\x00\x00"
    
    @FC().route('/<region>/getAgreement.spd', methods=['POST'])
    @FC().route('/<region>/addNewAccount.spd', methods=['POST'])
    @des_api()
    def getUnusedEndpoint(region):
        return 0x01, "\x01\x01Hello!!\r\n\x00"
    
    @FC().route('/<region>/getBloodMessage.spd', methods=['POST'])
    @des_api()
    def getBloodMessage(region):
        self = Server()
        return self.MessageManager.handle_getBloodMessage(request.args)
    
    @FC().route('/<region>/addBloodMessage.spd', methods=['POST'])
    @des_api()
    def addBloodMessage(region):
        self = Server()
        cmd, data, custom_command = self.MessageManager.handle_addBloodMessage(request.args)
        return cmd, data
    
    @FC().route('/<region>/updateBloodMessageGrade.spd', methods=['POST'])
    @des_api()
    def updateBloodMessageGrade(region):         
        self = Server()
        return self.MessageManager.handle_updateBloodMessageGrade(request.args, self)
    
    @FC().route('/<region>/deleteBloodMessage.spd', methods=['POST'])
    @des_api()
    def deleteBloodMessage(region):
        self = Server()
        return self.MessageManager.handle_deleteBloodMessage(request.args)
        
    @FC().route('/<region>/getReplayList.spd', methods=['POST'])
    @des_api()
    def getReplayList(region):
        self = Server()
        return self.ReplayManager.handle_getReplayList(request.args)
    
    @FC().route('/<region>/getReplayData.spd', methods=['POST'])
    @des_api()
    def getReplayData(region):
        self = Server()
        return self.ReplayManager.handle_getReplayData(request.args)
    
    @FC().route('/<region>/addReplayData.spd', methods=['POST'])
    @des_api()
    def addReplayData(region):
        self = Server()
        return self.ReplayManager.handle_addReplayData(request.args)
    
    @FC().route('/<region>/getWanderingGhost.spd', methods=['POST'])
    @des_api()
    def getWanderingGhost(region):
        self = Server()
        return self.GhostManager.handle_getWanderingGhost(request.args)
    
    @FC().route('/<region>/setWanderingGhost.spd', methods=['POST'])
    @des_api()
    def setWanderingGhost(region):
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.GhostManager.handle_setWanderingGhost(request.args, serverport)
    
    @FC().route('/<region>/getSosData.spd', methods=['POST'])
    @des_api()
    def getSosData(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_getSosData(request.args, serverport)
    
    @FC().route('/<region>/addSosData.spd', methods=['POST'])
    @des_api()
    def addSosData(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_addSosData(request.args, serverport, self)
    
    @FC().route('/<region>/checkSosData.spd', methods=['POST'])
    @des_api()
    def checkSosData(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_checkSosData(request.args, serverport)
    
    @FC().route('/<region>/outOfBlock.spd', methods=['POST'])
    @des_api()
    def outOfBlock(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_outOfBlock(request.args, serverport)
    
    @FC().route('/<region>/summonOtherCharacter.spd', methods=['POST'])
    @des_api()
    def summonOtherCharacter(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        characterID = self.players[request.remote_addr]
        return self.SOSManager.handle_summonOtherCharacter(request.args, serverport, characterID)
    
    @FC().route('/<region>/summonBlackGhost.spd', methods=['POST'])
    @des_api()
    def summonBlackGhost(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        characterID = self.players[request.remote_addr]
        return self.SOSManager.handle_summonBlackGhost(request.args, serverport, characterID)
    
    @FC().route('/<region>/initializeMultiPlay.spd', methods=['POST'])
    @des_api()
    def initializeMultiPlay(region):              
        self = Server()
        return self.PlayerManager.handle_initializeMultiPlay(request.args)
    
    @FC().route('/<region>/finalizeMultiPlay.spd', methods=['POST'])
    @des_api()
    def finalizeMultiPlay(region):              
        self = Server()
        return self.PlayerManager.handle_finalizeMultiPlay(request.args)
    
    @FC().route('/<region>/updateOtherPlayerGrade.spd', methods=['POST'])
    @des_api()
    def updateOtherPlayerGrade(region):              
        self = Server()
        characterID = self.players[request.remote_addr]
        return self.PlayerManager.handle_updateOtherPlayerGrade(request.args, characterID)