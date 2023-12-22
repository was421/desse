from core.storage.StorageContainer import StorageContainer as SC
from core.storage.Types import Message
from core.PlayerCommands import PlayerCommands
from core.Util import *
import logging

class MessageManager(object):
    def __init__(self):
        pass
        
    def handle_getBloodMessage(self, params):
        characterID = params["characterID"]
        blockID = make_signed(int(params["blockID"]))
        replayNum = int(params["replayNum"])
        
        to_send = []
        
        # first own non-legacy messages
        remaining = replayNum
        num_own = 0
        for msg in SC().persistent.message_fetch_list(characterID,blockID,remaining):
            to_send.append(msg.serialize())
            num_own += 1
            
        # then others non-legacy messages
        remaining = replayNum - len(to_send)
        num_others = 0
        if remaining > 0:
            for msg in SC().persistent.message_fetch_list(characterID,blockID,remaining,exclude_self=True):
                to_send.append(msg.serialize())
                num_others += 1
            
        # then legacy messages
        remaining = replayNum - len(to_send)
        num_legacy = 0
        if (num_own + num_others) < LEGACY_MESSAGE_THRESHOLD and remaining > 0:
            for msg in SC().persistent.message_fetch_list(characterID,blockID,remaining,exclude_self=True,legacy=True):
                to_send.append(msg.serialize())
                num_legacy += 1
        
        res = struct.pack("<I", len(to_send)) + b"".join(to_send)
            
        logging.debug("Sending %d own messages, %d others messages and %d legacy messages for block %s" % (num_own, num_others, num_legacy, BLOCK_NAMES[blockID]))
        
        return 0x1f, res
        
    def handle_addBloodMessage(self, params):
        msg = Message()
        msg.from_params(params, None)
        
        #commands are never result in stored messages
        if PlayerCommands().injest_message(msg):
            return 0x1d, "\x01"
            
        #this only runs if the above was not a command, so most of the time 
        msg.bmID = SC().persistent.message_store(msg)
        logging.info("Added new message %s" % str(msg))
            
        return 0x1d, "\x01"
        
    def handle_deleteBloodMessage(self, params):
        bmID = int(params["bmID"])
        
        SC().persistent.message_remove(bmID)
        
        logging.info("Deleted message %s" % str(bmID))
        
        return 0x27, "\x01"
        
    def handle_updateBloodMessageGrade(self, params):
        bmID = int(params["bmID"])
        
        msg = SC().persistent.message_fetch(bmID)
        msg.rating =+ 1
        SC().persistent.message_store(msg)
        
        player  = SC().persistent.player_fetch(msg.characterID)
        if player is not None:
            player.messagerating +=1
            SC().persistent.player_store(player)
            logging.info("Updated blood message grade for player %r" % (msg.characterID))
        else:
            logging.warn("No Such Player %r" % msg.characterID)
        
        logging.info("Recommended message %s" % str(msg))
        
        return 0x2a, "\x01"
