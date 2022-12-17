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
            if data:
                myNetwork.packetStore([(str(data), time.time(), str(myNetwork.ipPort))])

        except BaseException as e:
            if myNetwork.gameConnected:
                if myNetwork.isServer:
                    try:    # 
                        myNetwork.network_socket.bind(
                                    (myNetwork.ownIpAddress, myNetwork.ownPortNumber))
                        print(f"binding on {myNetwork.ownIpAddress} : {myNetwork.ownPortNumber}")
                        myNetwork.network_socket.listen(5)
                    except:
                        pass
                    myNetwork.network_connection, addr = myNetwork.network_socket.accept()
                    print("A Device connected")
                    myNetwork.ipPort = addr
                    # print(f"from server {myNetwork.ipPort}")
                else:
                    while True:
                        try:
                            myNetwork.network_connection.connect(
                                    (myNetwork.ipAddress, myNetwork.portNumber))
                            myNetwork.ipPort = myNetwork.network_connection.getpeername()
                            break
                        except:
                            continue



if __name__ == "__main__":
    main()