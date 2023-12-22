import logging,time

from core.storage.StorageContainer import StorageContainer as SC
from core.storage.Types import SOSData
from core.Util import *

class SOSManager(object):
    def __init__(self) -> None:
        pass

    def handle_getSosData(self, params, region:str):
        # TODO: limit number of SOS to what the client requests
        
        blockID = make_signed(int(params["blockID"]))
        sosNum = int(params["sosNum"])
        sosList = params["sosList"].split("a0a")
        sos_known = []
        sos_new = []
        
        for sos in SC().volatile.sos_fetch_all_in_region(region):
            if sos.updatetime + 30 < time.time():
                logging.info("Deleted SOS %r due to inactivity" % sos)
                SC().volatile.sos_remove(region,sos.get_characterID())
            else:
                if sos.blockID == blockID:
                    if str(sos.sosID) in sosList:
                        sos_known.append(struct.pack("<I", sos.sosID))
                        logging.debug("adding known SOS %d" % sos.sosID)
                    else:
                        sos_new.append(sos.serialize())
                        logging.debug("adding new SOS %d" % sos.sosID)
    
        data:bytearray = bytearray()
        data +=  struct.pack("<I", len(sos_known)) + b"".join(sos_known)
        data += struct.pack("<I", len(sos_new)) + b"".join(sos_new)
        
        return 0x0f, data

    def handle_addSosData(self, params, region:str):
        sos = SOSData(params, SC().volatile.sos_fetch_index())
        chr_str = sos.get_characterID()
        
        ratings = SC().persistent.player_fetch(chr_str).get_stats()
        sos.ratings = ratings[0:5]
        sos.totalsessions = ratings[5]
        
        SC().volatile.sos_store(region,sos)
        
        logging.info("added SOS %r %r" % (region, sos))
        return 0x0a, b"\x01"

    def handle_checkSosData(self, params, region:str):
        characterID = params["characterID"]
        
        sos = SC().volatile.sos_fetch(region,characterID)
        if sos is not None:
            sos.updatetime = time.time()
            SC().volatile.sos_store(sos)
            
        if SC().volatile.sos_fetch_pending_player_num(region) != 0 or SC().volatile.sos_fetch_pending_monk_num(region) != 0:
            logging.debug("Potential connect data pending players or monks")
        
        monk_nproomid = SC().volatile.sos_fetch_pending_monk(region,characterID)
        player_nproomid = SC().volatile.sos_fetch_pending_player(characterID)    
        if monk_nproomid is not None:
            logging.info("Summoning for monk player %r" % characterID)
            data = monk_nproomid
            SC().volatile.sos_remove_pending_monk(region,characterID)
            
        elif player_nproomid is not None:
            logging.info("Connecting player %r" % characterID)
            data = player_nproomid
            SC().volatile.sos_remove_pending_player(characterID)
            
        else:
            data = b"\x00"
                    
        return 0x0b, data
        
    def handle_summonOtherCharacter(self, params, region:str, playerid):
        ghostID = int(params["ghostID"])
        NPRoomID = params["NPRoomID"]
        logging.debug(f"NPRoomID: {NPRoomID}")
        logging.debug(f"Parsed NPRoomID {parse_nproomid(NPRoomID)}")
        logging.info("%r is attempting to summon id#%d" % (playerid, ghostID))
        
        for sos in SC().volatile.sos_fetch_all_in_region(region):
            if sos.sosID == ghostID:
                logging.info("%r adds pending request for summon %r" % (playerid, sos))
                SC().volatile.sos_store_pending_player(sos.get_characterID(),NPRoomID)
                return 0x0a, "\x01"
                
        logging.info("%r failed to summon, id#%d not present" % (playerid, ghostID))
        return 0x0a, "\x00"
            
    def handle_summonBlackGhost(self, params, region:str, playerid):
        NPRoomID = params["NPRoomID"]
        logging.debug(f"NPRoomID: {NPRoomID}")
        logging.debug(f"Parsed NPRoomID {parse_nproomid(NPRoomID)}")
        logging.info("%r is attempting to summon for monk" % playerid)
        
        
        for sos in SC().volatile.sos_fetch_all_in_region(region): 
            if sos.blockID in (40070, 40071, 40072, 40073, 40074, 40170, 40171, 40172, 40270):
                logging.info("%r adds pending request for monk %r" % (playerid, sos))
                SC().volatile.sos_store_pending_monk(region,sos.get_characterID(),NPRoomID)
                return 0x23, "\x01"
                
        logging.info("%r failed to summon for monk" % playerid)
        return 0x23, "\x00"
    
    def handle_outOfBlock(self, params, region:str):
        characterID = params["characterID"]
        sos = SC().volatile.sos_fetch(region,characterID)
        if sos is not None:
            logging.debug("removing old SOS %r" % sos.get_characterID())
            SC().volatile.sos_remove(region,sos.get_characterID())
            
        return 0x15, "\x01"