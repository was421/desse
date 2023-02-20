from core.storage.StorageContainer import StorageContainer as SC
from core.storage.Types import Ghost
from core.Util import *
import logging,struct,time,random

class GhostManager(object):
    def __init__(self):
        pass
        
    def _kill_stale_ghosts(self):
        current_time = time.time()

        for ghost in SC().volatile.ghost_fetch_all():
            if ghost.timestamp + 30.0 <= current_time:
                logging.debug("Deleted inactive ghost of %r" % ghost.characterID)
                SC().volatile.ghost_remove(ghost.characterID)
    
    def handle_getWanderingGhost(self, params):
        characterID = params["characterID"]
        blockID = make_signed(int(params["blockID"]))
        maxGhostNum = int(params["maxGhostNum"])
        
        self._kill_stale_ghosts()
        
        cands = []
        for ghost in SC().volatile.ghost_fetch_all():
            if ghost.ghostBlockID == blockID and ghost.characterID != characterID:
                cands.append(ghost)
                
        maxGhostNum = min(maxGhostNum, len(cands))
        
        res = convert_to_bytearray(struct.pack("<II", 0, maxGhostNum))
        ghost_cands:list[Ghost] =  random.sample(cands, maxGhostNum)
        for ghost in ghost_cands:
            replay = base64.b64encode(ghost.replayData).replace(b"+", b" ")
            res += struct.pack("<I", len(replay))
            res += replay

        return 0x11, res
        
    def handle_setWanderingGhost(self, params, region:str):
        characterID = params["characterID"]
        ghostBlockID = make_signed(int(params["ghostBlockID"]))
        replayData = decode_broken_base64(params["replayData"])
        
        # this is not strictly necessary, but it might help weed out bad ghosts that might otherwise crash the game
        if validate_replayData(replayData):
            ghost = Ghost(characterID, ghostBlockID, replayData)
            
            if characterID in SC().volatile.ghost_fetch_all():
                prevGhostBlockID = SC().volatile.ghost_fetch(characterID).ghostBlockID
                if ghostBlockID != prevGhostBlockID:
                    logging.debug("Player %r moved from %s to %s" % (characterID, BLOCK_NAMES[prevGhostBlockID], BLOCK_NAMES[ghostBlockID]))
            else:
                logging.debug("Player %r spawned into %s" % (characterID, BLOCK_NAMES[ghostBlockID]))
            
            ghost.region = region    
            SC().volatile.ghost_store(ghost)
        
        return 0x17, "\x01"
    
    def get_current_players(self, region:str):
        blocks = {}
        regiontotal = {}
        regiontotal[US_REGION] = 0
        regiontotal[EU_REGION] = 0
        regiontotal[JP_REGION] = 0
        
        self._kill_stale_ghosts()
        
        for ghost in SC().volatile.ghost_fetch_all():
            regiontotal[ghost.region] += 1
            
            if ghost.region == region:
                if ghost.ghostBlockID not in blocks:
                    blocks[ghost.ghostBlockID] = 0
                blocks[ghost.ghostBlockID] += 1
                
        blockslist = sorted((v, k) for (k, v) in blocks.items())
        logging.debug("Total players %r %r" % (regiontotal, blockslist))
        return regiontotal, blockslist
