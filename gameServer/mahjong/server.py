# -*- coding:utf-8 -*-
#!/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description: Server factory
"""

from common.log import log, LOG_LEVEL_RELEASE, LOG_LEVEL_ERROR
from common import net_resolver_pb
from common import mahjong_pb2
from common.server import Server

from player import Player
from game import Game

# import redis_instance
# import copy

class MahjongServer(Server):
    protocol = Player

    def __init__(self, *args, **kwargs):
        assert 'serviceTag' in kwargs
        self.serviceTag = kwargs['serviceTag']
        del kwargs['serviceTag']
        super(MahjongServer, self).__init__(*args, **kwargs)
        self.ip = self.serviceTag.split(':')[1]
        self.port = self.serviceTag.split(':')[2]

    def getGameID(self):
        return MY_GAMEID

    #创建游戏房间时调用
    def getGameModule(self, *initData):
        return Game(*initData)

    def startFactory(self):
        log(u'[on start factory]', LOG_LEVEL_RELEASE)

    def stopFactory(self):
        log(u'[on stop factory] peerList %s.'%(self.peerList), LOG_LEVEL_RELEASE)

    def registerProtocolResolver(self):
        unpacker = net_resolver_pb.Unpacker
        self.recverMgr.registerCommands( (\
            # unpacker(mahjong_pb2.C_S_CONNECTING, mahjong_pb2.C_S_Connecting, self.onReg), \
            # unpacker(mahjong_pb2.C_S_EXIT_ROOM, mahjong_pb2.C_S_ExitRoom, self.onExitGame), \
            unpacker(mahjong_pb2.C_S_PING, mahjong_pb2.C_S_Ping, self.onPing), \
            ) )
        packer = net_resolver_pb.Packer
        self.senderMgr.registerCommands( (\
            packer(mahjong_pb2.S_C_PING, mahjong_pb2.S_C_Ping), \
        ) )

    def onPing(self, player, game):
        # player.isOnline = True
        player.lastPingTimestamp = self.getTimestamp()
        resp = mahjong_pb2.S_C_Ping()
        self.sendOne(player, resp)
        # player.OnRefresh()
        log(u'[onPing][%s] lastPingTimestamp[%s]'%(player.descTxt,player.lastPingTimestamp), LOG_LEVEL_RELEASE)

