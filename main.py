import threading
import time
from network import MyNetwork
from DDoS import DDoSAttack

myNetwork = MyNetwork()

print("Unity Socket is listening")


def GameDataReceive():
    while True:
        try:
            global myNetwork

            data = myNetwork.game_connection.recv(1024).decode()
            myNetwork.OnGameData(str(data))

        except BaseException as e:
            myNetwork.game_socket.listen(5)
            myNetwork.game_connection, addr = myNetwork.game_socket.accept()
            print(f"Game Connected \n {myNetwork.game_connection}\n")


def main():
    global myNetwork

    x = threading.Thread(target=GameDataReceive)
    x.start()

    xD = threading.Thread(target=DDoSAttack, args=(myNetwork,))
    xD.start()

    while True:
        try:
            data = myNetwork.network_connection.recv(1024).decode()
            # someIpPort = myNetwork.network_connection.getpeername()
            # print(f"received from: {someIpPort}\nwith data: {data}");
            if data:
                myNetwork.packetStore([(str(data), time.time(), str(myNetwork.ipPort))])

        except BaseException as e:
            # print(e)
            if myNetwork.gameConnected:
                if myNetwork.isServer:
                    myNetwork.network_socket.bind(
                                (myNetwork.ownIpAddress, myNetwork.ownPortNumber))
                    myNetwork.network_socket.listen(5)
                    myNetwork.network_connection, addr = myNetwork.network_socket.accept()
                    myNetwork.networkAvailable = True
                    print("A Device connected")
                    myNetwork.ipPort = addr
                    # print(f"from server {myNetwork.ipPort}")
                else:
                    myNetwork.network_connection.connect(
                            (myNetwork.ipAddress, myNetwork.portNumber))
                    myNetwork.ipPort = myNetwork.network_connection.getpeername()



if __name__ == "__main__":
    main()