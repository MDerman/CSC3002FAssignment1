import sys
from socket import *

if __name__ == "__main__":

    server = '127.0.0.1'
    port = 13370
    bufferSize = 2048
    address = (server, port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    exit_cmd = "/exit"

    messages_sent = 0
    while True:
        try:
            if (messages_sent == 0):
                message = input("Use /login [USERNAME] to login\n")
                messages_sent += 1
            else:
                messages_sent += 1
                message = input()
            clientSocket.sendto(message.encode(), address)
            #sys.sleep(1)
            returnMsg, serverAddress = clientSocket.recvfrom(bufferSize)
            if returnMsg != "":
                print(returnMsg.decode())
            if message == exit_cmd:
                break
        except:
            print("Chat server is offline.")

    clientSocket.close()