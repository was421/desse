import tomllib, logging, socket, urllib.request, os, traceback

class Config:
    CONFIG_FILE_NAME:str = "desse_config.toml"
    _conf:dict
    _STATUS_SERVER:bytes = None
    _STATUS_SERVER_local:bytes = None
    _local_ip:str = None
    _public_ip:str = None
    _server_ip:str = None
    _server_port:int = None
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        try:
            try:
                file = open(self.CONFIG_FILE_NAME,"r")
                config_file = file.read()
                file.close()
                self._conf = tomllib.loads(config_file)
            except:
                pass
            
            self._map_environment()
            
        except Exception as e:
            logging.error(f"Cannot Load Config: {e}:{traceback.format_exc()}")
    
    def _string_to_key_dict(self,string:str) -> dict:
        if '..' in string:
            split = string.split('..')
            self._string_to_key_dict(''.join(split[1::]))
            string = split[0]
        key_depth = string.split('.')
        print(key_depth)
        frame = self._conf
        for k in key_depth[:-1]:
            if not isinstance(frame,dict):
                frame = {}
            if not isinstance(frame.get(k),dict):
                frame[k] = {}
            frame = frame[k]
        frame[key_depth[-1]] = 0
                
    def _map_environment(self):
        try:
            for key, value in os.environ.items():
                if '.' in key:
                    print(key)
                    key_depth = key.split('.')
                    print(key_depth)
                    frame = self._conf
                    for k in key_depth[:-1]:
                        if not isinstance(frame,dict):
                            frame = {}
                        if not isinstance(frame.get(k),dict):
                            frame[k] = {}
                        frame = frame[k]
                    frame[key_depth[-1]] = value    
                    
                    print("CONF -> ",self._conf[key_depth[0]])
        except Exception as e:
            logging.error(f"Env -> Dict: {e}:{traceback.format_exc()}")
       
    def get_flag(self,flag_name:str)->bool:
        value:dict = self.get_conf_dict("DESSE_FLAG")
        if(value is not None):
            try:
                ret = bool(value.get(flag_name))
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

        match(log_conf.get("LOG_LEVEL")):
            case "DEBUG":
                level = logging.DEBUG
            case "INFO":
                level = logging.INFO
            case "WARNING":
                level = logging.WARNING
            case "ERROR":
                level = logging.ERROR
        
        return level,log_conf.get("LOG_FILE")
        
    def get_local_ip(self)->str:
        if(self._local_ip is None):
            #this does not work on all machines
            self._local_ip = socket.gethostbyname(socket.gethostname())
        return self._local_ip
    
    def get_public_ip(self)->str:
        if(self._public_ip is None):
            #self._public_ip = urllib.request.urlopen('http://ident.me').read().decode('utf8')
            #this takes more work but i trust cloudflare more than whomever owns ident.me
            ret:str = urllib.request.urlopen('http://cloudflare.com/cdn-cgi/trace').read().decode('utf8')
            res:dict = {}
            for kv in ret.split('\n'):
                pair = kv.split('=')
                if len(pair) == 2:
                    res[pair[0]] = pair[1]
            self._public_ip = res.get('ip')
        return self._public_ip      
    
    def get_server_ip(self)->str:
        if self._server_ip is None:
            if self.get_flag("AUTOMATIC_IP_CONFIG"):
                self._server_ip = self.get_public_ip()
            else:
                server_conf = self.get_conf_dict("SERVER")
                self._server_ip = server_conf.get("IP")  
        return self._server_ip
    
    def get_server_port(self) -> int:
        if self._server_port is None:
            server_conf = self.get_conf_dict("SERVER")
            self._server_port = int(server_conf.get("PORT"))
        return self._server_port