from core.storage.StorageContainer import StorageContainer as SC
from core.storage.Types import Player
import logging,struct

class PlayerManager(object):
    def __init__(self):
        pass

    def _ensure_user_created(self, characterID):
        player = SC().persistent.player_fetch(characterID)
        if player is None:
            SC().persistent.player_store(Player(characterID))
            logging.info("Created new player %r" % characterID)
    
    def _debug_db_row(self, characterID):
        player = SC().persistent.player_fetch(characterID)
        logging.debug("Player info in db %r", player)
    
    def handle_initializeCharacter(self, params):
        characterID = params["characterID"]
        index = params["index"]
        characterID = characterID + index[0]
        
        self._ensure_user_created(characterID)
        logging.info("Player %r logged in" % characterID)
        
        self._debug_db_row(characterID)
        
        data = characterID + "\x00"
        return 0x17, data, characterID
        
    def handle_getQWCData(self, params, characterID):
        self._ensure_user_created(characterID)
        
        player = SC().persistent.player_fetch(characterID)
        
        data:bytearray = bytearray()
        for i in range(7):
            data += struct.pack("<ii", player.desired_tendency, 0)
            
        logging.debug("Player %r with desired tendency %d" % (player.characterID, player.desired_tendency))
        
        return 0x0e, data
    
    def handle_getMultiPlayGrade(self, params):
        characterID = params["NPID"]
        player = SC().persistent.player_fetch(characterID)
        ratings = player.get_stats()
        data:bytearray = bytearray()
        data += b"\x01"
        data += struct.pack("<iiiiii", *ratings)
        
        logging.debug("Player %r multiplayer stats %r" % (player.characterID, ratings))
        
        return 0x28, data
        
    def handle_getBloodMessageGrade(self, params):
        characterID = params["NPID"]
        self._ensure_user_created(characterID)
        
        player = SC().persistent.player_fetch(characterID)
        
        logging.debug("Player %r message rating %d" % (player.characterID, player.messagerating))
        
        data = bytearray()
        data += b"\x01"
        data += struct.pack("<i", player.messagerating)
        return 0x29, data
    
    def handle_initializeMultiPlay(self, params):
        characterID = params["characterID"]
        self._ensure_user_created(characterID)
        
        player = SC().persistent.player_fetch(characterID)
        player.numsessions += 1
        SC().persistent.player_store(player)

        logging.info("Player %r started a multiplayer session successfully" % characterID)
        
        self._debug_db_row(characterID)
        
        return 0x15, "\x01"
        
    def handle_finalizeMultiPlay(self, params):
        characterID = params["characterID"]
        self._ensure_user_created(characterID)
        
        player = SC().persistent.player_fetch(characterID)
        
        gradetext = "??no grade??"
        for key in ("gradeS", "gradeA", "gradeB", "gradeC", "gradeD"):
            if params[key] == "1":
                setattr(player,key,getattr(player,key)+1)
                gradetext = key
                SC().persistent.player_store(player)
                break
            
        logging.info("Player %r finished a multiplayer session successfully and received %s" % (characterID, gradetext))
        
        self._debug_db_row(characterID)
        
        return 0x21, "\x01"
        
    def handle_updateOtherPlayerGrade(self, params, myCharacterID):
        characterID = params["characterID"] + "0" # FOR SOME REASON ZERO ISN'T PRESENT HERE
        
        player = SC().persistent.player_fetch(characterID)
        
        key = ("gradeS", "gradeA", "gradeB", "gradeC", "gradeD")[int(params["grade"])]
        setattr(player,key,getattr(player,key)+1)
        
        SC().persistent.player_store(player)
  
        logging.info("Player %r gave player %r a %s rating" % (myCharacterID, characterID, key))
        
        self._debug_db_row(characterID)
        
        return 0x2b, "\x01"

