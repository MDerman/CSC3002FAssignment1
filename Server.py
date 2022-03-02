import base64
import sys
from socket import *
from threading import Thread
import json
from datetime import datetime
import hashlib

def processMessage(data, clientAddress):
    msg = data[1]
    header = data[0]

    if clientAddress not in clients.keys():
        if login_cmd not in msg[0:len(login_cmd)]:
            unicast_msg(header, "Welcome! Don't forget to login to receive direct messages!", clientAddress)
            client_name = "Client " + str(len(clients))
            clients[clientAddress] = client_name

    if login_cmd in msg[0:len(login_cmd)]:
        client_name = (msg.replace(login_cmd + ' ', '')).split(" ")[0]
        clients[clientAddress] = client_name
        join_msg = 'Welcome {client_name}!'
        unicast_msg(header, join_msg, clientAddress)

    # if we are ending the session we need to remove the socket instance
    if msg == exit_cmd:
        print(f'{clients[clientAddress]} has disconnected ')
        unicast_msg(header, 'You are leaving the room...', clientAddress)
        client_name = clients[clientAddress]
        del clients[clientAddress]
        broadcast_msg(header, f'{client_name} has left the room!', clientAddress)

    # are we unicasting or broadcasting
    elif '@' in msg[0]:
        try:
            recepientName, msg = msg[1:].split(' ', 1)
            try:
                RecipientAddress = clients.get(recepientName)
            except:
                errormsg = recepientName + " not found. Please make sure you have entered the username correctly."
                unicast_msg(header, errormsg, clientAddress)
        except:
            print("An error occurred.")

        unicast_msg(header, msg, RecipientAddress)
        print(msg)
    else:
        broadcast_msg(header, msg, clientAddress)

def parse_message_from_client(client):
    bytesmessage, serverAddress = serverSocket.recvfrom(bufferSize)

    #get header and message
    bytesmessage = str(base64.b64decode(bytesmessage))
    dictString, bytesmessage = bytesmessage.split('<END>', 2)
    dictString = dictString[2:]
    msg = bytesmessage[:-1]
    header = json.loads((dictString.replace("'", "\"")))

    #now we confirm
    msgbytes = (str(header) + "<END>" + "CONFIRMATION")
    msgbytes = base64.b64encode(msgbytes.encode('ascii'))
    serverSocket.sendto(msgbytes, client)

    #not sure how we will use this yet
    receivedMessages.append(header)
    return header, msg

def make_message(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    msgbytes = base64.b64encode(msgbytes.encode('ascii'))
    return msgbytes

def broadcast_msg(header, msg, clientAddress):
    #here I use clientAddress to be the one who sent the message to be broadcast
    #or the one user who doesn't need to see the broadcast - so this is technically
    #not used a "true broadcast"
    bytesmsg = make_message(header, msg)
    for client in clients:
        if (clientAddress != client):
            unicast_msg(bytesmsg, client)

def unicast_msg(header, msg, client):
    bytesmsg = make_message(header, msg)
    serverSocket.sendto(bytesmsg, client)

def check_for_client_connections(serverSocket, bufferSize):
    while True:
        msg, clientAddress = serverSocket.recvfrom(bufferSize)
        processMessage(parse_message_from_client(clientAddress), clientAddress)

if __name__ == "__main__":

    clients = {}
    receivedMessages = []
    port = 13370
    bufferSize = 2048

    exit_cmd = "/exit"
    login_cmd = "/login"

    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(("", port))
    print("Waiting for connections...")

    check_for_client_connections(serverSocket, bufferSize)

    #this prevents:
    #ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
    # try:
    #     check_for_client_connections(serverSocket, bufferSize)
    # except Exception as e:
    #     print(e)
    #     check_for_client_connections(serverSocket, bufferSize)


    serverSocket.close()
