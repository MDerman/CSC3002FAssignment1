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
    global msgs_rec
    while msgs_rec != -1:
        
        global clientSocket
        bytesmessage = ""
        serverAddress = ""
        try:
            clientSocket.settimeout(9999)
            bytesmessage, serverAddress = clientSocket.recvfrom(bufferSize)
            # get header and message
            bytesmessage = str(base64.b64decode(bytesmessage))
            dictString, bytesmessage = bytesmessage.split('<END>', 2)
            dictString = dictString[2:]
            message = bytesmessage[:-1]
            header = json.loads((dictString.replace("'", "\"")))
            msgs_rec = msgs_rec + 1
            if message == '[Server] You are leaving the room...':
                print("["+ (header.get("SentTime"))  + "]" + message)
                print("You have left")
                return False
            elif header["Type"] != "C":
                print("["+ (header.get("SentTime")) +"]" + message)
            else:
                if len(arr_messages_pending) > 0:
                    for i in range(0, len(arr_messages_pending)):
                        header_client = arr_messages_pending[i][0]
                        if (header["Sent"] == header_client["Sent"]) and (
                            header["Hash"] == header_client["Hash"]
                        ):
                            arr_messages_received.append(header)
                            print("\x1B[3m(message received)")
                            arr_messages_pending.pop(i)
                        else:
                            return False
        except:
            time.sleep(0.01)

def get_header(msg):
    time = datetime.now()
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header = {
        "Sent": time.strftime("%m/%d/%Y, %H:%M"),
        "Hash": hash,
        "Type" : "M",
        "Num" : messages_sent
    }
    return header

def create_bytes_msg(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    return base64.b64encode(msgbytes.encode('ascii'))

def send_msg_with_header(header, msg, address):
    msgbytes = create_bytes_msg(header, msg)
    clientSocket.sendto(msgbytes, address)

def send_msg(msg, address):
    global messages_sent
    send_msg_with_header(get_header(msg), msg, address)

def send_messages():
    if len(arr_messages_pending) > 0:
        time.sleep(0.1)
        for i in range(0,len(arr_messages_pending), 1):
              if len(arr_messages_pending) > 0:
                 global messages_sent
                 msg = arr_messages_pending[i][1]
                 head = arr_messages_pending[i][0]
                 head["Type"] = "C" #possibility of using a different type here...
                 send_msg_with_header(head, msg, address)

if __name__ == "__main__":

    global msgs_rec
    arr_messages_pending = []
    arr_messages_received = []
    msgs_rec = 0

    server = '127.0.0.1'
    port = 13370
    bufferSize = 2048
    address = (server, port)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.setblocking(True)
    exit_cmd = "/exit"
    messages_sent = 0
    receive_thread = Thread(target=receive_messages_from_server, args=())
    receive_thread.start()
    #send_msg_thread = Thread(target=send_messages, args=())
    #send_msg_thread.start()

    message = 'connection established'
    header = get_header(message)
    send_msg(message, address)
    print("Welcome!")
    while True:
        # now we try to send messages that have not been received by the server
        send_messages()
        if (messages_sent == 0):
            message = input('Type \"/login\ ' + '[USERNAME]\" to login.\nType \"/exit\" to exit.\nUse @[USERNAME] to send a direct message.\n')
        else:
            message = input()
        if message == exit_cmd:
            header = get_header(message)
            send_msg(message, address)
            receive_thread.join()
            sys.exit()
        if message != "":
            try:
                header = get_header(message)
                arr_messages_pending.append((header, message))
                messages_sent += 1
                send_msg(message, address)
            except:
                print("Chat server is offline. Message not sent.")

    #else:
        # msgs_rec = -1
        # print("Unfortunately, you are unable to establish a connection with the server - please try again later")
        # receive_thread.join
        # #send_msg_thread.join
        # sys.exit()
        #

    