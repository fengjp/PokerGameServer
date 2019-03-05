# -*- coding:utf-8 -*-
#!/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description: game logic
"""

from common import mahjong_pb2
from common.log import *
from player import Player

# import logging
# import logging.handlers
# LOG_FILE = 'log/game.log'

# handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # ???handler
# fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

# formatter = logging.Formatter(fmt)  
# handler.setFormatter(formatter)

# logger = logging.getLogger('game')
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)


class Game(object):
    '''游戏相关逻辑
    '''
    def __init__(self, server, ruleParams,needInit = True, roomId = 0):
        self.server = server
        self.roomId = roomId
        super(Game, self).__init__(server, ruleParams,needInit = needInit, roomId=0)

