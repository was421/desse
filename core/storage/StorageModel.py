from core.storage.Types import Replay,SOSData,Player,Message,Ghost
from core.Util import *
import logging


class StorageModel:
    
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
        not_implemented()
    
    def ghost_store(self,ghost:Ghost):
        not_implemented()
    
    def ghost_remove(self,characterID:str):
        not_implemented()
        
    def ghost_fetch_all(self) -> list[Ghost]:
        not_implemented()
    #--------------------------------------------------------------------------