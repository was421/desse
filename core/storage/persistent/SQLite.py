from core.storage.StorageModel import StorageModel
from core.storage.Types import Replay,SOSData,Player,Message,Ghost,ActiveConnection
from core.Util import *
import sqlite3,struct

class SQLite(StorageModel):
    
    def __init__(self) -> None:
        super().__init__()
        self.conn = sqlite3.connect('db/core.sqlite',check_same_thread=False)
        self._make_messages_db()
        self._make_player_db()
        self._make_replay_db()
    
    def _make_replay_db(self):
        self.conn.execute("""create table IF NOT EXISTS replays(
                ghostID integer primary key autoincrement,
                characterID text,
                blockID integer,
                posx real,
                posy real,
                posz real,
                angx real,
                angy real,
                angz real,
                messageID integer,
                mainMsgID integer,
                addMsgCateID integer,
                replayBinary text,
                legacy integer)""")
        self.conn.commit()
        res = self.conn.execute("SELECT COUNT(*) FROM replays").fetchone()
        if res[0] == 0:
            f = open("data/legacyreplaydata.bin", "rb")
            while True:
                data = f.read(4)
                if len(data) == 0:
                    break
                sz = struct.unpack("<I", data)[0]
                
                rep = Replay()
                rep.unserialize(f.read(sz))
                        
                self.conn.execute("insert into replays(ghostID, characterID, blockID, posx, posy, posz, angx, angy, angz, messageID, mainMsgID, addMsgCateId, replayBinary, legacy) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rep.to_db_row())
            f.close()
            self.conn.commit()
            
    def _make_messages_db(self):
        self.conn.execute("""create table IF NOT EXISTS messages(
            bmID integer primary key autoincrement,
            characterID text,
            blockID integer,
            posx real,
            posy real,
            posz real,
            angx real,
            angy real,
            angz real,
            messageID integer,
            mainMsgID integer,
            addMsgCateID integer,
            rating integer,
            legacy integer)""")
        self.conn.commit()
        res = self.conn.execute("SELECT COUNT(*) FROM messages").fetchone()
        if res[0] == 0:
            f = open("data/legacymessagedata.bin", "rb")
            while True:
                data = f.read(4)
                if len(data) == 0:
                    break
                sz = struct.unpack("<I", data)[0]
                
                msg = Message()
                msg.unserialize(f.read(sz))
                        
                self.conn.execute("insert into messages(bmID, characterID, blockID, posx, posy, posz, angx, angy, angz, messageID, mainMsgID, addMsgCateId, rating, legacy) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", msg.to_db_row())
            f.close()   
            self.conn.commit()
    
    def _make_player_db(self):
        self.conn.execute("""create table IF NOT EXISTS players(
                characterID text primary key,
                gradeS integer,
                gradeA integer,
                gradeB integer,
                gradeC integer,
                gradeD integer,
                numsessions integer,
                messagerating integer,
                desired_tendency integer)""")  
        self.conn.commit()
                 
    #Replay Data-Normally Persistent-------------------------------------------
    def replay_store(self, replay:Replay) -> int:
        c = self.conn.cursor()
        c.execute("insert into replays(characterID, blockID, posx, posy, posz, angx, angy, angz, messageID, mainMsgID, addMsgCateId, replayBinary, legacy) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", replay.to_db_row()[1:])
        self.conn.commit()
        return c.lastrowid
        
    def replay_fetch_specific(self,ghostID:int) -> Replay | None:
        replay = Replay()
        results = self.conn.execute("select * from replays where ghostID = ?", (ghostID,)).fetchone()
        if(results is None):
            return None
        replay.from_db_row(results)
        return replay
    
    def replay_fetch_list(self,blockID:int,replayNum:int,legacy:bool = False) -> list[Replay]:
        res:list[Replay] = []
        for row in self.conn.execute("select * from replays where blockID = ? and legacy = ? order by random() limit ?", (blockID, int(legacy),replayNum)):
            rep = Replay()
            rep.from_db_row(row)
            res.append(rep)
        return res
    #--------------------------------------------------------------------------
    
    #SOS-Normally Volatile-----------------------------------------------------
    def sos_fetch_index(self) -> int:
        not_implemented()
    
    def sos_store(self,region:str,sos_data:SOSData):
        not_implemented()
    
    def sos_remove(self,region:str,characterID:str):
        not_implemented()
    
    def sos_fetch(self,region:str,characterID:str) -> SOSData | None:
        not_implemented()
    
    def sos_fetch_all_in_region(self,region:str) -> list[SOSData]:
        not_implemented()
    
    #Summons
    def sos_fetch_pending_player_num(self,region:str) -> int:
        not_implemented()
    
    def sos_fetch_pending_player(self,characterID:str) -> str | None: #returns NPRoomID
        not_implemented()
    
    def sos_remove_pending_player(self,characterID:str):
        not_implemented()
    
    def sos_store_pending_player(self,characterID:str,nproomid:str):
        not_implemented()
    
    #Monk
    def sos_fetch_pending_monk_num(self,region:str) -> int:
        not_implemented()
    
    def sos_fetch_pending_monk(self,region:str,characterID:str) -> str | None: #returns NPRoomID
        not_implemented()
    
    def sos_remove_pending_monk(self,region:str,characterID:str):
        not_implemented()
    
    def sos_store_pending_monk(self,region:str,characterID:str,nproomid:str):
        not_implemented()
    #--------------------------------------------------------------------------
    
    #Player-Normally Persistent------------------------------------------------
    def player_fetch(self,characterID:str) -> Player | None:
        result = self.conn.execute("select * from players where characterID = ?", (characterID,)).fetchone()
        if result is None:
            return None
        player = Player()
        player.from_tuple(result)
        return player
        
    def player_store(self,player:Player):
        self.conn.execute("replace into players(characterID, gradeS, gradeA, gradeB, gradeC, gradeD, numsessions, messagerating, desired_tendency) VALUES (?,?,?,?,?,?,?,?,?)", player.as_tuple())
        self.conn.commit()
    #--------------------------------------------------------------------------
    
    #Message-Normally Persistent-----------------------------------------------
    def message_fetch(self,blood_message_id:int) -> Message | None:
        row = self.conn.execute("select * from messages where bmID = ?", (blood_message_id,)).fetchone()
        if row is None:
            return None
        msg = Message()
        msg.from_db_row(row)
        return msg
        
    def message_store(self,msg:Message) -> int:
        c = self.conn.cursor()
        c.execute("replace into messages(characterID, blockID, posx, posy, posz, angx, angy, angz, messageID, mainMsgID, addMsgCateId, rating, legacy) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", msg.to_db_row()[1:])
        self.conn.commit()
        return c.lastrowid
    
    def message_remove(self,blood_message_id:int):
        self.conn.execute("delete from messages where bmID = ?", (blood_message_id,))
        self.conn.commit()
        
    def message_fetch_list(self,characterID:str, blockID:int, n_many:int,exclude_self:bool = False,legacy:bool = False) -> list[Message]:
        resp:list[Message] = []
        
        if(exclude_self):
            res = self.conn.execute("select * from messages where characterID != ? and blockID = ? and legacy = ? order by random() limit ?", (characterID, blockID, int(legacy),n_many))
        else:
            res = self.conn.execute("select * from messages where characterID = ? and blockID = ? and legacy = ? order by random() limit ?", (characterID, blockID, int(legacy),n_many))
        
        for row in res:
            msg = Message()
            msg.from_db_row(row)
            resp.append(msg)
        
        return resp
            
    #--------------------------------------------------------------------------
    
    #Ghost-Normally Volatile---------------------------------------------------
    def ghost_fetch(self,characterID:str) -> Ghost | None:
        not_implemented()
    
    def ghost_store(self,ghost:Ghost):
        not_implemented()
    
    def ghost_remove(self,characterID:str):
        not_implemented()
        
    def ghost_fetch_all(self) -> list[Ghost]:
        not_implemented()
    #--------------------------------------------------------------------------
    
    #ActiveConnection-Normally Volatile----------------------------------------
    def active_connection_store(self,active_connection:ActiveConnection):
        not_implemented()
    
    def active_connection_fetch(self,uuid4:str) -> ActiveConnection | None:
        not_implemented()
    
    def active_connection_remove(self,uuid4:str):
        not_implemented()
    
    def active_connection_fetch_all(self) -> list[ActiveConnection]:
        not_implemented()
    #--------------------------------------------------------------------------