import json, logging

class Config:
    CONFIG_FILE_NAME:str = "des_emu_config.json"
    _conf:dict
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance._setup()
        return cls.instance
    
    def _setup(self):
        try:
            config_file = open(self.CONFIG_FILE_NAME,"r").read()
            self._conf = json.loads(config_file)
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
    
    def get_info_ss(self) -> bytes:
        ss_conf = self.get_conf_dict("INFO_SS")
        iss_ip:str = ss_conf.get("ip")
        data = b"""
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
        <gameurl1>http://0.0.0.0:18000/us/</gameurl1>
        <gameurl2>http://0.0.0.0:18000/eu/</gameurl2>
        <gameurl3>http://0.0.0.0:18000/jp/</gameurl3>
        <gameurl4>http://0.0.0.0:18000/jp/</gameurl4>
        <gameurl5>http://0.0.0.0:18000/eu/</gameurl5>
        <gameurl6>http://0.0.0.0:18000/eu/</gameurl6>
        <gameurl7>http://0.0.0.0:18000/eu/</gameurl7>
        <gameurl8>http://0.0.0.0:18000/eu/</gameurl8>
        <gameurl11>http://0.0.0.0:18000/jp/</gameurl11>
        <gameurl12>http://0.0.0.0:18000/jp/</gameurl12>
        <browserurl1></browserurl1>
        <browserurl2></browserurl2>
        <browserurl3></browserurl3>
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
        """.replace(b"0.0.0.0",iss_ip.encode())
        return data