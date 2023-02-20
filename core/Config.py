import json, logging, socket, urllib.request, uuid

class Config:
    CONFIG_FILE_NAME:str = "des_emu_config.json"
    #it needs to hard coded to this port b/c the game only looks there
    _server_port:int = 18000
    _conf:dict
    _info_ss:bytes = None
    _info_ss_local:bytes = None
    _local_ip:str = ""
    _public_ip:str = ""
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        try:
            config_file = open(self.CONFIG_FILE_NAME,"r").read()
            self._conf = json.loads(config_file)
            
            #this does not work on all machines
            self._local_ip = socket.gethostbyname(socket.gethostname())
            
            #self._public_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
            #this takes more work but i trust cloudflare more than whomever owns ident.me
            ret:str = urllib.request.urlopen('http://cloudflare.com/cdn-cgi/trace').read().decode('utf8')
            res:dict = {}
            for kv in ret.split('\n'):
                pair = kv.split('=')
                if len(pair) == 2:
                    res[pair[0]] = pair[1]
            self._public_ip = res.get('ip')
        except Exception as e:
            logging.error(f"Cannot Load Config: {e}")
         
    def get_flag(self,flag_name:str)->bool:
        value = self._conf.get(flag_name)
        if(value is not None):
            try:
                ret = bool(value)
                return ret
            except Exception as e:
                logging.warning(f"Requested flag {flag_name} isn't boolean, returning false: {e}")
                return False
        logging.warning(f"Requested flag {flag_name} does not exist, returning false: {e}")
        return False
    
    def get_conf_dict(self,dict_name:str) -> dict | None:
        value = self._conf.get(dict_name)
        if(value is not None):
            try:
                ret = dict(value)
                return ret
            except Exception as e:
                logging.warning(f"Requested config dict {dict_name} isn't a dict, returning None: {e}")
                return None
        logging.warning(f"Requested config dict {dict_name} does not exist, returning None: {e}")
        return None
    
    def get_logging_settings(self) -> tuple[int:str]:
        log_conf = self.get_conf_dict("LOGGING")
        level = logging.NOTSET

        match(log_conf.get("log_level")):
            case "DEBUG":
                level = logging.DEBUG
            case "INFO":
                level = logging.INFO
            case "WARNING":
                level = logging.WARNING
            case "ERROR":
                level = logging.ERROR
        
        return level,log_conf.get("log_file")
        
    def get_server_local_ip(self)->str:
        return self._local_ip
    
    def get_server_public_ip(self)->str:
        return self._public_ip      
    
    def get_server_port(self) -> int:
        return self._server_port
    
    def get_info_ss(self,uuid4:str,local:bool = False) -> bytes:

        if(self._info_ss is None):
            if self.get_flag("automatic_ip_config"):
                public_ip = self.get_server_public_ip()
            else:
                ss_conf = self.get_conf_dict("INFO_SS")
                public_ip = ""
                if(ss_conf is not None):
                    public_ip = ss_conf.get("ip")
                else:
                    public_ip = '0.0.0.0'
            template = b"""
            <ss>0</ss>
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
            <gameurl1>http://?ip?:18000/us/?uuid?/</gameurl1>
            <gameurl2>http://?ip?:18000/eu/?uuid?/</gameurl2>
            <gameurl3>http://?ip?:18000/jp/?uuid?/</gameurl3>
            <gameurl4>http://?ip?:18000/jp/?uuid?/</gameurl4>
            <gameurl5>http://?ip?:18000/eu/?uuid?/</gameurl5>
            <gameurl6>http://?ip?:18000/eu/?uuid?/</gameurl6>
            <gameurl7>http://?ip?:18000/eu/?uuid?/</gameurl7>
            <gameurl8>http://?ip?:18000/eu/?uuid?/</gameurl8>
            <gameurl11>http://?ip?:18000/jp/?uuid?/</gameurl11>
            <gameurl12>http://?ip?:18000/jp/?uuid?/</gameurl12>
            <browserurl1>http://?ip?:18000/unk_endpoint1/</browserurl1>
            <browserurl2>http://?ip?:18000/unk_endpoint2/</browserurl2>
            <browserurl3>http://?ip?:18000/unk_endpoint3/</browserurl3>
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
            self._info_ss = template.replace(b"?ip?",public_ip.encode())
            self._info_ss_local = template.replace(b"?ip?",self.get_server_local_ip().encode())
        if local:
            return self._info_ss_local.replace(b"?uuid?",uuid4.encode())
        return self._info_ss.replace(b"?uuid?",uuid4.encode())