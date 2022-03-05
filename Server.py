import base64
import sys
from socket import *
from threading import Thread
import json
from datetime import datetime
import hashlib

def get_header(msg):
    time = datetime.now()
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header = {
        "SentTime": str(time),
        "Hash": hash
    }
    return header

def is_client_name_taken(client_name):
    global clients
    for client in clients.values():
        if client == client_name:
            return True
    return False

def get_address_from_client_name(client_name):
    for client_tuple in clients.items():
        if client_tuple[1] == client_name:
            return client_tuple[0]
    return None

def processMessage(data, clientAddress):
    msg = data[1]
    header = data[0]

    if clientAddress not in clients.keys():
        if login_cmd not in msg[0:len(login_cmd)]:
            unicast_msg(header, "][Server] Welcome! Don't forget to login to receive direct messages!", clientAddress)
            client_name = "Client " + str(len(clients))
            clients[clientAddress] = client_name

    if login_cmd in msg[0:len(login_cmd)]:
        client_name = (msg.replace(login_cmd + ' ', '')).split(" ")[0]
        if is_client_name_taken(client_name):
            error_msg = "][Server] Sorry, that name is taken. Try another."
            unicast_msg(get_header(error_msg), error_msg, clientAddress)
        else:
            clients[clientAddress] = client_name
            join_msg = '][Server] Welcome {}!'.format(client_name)
            unicast_msg(get_header(join_msg), join_msg, clientAddress)
            broadcast_msg(get_header(msg),"][Broadcast from: Server] " +str(client_name)+" has just come online!", clientAddress)
    
    elif msg == exit_cmd:
        print(f'{clients[clientAddress]} has disconnected ')
        unicast_msg(get_header(msg), '][Server] You are leaving the room...', clientAddress)
        client_name = clients[clientAddress]
        del clients[clientAddress]
        broadcast_msg(get_header(msg), "][Broadcast from: Server] " + str(client_name) + " has left the chat room!", clientAddress)

    # are we unicasting or broadcasting
    elif '@' in msg[0]:
        try:
            recipient_name, msg = msg[1:].split(' ', 1)
            try:
                RecipientAddress = get_address_from_client_name(recipient_name)
            except:
                error_msg = recipient_name + " not found. Please make sure you have entered the username correctly."
                unicast_msg(get_header(error_msg), error_msg, clientAddress)
        except:
            print("An error occurred.")
        msg = "][Direct Message from: "+ clients[clientAddress] + "] " +msg
        unicast_msg(get_header(msg), msg, RecipientAddress)
        print(msg)
    else:
        msg = "][Broadcast from: "+ clients[clientAddress] + "] " +msg
        print(msg)
        broadcast_msg(get_header(msg), msg, clientAddress)

def parse_message_from_client(bytesmessage, client):
    #get header and message
    bytesmessage = str(base64.b64decode(bytesmessage))
    dictString, bytesmessage = bytesmessage.split('<END>', 2)
    dictString = dictString[2:]
    msg = bytesmessage[:-1]
    header = json.loads((dictString.replace("'", "\"")))

    #now we confirm
    send_confirmation_message(msg, header, client)

    #not sure how we will use this yet
    receivedMessages.append(header)
    return header, msg

def send_confirmation_message(msg, header, client):
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header["Hash"] = hash
    msgbytes = (str(header) + "<END>" + "CONFIRMATION")
    msgbytes = base64.b64encode(msgbytes.encode('ascii'))
    serverSocket.sendto(msgbytes, client)

def make_message(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    msgbytes = base64.b64encode(msgbytes.encode('ascii'))
    return msgbytes

def broadcast_msg(header, msg, clientAddress):
    #here I use clientAddress to be the one who sent the message to be broadcast
    #or the one user who doesn't need to see the broadcast - so this is technically
    #not used a "true broadcast"
    for client in clients:
        if (clientAddress != client):
            unicast_msg(header, msg, client)

def unicast_msg(header, msg, client):
    bytesmsg = make_message(header, msg)
    serverSocket.sendto(bytesmsg, client)

def check_for_client_connections(serverSocket, bufferSize):
    while True:
        msg, clientAddress = serverSocket.recvfrom(bufferSize)
        processMessage(parse_message_from_client(msg, clientAddress), clientAddress)

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
    serverSocket.close()
