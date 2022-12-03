import threading
import time			
from network import MyNetwork
from DDoS import DDoSAttack

myNetwork = MyNetwork()

print ("Unity Socket is listening")

def GameDataReceive():
  while True:
    try:
      global myNetwork

      data = myNetwork.game_connection.recv(1024).decode()
      myNetwork.OnGameData(str(data))

    except BaseException as e:
      print (e)
      myNetwork.game_connection , addr = myNetwork.game_socket.accept()
      print (f"Game Connected \n {myNetwork.game_connection}\n")


def main():
  global myNetwork

  x = threading.Thread(target=GameDataReceive)
  x.start()

  xD = threading.Thread(target=DDoSAttack , args=(myNetwork,))
  xD.start()

  while True:
    try:
      data = myNetwork.network_connection.recv(1024).decode()
      if data:
        myNetwork.packetStore([(str(data) , time.time() , "ClientIP")])

    except BaseException as e:
      print (e)
      myNetwork.network_connection , addr = myNetwork.network_soccket.accept()
      print ("A Device connected")


if __name__ == "__main__":
  main()
