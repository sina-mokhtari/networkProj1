import random
import socket
import threading
from time import sleep
from config import *


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

        stackChecker = threading.Thread(target=self.checkStack)
        stackChecker.start()


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
        return True, packet

    def OnGameData(self, data: str):

        if not data:
            return

        print(f"Unity Says: {data}")

        dataSplitted = data.split(',')

        if (dataSplitted[0] == 'H' or dataSplitted[0] == 'C'):
            if (dataSplitted[0] == 'H'):
                self.isServer = True
                try:
                    self.network_socket.bind((dataSplitted[1], int(dataSplitted[2])))
                    self.network_socket.listen(5)
                except:
                    print("error")
            else:
                    self.isServer = False
                    self.network_connection.connect((dataSplitted[1], int(dataSplitted[2])))
        else:
            self.SendDataToClient(data)

    def OnNetworkData(self):
        data = self.ReadLastPacket()
        print(f"Network Says: {str(data)}")
        self.SendDataToGame(data[0])
        self.SendDataToGame("OK")