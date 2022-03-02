from datetime import datetime
import hashlib
import base64
import select
import sys
import time
from socket import *
from threading import Thread
import json


def receive_messages_from_server():
    while True:
        bytesmessage, serverAddress = clientSocket.recvfrom(bufferSize)
        # get header and message
        bytesmessage = str(base64.b64decode(bytesmessage))
        dictString, bytesmessage = bytesmessage.split('<END>', 2)
        dictString = dictString[2:]
        message = bytesmessage[:-1]
        header = json.loads((dictString.replace("'", "\"")))

        if message != 'CONFIRMATION':
            print("["+str(header("SentTime")) + "] " + message)
        else:
            for i in messages_sent:
                if header == messages_sent[i]:
                    messages_received.append(header)
                else:
                    return False

def get_header(msg):
    time = datetime.now()
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header = {
        "SentTime": str(time),
        "Hash": hash
    }
    return header

def create_bytes_msg(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    return base64.b64encode(msgbytes.encode('ascii'))

def send_msg_with_header(header, msg, address):
    msgbytes = create_bytes_msg(header, msg)
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

    messages_being_sent = []
    messages_sent = []
    messages_received = []

    server = '127.0.0.1'
    port = 13370
    bufferSize = 2048
    address = (server, port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.setblocking(True)
    exit_cmd = "/exit"
    messages_sent = 0
    Thread(target=receive_messages_from_server, args=()).start()
    Thread(target=send_messages, args=()).start()

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
                header = get_header(message)
                send_msg(message, address)
            except:
                messages_being_sent.append(header, message)
                print("Chat server is offline. Message not sent.")
