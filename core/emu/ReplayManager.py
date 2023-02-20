import logging

from core.storage.StorageContainer import StorageContainer as SC
from core.storage.Types import Replay
from core.Util import *

class ReplayManager(object):
    
    def __init__(self) -> None:
        pass
        
    def handle_getReplayList(self, params):
        blockID = make_signed(int(params["blockID"]))
        replayNum = int(params["replayNum"])

        to_send = []
        
        # first non-legacy replays
        remaining = replayNum
        num_live = 0
        for row in SC().persistent.replay_fetch_list(blockID,remaining):
            row:Replay
            to_send.append(row.serialize_header())
            num_live += 1
        
        # then legacy replays
        remaining = replayNum - len(to_send)
        num_legacy = 0
        if num_live < LEGACY_REPLAY_THRESHOLD and remaining > 0:
            for row in SC().persistent.replay_fetch_list(blockID,remaining,1):
                row:Replay
                to_send.append(row.serialize_header())
                num_legacy += 1

        res = struct.pack("<I", len(to_send)) + b"".join(to_send)

        logging.debug("Sending %d live replays and %d legacy replays for block %s" % (num_live, num_legacy, BLOCK_NAMES[blockID]))
        
        return 0x1f, res
        
    def handle_addReplayData(self, params):
        rawReplay = decode_broken_base64(params["replayBinary"])
        
        if validate_replayData(rawReplay):
            rep = Replay()
            rep.from_params(params, None, rawReplay)
            rep.ghostID = SC().persistent.replay_store(rep)
            logging.info("Added new replay %s" % str(rep))

        return 0x1d, "\x01"
        
    def handle_getReplayData(self, params):
        ghostID = int(params["ghostID"])
        
        row = SC().persistent.replay_fetch_specific(ghostID)
        if row is None:
            logging.warning("Tried to read replayID %d data which does not exist" % ghostID)
            replayBinary = bytes()
        else:
            logging.info("Player requested info for replay %s" % row)
            replayBinary = convert_to_bytearray(row.replayBinary)

                
        res = convert_to_bytearray(struct.pack("<II", ghostID, len(replayBinary)) + replayBinary)
            
        return 0x1e, res