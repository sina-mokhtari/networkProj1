import random
import socket
import threading
import re
import time
from time import sleep
from config import *

RTT = 200


class MyNetwork:

    def __init__(self):
        self.stack = [('', None, '')] * 20
        self.counter = 0
        self.game_connection = socket.socket()
        self.network_connection = socket.socket()

        self.network_socket = socket.socket()

        self.game_socket = socket.socket()
        self.game_socket.bind(('', 8001))

        self.isServer = False

        self.networkAvailable = False

        self.gameAvailable = False

        self.gameConnected = False

        self.ipPort = ''

        self.ipAddress = ''

        self.ownIpAddress = ''

        self.portNumber = 0

        self.ownPortNumber = 0

        self.sendTime = 0

        self.waitingForAck = False

        self.seqNum = 1

        self.prevSeq = 1

        self.timeoutReached = False

        self.lastSentPckt = ''

        stackChecker = threading.Thread(target=self.checkStack)
        stackChecker.start()

        timeoutChecker = threading.Thread(target=self.TimeoutCheck)
        timeoutChecker.start()


# ---------------------------- ! Dont Touch My Code ! ----------------------------
# --------------------------------------------------------------------------------
# -------------------------------------🏴‍☠️🏴‍☠️---------------------------------------
# --------------------------------------------------------------------------------
# -----------------------------🚩 ! Danger Zone ! 🚩-------------------------------

    def packetStore(self, packets):
        """Each packet contains -> data , pckt_time , ip
        """
        for _pckt in packets:

            data, pckt_time, ip = _pckt

            if DestroyPacket and random.randint(0, 100) < Chance_Destroy * 100:
                index_1 = random.randint(0, len(data) - 1)
                index_2 = random.randint(0, len(data) - 1)
                index_3 = random.randint(0, len(data) - 1)
                data = data.replace(data[index_1], data[index_2])
                data = data[:index_3] + '$' + data[index_3+1:]
                # edited by us ###############################
                _pckt = data, pckt_time, ip

            if PacketLoss and random.randint(0, 100) < Chance_Loss * 100:
                print("--- Packet Loss ---")
                continue

            safe, pckt = self.Firewall(_pckt)

            if not safe:
                continue

            data, pckt_time, ip = pckt

            if self.counter >= max_stack_size:
                print("--- Stack Full ! ---")
                return

            self.stack[self.counter] = (data, pckt_time, ip)
            self.counter += 1

    def checkStack(self):
        while True:
            while self.counter > 0:
                sleep(network_delay)
                self.OnNetworkData()

    def ReadLastPacket(self):
        """Read last packet in stack. 
            return -> content , pckt_time , ip
        """

        if self.counter > 0:
            result = self.stack[self.counter - 1]
            self.counter -= 1
            return result

    def SendDataToClient(self, data: str):
        """Send packet data to your Client using (self.network_connection) 
        """

        try:
            self.network_connection.send(data.encode())
        except BaseException as e:
            print(e)

    def SendDataToGame(self, data: str):
        """Send packet data to Game
        """

        try:
            self.game_connection.send(data.encode())
        except BaseException as e:
            print(e)


# -----------------------------🚩 ! Danger Zone ! 🚩-----------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


# ------------------------------ ❤ This is For You ❤ ----------------------------

# ----------------------------  Bridge Service Functions -------------------------

    def Firewall(self, packet):
        data, time, ip = packet
        if ((ip != str(self.ipPort))):
            print(" DDoS Blocked :))))) ")
            return False, packet
        else:
            return True, packet
        # return (True, packet) if (re.match('[0-1],[0-9],[0-9]', str(packet))) else (False, packet)

    def OnGameData(self, data: str):

        if not data:
            return

        print(f"Unity Says: {data}")

        if (data == "CLOSE"):
            self.networkAvailable = False
            return

        dataSplitted = data.split(',')

        if (dataSplitted[0] == 'H' or dataSplitted[0] == 'C'):
            if not (self.networkAvailable):
                if (dataSplitted[0] == 'H'):
                    self.gameConnected = True
                    self.isServer = True
                    self.ownIpAddress = dataSplitted[1]
                    self.ownPortNumber = int(dataSplitted[2])
                    try:
                        pass
                        # self.network_socket.bind(
                        #     (dataSplitted[1], int(dataSplitted[2])))
                        # self.network_socket.listen(5)
                    except:
                        print("error")
                else:
                    self.gameConnected = True
                    self.isServer = False
                    self.ipAddress = dataSplitted[1]
                    self.portNumber = int(dataSplitted[2])
                    # self.network_connection.connect(
                    #     (dataSplitted[1], int(dataSplitted[2])))

        else:

            if self.isServer and data[0] == '2':
                return

            if (not self.isServer) and data[0] == '1':
                return

            crc = self.CrcCalculate(data)
            self.changeSeq()
            #print(f"turn in onGameData: {self.seqNum}")
            self.lastSentPckt = data + "," + str(self.seqNum) + "," + str(crc)
            print(f"last: {self.lastSentPckt}")
            self.SendDataToClient(self.lastSentPckt)
            self.waitingForAck = True
            self.sendTime = round(time.time()*1000)
            # print(self.lastSentPckt[0:5])
            # print(self.lastSentPckt.split(',')[4])

    def OnNetworkData(self):
        data = self.ReadLastPacket()
        print(f"Network Says: {str(data)}")

        # receive ack
        if self.waitingForAck:
            if (data[0] == "ACK0"):
                if self.seqNum == 0:
                    self.waitingForAck = False
                else:
                    print("ignoring junk ACK")
                return

            if (data[0] == "ACK1"):
                if self.seqNum == 1:
                    self.waitingForAck = False
                else:
                    print("ignoring junk ACK")
                return

        else:
            if (data[0] == "ACK0" or data[0] == "ACK1"):
                print("ignoring junk ACK")
                return

        if (re.search('[^0-9,]', data[0])):
            return

        # receive data
        if (re.match('[1-2],[0-9],[0-9]', data[0][0:5])):
            crc = data[0].split(',')[4]
            # ?????????????
            if not (self.CrcCheck(data[0][0:5], crc)) or data[0].split(',')[3] == self.prevSeq:
                # packet destroyed or out of order, send previous ACK
                print(
                    f"got repeated data!! sending last ack: ACK{self.prevSeq}")
                self.SendDataToClient("ACK" + str(self.prevSeq))
            else:
                #print(f"turn in onNetworkData: {self.rcvTurn}")
                self.SendDataToClient(
                    "ACK" + str(data[0].split(',')[3]))  # ?????????????
                self.SendDataToGame(data[0][0:5])
                self.SendDataToGame("OK")
                self.prevSeq = data[0].split(',')[3]  # ?????????????

        else:
            print(f"something wrong with this data: {data}")

    def CrcCalculate(self, data: str):
        s = 0
        for i in range(0, len(data), 2):
            if (i+1) < len(data):
                a = ord(data[i])
                b = ord(data[i+1])
                s = s + (a+(b << 8))
            elif (i+1) == len(data):
                s += ord(data[i])
            else:
                raise "Something Wrong here"

        s = s + (s >> 16)
        s = ~s & 0xffff

        return s

    def CrcCheck(self, data: str, crc: str):
        if (re.search('[^0-9]', crc)):
            return False

        return self.CrcCalculate(data) == int(crc)

    def TimeoutCheck(self):
        while True:
            if self.waitingForAck:
                if (round(time.time()*1000) - self.sendTime > RTT):
                    # self.timeoutReached = True
                    print(
                        f"timeout reached!! sending again: {self.lastSentPckt}")
                    self.SendDataToClient(self.lastSentPckt)
                    self.sendTime = round(time.time()*1000)

    def changeSeq(self):
        self.seqNum = 1 if (self.seqNum == 0) else 0
