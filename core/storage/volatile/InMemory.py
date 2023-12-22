from core.storage.StorageModel import StorageModel
from core.storage.Types import Replay,SOSData,Player,Message,Ghost,ActiveConnection
from core.Util import *

class InMemory(StorageModel):
    def __init__(self) -> None:
        super().__init__()
        #SOS-------------------------------------------------------------------
        self._sos_index:int = 0
        self._sos:dict[str,dict[str,SOSData]] = {}
        self._sos_pending_player:dict[str,str] = {}
        self._sos_pending_monk:dict[str,dict[str,str]] = {}
        #----------------------------------------------------------------------
        
        #Ghost-----------------------------------------------------------------
        self._ghost:dict[str:Ghost] = {}
        #----------------------------------------------------------------------
        
        #ActiveConnection------------------------------------------------------
        self._active_connection:dict[str:ActiveConnection] = {}
        #----------------------------------------------------------------------
        
        
    #Replay Data-Normally Persistent-------------------------------------------
    def replay_store(self, replay:Replay) -> int:
        not_implemented()
    
    def replay_fetch_specific(self,ghostID:int) -> Replay | None:
        not_implemented()
    
    def replay_fetch_list(self,blockID:int,replayNum:int,legacy:bool = False) -> list[Replay]:
        not_implemented()
    #--------------------------------------------------------------------------
    
    #SOS-Normally Volatile-----------------------------------------------------
    def sos_fetch_index(self) -> int:
        index = self._sos_index
        self._sos_index += 1
        return index
    
    def sos_store(self,region:str,sos_data:SOSData):
        if self._sos.get(region) is None:
            self._sos[region] = {}
        self._sos[region][sos_data.characterID] = sos_data
    
    def sos_remove(self,region:str,characterID:str):
        if self._sos.get(region) is None:
            self._sos[region] = {}
        if self._sos[region].get(characterID) is not None:
            del self._sos[region][characterID]
    
    def sos_fetch(self,region:str,characterID:str) -> SOSData | None:
        if self._sos.get(region) is None:
            self._sos[region] = {}
        return self._sos[region].get(characterID)
    
    def sos_fetch_all_in_region(self,region:str) -> list[SOSData]:
        res:list[SOSData] = []
        if(self._sos.get(region) is None):
            self._sos[region] = {}
        for sos in self._sos[region].values():
            res.append(sos)
        return res
            
    #Summons
    def sos_fetch_pending_player_num(self,region:str) -> int:
        return len(self._sos_pending_player)
    
    def sos_fetch_pending_player(self,characterID:str) -> str | None: #returns NPRoomID
        return self._sos_pending_player.get(characterID)
    
    def sos_remove_pending_player(self,characterID:str):
        if self._sos_pending_player.get(characterID) is not None:
            del self._sos_pending_player[characterID]
    
    def sos_store_pending_player(self,characterID:str,nproomid:str):
        self._sos_pending_player[characterID] = nproomid
    
    #Monk
    def sos_fetch_pending_monk_num(self,region:str) -> int:
        if self._sos_pending_monk.get(region) is None:
            self._sos_pending_monk[region] = {}
        return len(self._sos_pending_monk[region])
    
    def sos_fetch_pending_monk(self,region:str,characterID:str) -> str | None: #returns NPRoomID
        if self._sos_pending_monk.get(region) is None:
            self._sos_pending_monk[region] = {}
        return self._sos_pending_monk[region].get(characterID)
    
    def sos_remove_pending_monk(self,region:str,characterID:str):
        if self._sos_pending_monk.get(region) is None:
            self._sos_pending_monk[region] = {}
        if self._sos_pending_monk[region].get(characterID) is not None:
            del self._sos_pending_monk[region][characterID]
    
    def sos_store_pending_monk(self,region:str,characterID:str,nproomid:str):
        if self._sos_pending_monk.get(region) is None:
            self._sos_pending_monk[region] = {}
        self._sos_pending_monk[region][characterID] = nproomid
    #--------------------------------------------------------------------------
    
    #Player-Normally Persistent------------------------------------------------
    def player_fetch(self,characterID:str) -> Player | None:
        not_implemented()
        
    def player_store(self,player:Player):
        not_implemented()
    #--------------------------------------------------------------------------
    
    #Message-Normally Persistent-----------------------------------------------
    def message_fetch(self,blood_message_id:int) -> Message | None:
        not_implemented()
        
    def message_store(self,msg:Message) -> int:
        not_implemented()
        
    def message_remove(self,blood_message_id:int):
        not_implemented()
        
    def message_fetch_list(self,characterID:str, blockID:int, n_many:int,exclude_self:bool = False,legacy:bool = False) -> list[Message]:
        not_implemented()
    #--------------------------------------------------------------------------
    
    #Ghost-Normally Volatile---------------------------------------------------
    def ghost_fetch(self,characterID:str) -> Ghost | None:
        return self._ghost.get(characterID)
    
    def ghost_store(self,ghost:Ghost):
        self._ghost[ghost.characterID] = ghost
    
    def ghost_remove(self,characterID:str):
        if self._ghost.get(characterID):
            del self._ghost[characterID]
        
    def ghost_fetch_all(self) -> list[Ghost]:
        return list(self._ghost.values())
            
    #--------------------------------------------------------------------------
    
    #ActiveConnection-Normally Volatile----------------------------------------
    def active_connection_store(self,active_connection:ActiveConnection):
        self._active_connection[active_connection._connection_uuid4] = active_connection
    
    def active_connection_fetch(self,uuid4:str) -> ActiveConnection | None:
        return self._active_connection.get(uuid4)
    
    def active_connection_remove(self,uuid4:str):
        if self._active_connection.get(uuid4) is not None:
            del self._active_connection[uuid4]
    
    def active_connection_fetch_all(self) -> list[ActiveConnection]:
        return list(self._active_connection.values())
    #--------------------------------------------------------------------------