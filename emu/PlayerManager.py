import logging, os, sqlite3, struct

from core.Config import Config
from emu.Util import *

class PlayerManager(object):
    def __init__(self):
        self.conf = Config().get_conf_dict("SQLite")
        dbfilename = self.conf["players_db_path"]
        if not os.path.isfile(dbfilename):
            conn = sqlite3.connect(dbfilename)
            c = conn.cursor()
            c.execute("""create table players(
                characterID text primary key,
                gradeS integer,
                gradeA integer,
                gradeB integer,
                gradeC integer,
                gradeD integer,
                numsessions integer,
                messagerating integer,
                desired_tendency integer)""")
                
            conn.commit()
            conn.close()
            
            logging.info("Created user database")
            
        self.conn = sqlite3.connect(dbfilename)

    def ensure_user_created(self, characterID):
        row = self.conn.execute("select count(*) from players where characterID = ?", (characterID,)).fetchone()
        if row[0] == 0:
            self.conn.execute("insert into players(characterID, gradeS, gradeA, gradeB, gradeC, gradeD, numsessions, messagerating, desired_tendency) VALUES (?,?,?,?,?,?,?,?,?)", (characterID, 0, 0, 0, 0, 0, 0, 0, 0))
            self.conn.commit()
            logging.info("Created new player %r in database" % characterID)
    
    def debug_db_row(self, characterID):
        row = self.conn.execute("select * from players where characterID = ?", (characterID,)).fetchone()
        logging.debug("Player info in db %r", row)
    
    def handle_initializeCharacter(self, params):
        characterID = params["characterID"]
        index = params["index"]
        characterID = characterID + index[0]
        
        self.ensure_user_created(characterID)
        logging.info("Player %r logged in" % characterID)
        
        self.debug_db_row(characterID)
        
        data = characterID + "\x00"
        return 0x17, data, characterID
        
    def handle_getQWCData(self, params, characterID):
        self.ensure_user_created(characterID)
        
        row = self.conn.execute("select desired_tendency from players where characterID = ?", (characterID,)).fetchone()
        desired_tendency = row[0]
        
        data:bytearray = bytearray()
        for i in range(7):
            data += struct.pack("<ii", desired_tendency, 0)
            
        logging.debug("Player %r with desired tendency %d" % (characterID, desired_tendency))
        
        return 0x0e, data
    
    def handle_getMultiPlayGrade(self, params):
        characterID = params["NPID"]
        ratings = self.getPlayerStats(characterID)
        data:bytearray = bytearray()
        data += b"\x01"
        data += struct.pack("<iiiiii", *ratings)
        
        logging.debug("Player %r multiplayer stats %r" % (characterID, ratings))
        
        return 0x28, data
        
    def handle_getBloodMessageGrade(self, params):
        characterID = params["NPID"]
        self.ensure_user_created(characterID)
        
        row = self.conn.execute("select messagerating from players where characterID = ?", (characterID,)).fetchone()
        messagerating = row[0]
        
        logging.debug("Player %r message rating %d" % (characterID, messagerating))
        
        data = bytearray()
        data += b"\x01"
        data += struct.pack("<i", messagerating)
        return 0x29, data
    
    def handle_initializeMultiPlay(self, params):
        characterID = params["characterID"]
        self.ensure_user_created(characterID)
    
        self.conn.execute("update players set numsessions = numsessions + 1 where characterID = ?", (characterID,))
        self.conn.commit()
        
        logging.info("Player %r started a multiplayer session successfully" % characterID)
        
        self.debug_db_row(characterID)
        
        return 0x15, "\x01"
        
    def handle_finalizeMultiPlay(self, params):
        characterID = params["characterID"]
        self.ensure_user_created(characterID)
        
        gradetext = "??no grade??"
        for key in ("gradeS", "gradeA", "gradeB", "gradeC", "gradeD"):
            if params[key] == "1":
                self.conn.execute("update players set %s = %s + 1 where characterID = ?" % (key, key), (characterID,))
                self.conn.commit()
                gradetext = key
                break

        logging.info("Player %r finished a multiplayer session successfully and received %s" % (characterID, gradetext))
        
        self.debug_db_row(characterID)
        
        return 0x21, "\x01"
        
    def handle_updateOtherPlayerGrade(self, params, myCharacterID):
        characterID = params["characterID"] + "0" # FOR SOME REASON ZERO ISN'T PRESENT HERE
        
        key = ("gradeS", "gradeA", "gradeB", "gradeC", "gradeD")[int(params["grade"])]
        self.conn.execute("update players set %s = %s + 1 where characterID = ?" % (key, key), (characterID,))
        self.conn.commit()
        
        logging.info("Player %r gave player %r a %s rating" % (myCharacterID, characterID, key))
        
        self.debug_db_row(characterID)
        
        return 0x2b, "\x01"
    
    def getPlayerStats(self, characterID):
        self.ensure_user_created(characterID)
        return self.conn.execute("select gradeS, gradeA, gradeB, gradeC, gradeD, numsessions from players where characterID = ?", (characterID,)).fetchone()
        
    def updateBloodMessageGrade(self, characterID):
        c = self.conn.cursor()
        c.execute("update players set messagerating = messagerating + 1 where characterID = ?", (characterID,)).fetchone()
        self.conn.commit()
        logging.info("Updated blood message grade for player %r, rows affected %d" % (characterID, c.rowcount))
