from studyhelperbot.db import AnalizaDB
import studyhelperbot.bot 
import logging

logging.basicConfig(level=logging.INFO)
db = AnalizaDB()
db.connect()
db.disconnect()
