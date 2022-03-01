import sys
from socket import *
from threading import Thread

# def inputThread(messages_sent):
#     while True:
#         message = ""
#         if (messages_sent == 0):
#             message = input("Use /login [USERNAME] to login\n")
#             messages_sent += 1
#         else:
#             messages_sent += 1
#             message = input()
#         if message == exit_cmd:
#             break
#         if message != "":
#             clientSocket.sendto(message.encode(), address)

# def update_messages(bufferSize, clientSocket):
#     listeningSocket = socket(AF_INET, SOCK_DGRAM)
#     listeningSocket.bind(("", port))
#     while True:
#         returnMsg, serverAddress = clientSocket.recvfrom(bufferSize)
#         if returnMsg != "":
#             print(returnMsg.decode())
#         if message == exit_cmd:
#             break

if __name__ == "__main__":

    server = '127.0.0.1'
    port = 13370
    bufferSize = 2048
    address = (server, port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    exit_cmd = "/exit"

    messages_sent = 0
    #Thread(target=inputThread, args=(messages_sent,)).start()

    while True:
        message = ""
        if (messages_sent == 0):
            message = input('Welcome to the chat!\nType \"/login\ '
                            '[USERNAME]\" to login.\nType \"/exit\" to exit.\nUse @[USERNAME] to send a direct message.\n')
            messages_sent += 1
        else:
            messages_sent += 1
            message = input()
        if message == exit_cmd:
            break
        if message != "":
            try:
                clientSocket.sendto(message.encode(), address)
                returnMsg, serverAddress = clientSocket.recvfrom(bufferSize)
                if returnMsg != "":
                    print(returnMsg.decode())
            except:
               print("Chat server is offline.")
            #clientSocket.close()
            #clientSocket = socket(AF_INET, SOCK_DGRAM)


