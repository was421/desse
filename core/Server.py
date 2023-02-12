from flask import Flask, request, Response
from functools import wraps
from waitress import serve

import threading,base64,struct

from core.Config import Config


from emu.GhostManager import *
from emu.MessageManager import *
from emu.PlayerManager import *
from emu.ReplayManager import *
from emu.SOSManager import *
from emu.Util import *

class FC:
    f:Flask
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FC, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        self.f = Flask(__name__)
    
    def start_daemon(self):
        threading.Thread(target=lambda: serve(self.f,host='0.0.0.0',port=18000),daemon=True).start()
        
    def start_blocking(self):
        serve(self.f,host='0.0.0.0',port=18000)
    
class Server:
    name:str = "BACON"
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
    
    def start(self):
        FC().start_blocking()
    
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
    
    @FC().f.route('/demons-souls-us/ss.info', methods=['POST'])
    @des_api(bootstrap=True)
    def bootstrap():
        return 0x00,Config().get_info_ss()
    
    @FC().f.route('/<region>/login.spd', methods=['POST'])
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
    
    @FC().f.route('/<region>/initializeCharacter.spd', methods=['POST'])
    @des_api()
    def initializeCharacter(region):
        self = Server()
        cmd, data, characterID = self.PlayerManager.handle_initializeCharacter(request.args)
        self.players[request.remote_addr] = characterID
        return cmd,data
    
    @FC().f.route('/<region>/getQWCData.spd', methods=['POST'])
    @des_api()
    def getQWCData(region):
        self = Server()
        characterID = self.players[request.remote_addr]
        return self.PlayerManager.handle_getQWCData(request.args, characterID)
    
    @FC().f.route('/<region>/addQWCData.spd', methods=['POST'])
    @des_api()
    def addQWCData(region):
        return 0x09, "\x01"
    
    @FC().f.route('/<region>/getMultiPlayGrade.spd', methods=['POST'])
    @des_api()
    def getMultiPlayGrade(region):
        self = Server()
        return self.PlayerManager.handle_getMultiPlayGrade(request.args)
    
    @FC().f.route('/<region>/getBloodMessageGrade.spd', methods=['POST'])
    @des_api()
    def getBloodMessageGrade(region):
        self = Server()
        return self.PlayerManager.handle_getBloodMessageGrade(request.args)
    
    @FC().f.route('/<region>/getTimeMessage.spd', methods=['POST'])
    @des_api()
    def getTimeMessage(region):
        # first byte
        # 0x00 - nothing
        # 0x01 - undergoing maintenance
        # 0x02 - online service has been terminated

        return 0x22, "\x00\x00\x00"
    
    @FC().f.route('/<region>/getAgreement.spd', methods=['POST'])
    @FC().f.route('/<region>/addNewAccount.spd', methods=['POST'])
    @des_api()
    def getUnusedEndpoint(region):
        return 0x01, "\x01\x01Hello!!\r\n\x00"
    
    @FC().f.route('/<region>/getBloodMessage.spd', methods=['POST'])
    @des_api()
    def getBloodMessage(region):
        self = Server()
        return self.MessageManager.handle_getBloodMessage(request.args)
    
    @FC().f.route('/<region>/addBloodMessage.spd', methods=['POST'])
    @des_api()
    def addBloodMessage(region):
        self = Server()
        cmd, data, custom_command = self.MessageManager.handle_addBloodMessage(request.args)
        return cmd, data
    
    @FC().f.route('/<region>/updateBloodMessageGrade.spd', methods=['POST'])
    @des_api()
    def updateBloodMessageGrade(region):         
        self = Server()
        return self.MessageManager.handle_updateBloodMessageGrade(request.args, self)
    
    @FC().f.route('/<region>/deleteBloodMessage.spd', methods=['POST'])
    @des_api()
    def deleteBloodMessage(region):
        self = Server()
        return self.MessageManager.handle_deleteBloodMessage(request.args)
        
    @FC().f.route('/<region>/getReplayList.spd', methods=['POST'])
    @des_api()
    def getReplayList(region):
        self = Server()
        return self.ReplayManager.handle_getReplayList(request.args)
    
    @FC().f.route('/<region>/getReplayData.spd', methods=['POST'])
    @des_api()
    def getReplayData(region):
        self = Server()
        return self.ReplayManager.handle_getReplayData(request.args)
    
    @FC().f.route('/<region>/addReplayData.spd', methods=['POST'])
    @des_api()
    def addReplayData(region):
        self = Server()
        return self.ReplayManager.handle_addReplayData(request.args)
    
    @FC().f.route('/<region>/getWanderingGhost.spd', methods=['POST'])
    @des_api()
    def getWanderingGhost(region):
        self = Server()
        return self.GhostManager.handle_getWanderingGhost(request.args)
    
    @FC().f.route('/<region>/setWanderingGhost.spd', methods=['POST'])
    @des_api()
    def setWanderingGhost(region):
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.GhostManager.handle_setWanderingGhost(request.args, serverport)
    
    @FC().f.route('/<region>/getSosData.spd', methods=['POST'])
    @des_api()
    def getSosData(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_getSosData(request.args, serverport)
    
    @FC().f.route('/<region>/addSosData.spd', methods=['POST'])
    @des_api()
    def addSosData(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_addSosData(request.args, serverport, self)
    
    @FC().f.route('/<region>/checkSosData.spd', methods=['POST'])
    @des_api()
    def checkSosData(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_checkSosData(request.args, serverport)
    
    @FC().f.route('/<region>/outOfBlock.spd', methods=['POST'])
    @des_api()
    def outOfBlock(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        return self.SOSManager.handle_outOfBlock(request.args, serverport)
    
    @FC().f.route('/<region>/summonOtherCharacter.spd', methods=['POST'])
    @des_api()
    def summonOtherCharacter(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        characterID = self.players[request.remote_addr]
        return self.SOSManager.handle_summonOtherCharacter(request.args, serverport, characterID)
    
    @FC().f.route('/<region>/summonBlackGhost.spd', methods=['POST'])
    @des_api()
    def summonBlackGhost(region):              
        self = Server()
        serverport = SERVER_TO_PORT[region]
        characterID = self.players[request.remote_addr]
        return self.SOSManager.handle_summonBlackGhost(request.args, serverport, characterID)
    
    @FC().f.route('/<region>/initializeMultiPlay.spd', methods=['POST'])
    @des_api()
    def initializeMultiPlay(region):              
        self = Server()
        return self.PlayerManager.handle_initializeMultiPlay(request.args)
    
    @FC().f.route('/<region>/finalizeMultiPlay.spd', methods=['POST'])
    @des_api()
    def finalizeMultiPlay(region):              
        self = Server()
        return self.PlayerManager.handle_finalizeMultiPlay(request.args)
    
    @FC().f.route('/<region>/updateOtherPlayerGrade.spd', methods=['POST'])
    @des_api()
    def updateOtherPlayerGrade(region):              
        self = Server()
        characterID = self.players[request.remote_addr]
        return self.PlayerManager.handle_updateOtherPlayerGrade(request.args, characterID)