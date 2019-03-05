# -*- coding:utf-8 -*-
#!/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description: Server factory
"""

from autobahn.twisted.websocket import WebSocketServerFactory
from twisted.internet.task import LoopingCall

from log import log, LOG_LEVEL_RELEASE, LOG_LEVEL_ERROR
import net_resolver_pb
from gameobject import GameObject
from peer import Peer
import time

import traceback

CHECK_PEER_TICK = 5000
TICK_PEERS_COUNT = 10
MAX_PACKET_PER_TICK = 100

class Server(WebSocketServerFactory, GameObject):
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.peers = {}
        self.peerList = []
        self.tickPeerIdx = 0
        self.initNetManager()
        self.tickTimer = LoopingCall(self.onTick)
        self.tickTimer.start(0.2, False)
        self.lastCheckTimestamp = self.getTimestamp()

        self.msgBuffers = []

    def getTimestamp(self):
        return int(time.time()*1000)

    def logPrefix(self):
        """
        Describe this factory for log messages.
        """
        return self.__class__.__name__

    def sendData(self, peer, data):
        log(u'Send to [%s]'%(peer.descTxt))
        peer.sendMessage(data, True)

    def sendOne(self, peer, protocol_obj):
        assert isinstance(peer, Peer)
        self.sendData(peer, self.senderMgr.pack(protocol_obj))

    def send(self, peers, protocol_obj, excludes=()):
        data = self.senderMgr.pack(protocol_obj)
        for peer in peers:
            if peer not in excludes:
                self.sendData(peer, data)

    def sendAll(self, protocol_obj):
        self.send(self.peerList, protocol_obj)

    def getResolverMgr(self):
        return self.senderMgr, self.recverMgr

    def initNetManager(self):
        self.senderMgr = net_resolver_pb.SendManager()
        self.recverMgr = net_resolver_pb.RecvManager()
        self.registerProtocolResolver()

    def registerProtocolResolver(self):
        pass
        # raise 'abstract interface'

    def onAddPeer(self, peer):
        pass
        # raise 'abstract interface'

    def onRemovePeer(self, peer):
        pass
        # raise 'abstract interface'

    def addPeer(self, peer):
        assert peer.hashKey not in self.peers, "Peer[%s] is existed."%(peer.descTxt)
        self.peers[peer.hashKey] = peer
        self.peerList.append(peer)
        self.onAddPeer(peer)

    def removePeer(self, peer):
        assert peer.hashKey in self.peers, "Peer[%s] is not existed."%(peer.descTxt)
        #self.resolvePacketOnPeerClose(peer)
        self.onRemovePeer(peer)
        self.peerList.remove(peer)
        del self.peers[peer.hashKey]

    def isValidPacket(self, msgName):
        pass
        # raise 'abstract interface'

    def onTick(self):
        timestamp = self.getTimestamp()
        try:
            #self.resolvePacket(timestamp)
            self.onRefresh(timestamp)
        except:
            for tb in traceback.format_exc().splitlines():
                log(tb, LOG_LEVEL_ERROR)

    def onRefresh(self, timestamp):
        if timestamp - self.lastCheckTimestamp > CHECK_PEER_TICK:
            self.onCheck(timestamp)

    def onCheck(self, timestamp):
        self.lastCheckTimestamp = timestamp
        countPeers = len(self.peerList)
        if countPeers <= 0:
            return
        if self.tickPeerIdx >= countPeers:
            self.tickPeerIdx = 0
        peers = self.peerList[self.tickPeerIdx:self.tickPeerIdx+TICK_PEERS_COUNT]
        self.tickPeerIdx += TICK_PEERS_COUNT
        log(u'==================================Total peers [%s]============================'%(countPeers),LOG_LEVEL_RELEASE)
        for peer in peers:
            peer.onCheck(timestamp)

    def recvPacket(self, peer, buf):
        self.msgBuffers.append((peer, buf))

    def resolveMsg(self, peer, msgData):
        recvMgr = self.recverMgr
        unpackRes = recvMgr.unpackCall(peer, msgData)
        if not unpackRes:
            peer.invalidCounter('Invalid data for resolved.')
        elif self.isValidPacket(unpackRes[0]):
            peer.lastPacketTimestamp = self.getTimestamp()

    def resolvePacket(self, timestamp):
        recvMgr = self.recverMgr
        #log(u'Packet count[%d]'%(len(self.msgBuffers)))
        for peer, packet in self.msgBuffers[:MAX_PACKET_PER_TICK]:
            unpackRes = recvMgr.unpackCall(peer, packet)
            if not unpackRes:
                peer.invalidCounter('Invalid data for resolved.')
            elif self.isValidPacket(unpackRes[0]):
                peer.lastPacketTimestamp = timestamp
        self.msgBuffers = self.msgBuffers[MAX_PACKET_PER_TICK:]

    def resolvePacketOnPeerClose(self, peer):
        recvMgr = self.recverMgr
        for buf in self.msgBuffers[:]:
            if buf[0] == peer:
                recvMgr.unpackCall(buf[0], buf[1])
                self.msgBuffers.remove(buf)
