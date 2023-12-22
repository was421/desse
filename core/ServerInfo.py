import sqlite3,os,logging
from flask import render_template_string
from datetime import datetime,timedelta

from core.storage.StorageContainer import StorageContainer as SC
from core.storage.Types import ActiveConnection
from core.Config import Config
from core.Util import *


class ServerInfo:
    _render_ctx:dict = {}
    _tlast_update:datetime = None
    
    def __new__(cls):
      if not hasattr(cls, 'instance'):
          cls.instance = super(ServerInfo, cls).__new__(cls)
          cls.instance._setup()
      return cls.instance
    
    def _setup(self) -> None:
        self.conf = Config().get_conf_dict("SQLITE")
        dbfilename = self.conf["ADMIN_DB_PATH"]
        if not os.path.isfile(dbfilename):#TODO: move to StorageModel
            conn = sqlite3.connect(dbfilename)
            c = conn.cursor()
            c.execute("""create table player_data(
                characterID text primary key,
                ip text,
                last_login text,
                banned integer,
                mm_password text,
                slmm integer,
                rpcs3 integer)""")
            conn.commit()
            c.execute("""CREATE TABLE "motd" (
                        "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        "order"	INTEGER NOT NULL,
                        "motd"	INTEGER)""")
            conn.commit()
            
            conn.execute("insert into motd values(NULL,0,:MESSAGE)",
                      {'MESSAGE':"Welcome to Church Guard's test server!\r\nThis is a temporary server, it will\r\neventually be shut down.\r\n\r\nsource code:\r\nhttps://github.com/was421/desse\r\n"})
            conn.commit()
            
            c.execute("""create table player_motd(
                characterID text primary key,
                motd text)""")
            conn.commit()
            conn.execute("insert into player_motd values(:CHARACTERID,:MOTD)",{"CHARACTERID":"tos","MOTD":"Be Nice, No Cheating"})
            conn.commit()
            conn.close()
            
            logging.info("Created Admin database")
            
        self.conn = sqlite3.connect(dbfilename,check_same_thread=False)
    
    #Player Lookup
    def lookup_characterID_by_ip(self,ip:str)->list[str]:
        return self.conn.execute("select characterID from player_data where ip=:ip",ip).fetchall()
    
    def lookup_ip_by_characterID(self,characterID:str) -> str:
        return self.conn.execute("select ip from player_data where characterID=:characterID",characterID).fetchone()
    
    def create_player_data(self,ip:str,characterID:str):
        last_login = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        values ={}
        values['characterID'] = characterID
        values['ip'] = ip
        values['last_login'] = last_login
        values['banned'] = 0
        values['mm_password'] = ""
        values['slmm'] = 1
        values['rpcs3'] = 0
        self.conn.execute("insert into player_data values(:characterID,:ip,:last_login,:banned,:mm_password,:slmm,:rpcs3)",values)
        self.conn.commit()
          
    def update_player_data_and_check_banned(self,ip:str,characterID:str) -> str:
        rec = len(self.conn.execute("select characterID from player_data where characterID=:characterID limit 1",{'characterID':characterID}).fetchall())
        last_login = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        if(rec == 0):
            return 'new'
        self.conn.execute("update player_data SET ip=:ip,last_login=:last_login where characterID=:characterID",{'ip':ip,'last_login':last_login,'characterID':characterID})
        self.conn.commit()
        ret = self.conn.execute("select banned from player_data where characterID=:characterID limit 1",{'characterID':characterID}).fetchone()
        if(ret[0] > 0):
            return 'banned'
        return 'clear'
    
    def get_player_settings(self,characterID:str):
        return self.conn.execute("select mm_password,slmm,rpcs3 from player_data where characterID=:characterID",{'characterID':characterID}).fetchone()
    
    #MOTD
    def get_motd_list(self) -> list[tuple[str]]:
        return self.conn.execute('select motd from motd order by "order" asc').fetchall()
    
    def get_player_specific_motd(self,characterID) -> tuple[str] | None:
        return self.conn.execute('select motd from player_motd where characterID=:characterID limit 1',{'characterID':characterID}).fetchone()
    
    def render_motd(self,characterID:str,region:str,template:str,current_players_results:tuple[dict,list]) -> str:
        tnow = datetime.now()
        
        if(self._tlast_update is None or (tnow - self._tlast_update).total_seconds() > 5):
            self._render_ctx:dict = {}
            #STATIC Data
            self._render_ctx['STATIC'] = {'BLOCK_NAMES':BLOCK_NAMES}
            
            #players Data
            #{serverport:count} [(block:count)]             
            regiontotal, blockslist = current_players_results
            self._render_ctx['players'] = {'regiontotal':regiontotal,'blockslist':blockslist, 'total_players':sum(regiontotal.values())}
            
            #current_player
            #
            str().upper()
            settings = self.get_player_settings(characterID)
            self._render_ctx['current_player'] = {'settings':settings}
            
            #
        try:
            rendered =  render_template_string(template,**self._render_ctx)
        except Exception as e:
            rendered = ""
            logging.error(f"Failed To Render Message {e}")
            
        return rendered
    
    #Connections
    def create_active_connection(self,active_connection:ActiveConnection):
        SC().volatile.active_connection_store(active_connection)
    
    def update_connection_time(self,uuid4:str):
        ac = SC().volatile.active_connection_fetch(uuid4)
        if ac is not None:
            ac.update_time()
            SC().volatile.active_connection_store(ac)
    
    def get_active_connection(self,uuid4:str) -> ActiveConnection:
        return SC().volatile.active_connection_fetch(uuid4)
    
    def validate_all_connections(self):
        acl = SC().volatile.active_connection_fetch_all()
        for ac in acl:
            if ac._last_seen + timedelta(hours=1) < datetime.now():
                SC().volatile.active_connection_remove(ac)
         
    #recent connections
    def get_recent_connection(self,uuid4) -> ActiveConnection:
        pass
    
        