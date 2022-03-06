from datetime import datetime
import hashlib
import base64
import select
import sys
import time
from socket import *
from threading import Thread, Lock
import json

#@Slaven so now we have messages_being sent being populated whenever we send a message,
#once confirmation from server is received, we remove the message from messages_being_sent
#and add it to messages_received. if the actual message was corrupted, then the headers won't match
#and so it will be as if the message was never received according to the client.


def receive_messages_from_server():
    while True:
        global msgs_rec
        global clientSocket
        bytesmessage = ""
        serverAddress = ""
        try:
            bytesmessage, serverAddress = clientSocket.recvfrom(bufferSize)
            # get header and message
            bytesmessage = str(base64.b64decode(bytesmessage))
            dictString, bytesmessage = bytesmessage.split('<END>', 2)
            dictString = dictString[2:]
            message = bytesmessage[:-1]
            header = json.loads((dictString.replace("'", "\"")))
            msgs_rec = msgs_rec + 1
            
            if message == '][Server] You are leaving the room...':
                print("["+ (header.get("SentTime"))  + message)
                print("You have left")
                return False
            elif  message != 'CONFIRMATION':
                print("["+ (header.get("SentTime"))  + message)
            else:
                if len(messages_being_sent) > 0:
                    for i in messages_being_sent:
                        if header == messages_being_sent[i]:
                            messages_received.append(header)
                            messages_being_sent.pop(i)
                        else:
                            return False
        except:
            time.sleep(0.01)

def get_header(msg):
    time = datetime.now()
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header = {
        "SentTime": time.strftime("%m/%d/%Y, %H:%M"),
        "Hash": hash
    }
    return header

def create_bytes_msg(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    return base64.b64encode(msgbytes.encode('ascii'))

def send_msg_with_header(header, msg, address):
    msgbytes = create_bytes_msg(header, msg)
    messages_being_sent.append((header, message))
    clientSocket.sendto(msgbytes, address)

def send_msg(msg, address):
    send_msg_with_header(get_header(msg), msg, address)

def send_messages():
    #TRY SEND MESSAGES
    while True:
        if len(messages_being_sent) > 0:
            send_msg(messages_being_sent[0][1], address)
        time.sleep(0.5)

if __name__ == "__main__":

    global msgs_rec
    messages_being_sent = []
    messages_received = []
    msgs_rec = 0

    server = '127.0.0.1'
    port = 13370
    bufferSize = 2048
    address = (server, port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.setblocking(True)
    exit_cmd = "/exit"
    messages_sent = 0
    th = Thread(target=receive_messages_from_server, args=())
    th.start()
    #Thread(target=send_messages, args=()).start()

    msgs_rec = 0
    time.sleep(1)
    print(msgs_rec)

    while True:

        if (messages_sent == 0):
            message = input('Welcome to the chat!\nType \"/login\ '
                            '[USERNAME]\" to login.\nType \"/exit\" to exit.\nUse @[USERNAME] to send a direct message.\n')
            messages_sent += 1
        else:
            messages_sent += 1
            message = input()
        if message == exit_cmd:
            header = get_header(message)
            send_msg(message, address)
            th.join()
            sys.exit()
        if message != "":
            try:
                header = get_header(message)
                send_msg(message, address)
                message = ""
            except:
                print("Chat server is offline. Message not sent.")
            message = ""
   

    