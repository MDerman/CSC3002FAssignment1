from datetime import datetime
import hashlib
import base64
import select
import sys
import time
from socket import *
from threading import Thread, Lock
import json

"""
Description: 
    Function that loops while the client is online and listens for any messages sent to the client socket.

Based on the type of message recieved this function can:
    Print the contents of the message
    Quit the function and trigger the thread to quit if the exit command is received
    Check to see if the integrity of the message has been preserved

How it works:
    Creates a socket that it continuously listens to 
    Decodes the message receieved from the server
    Retrieves the header associated with the message and creates its own header from the message it recieved
        If the two match up then the message is valid and it is printed
        Else: the server is notified the message has been corrupted and is 
        initated to go into loss recovery, the client does notprint the message

Parameters:
    None

Return:
    None
"""

def receive_messages_from_server():
    global msgs_rec
    while msgs_rec != -1:

        global clientSocket
        bytesmessage = ""
        serverAddress = ""
        try:
            clientSocket.settimeout(0.02)
            bytesmessage, serverAddress = clientSocket.recvfrom(bufferSize)

            # get header and message
            bytesmessage = str(base64.b64decode(bytesmessage))
            dictString, bytesmessage = bytesmessage.split('<END>', 2)
            dictString = dictString[2:]
            message = bytesmessage[:-1]
            header = json.loads((dictString.replace("'", "\"")))
            msgs_rec = msgs_rec + 1

            if message == '[Server] You are leaving the room...':
                print("[" + (header.get("SentTime")) + "]" + message)
                print("You have left")
                return False
            elif header["Type"] != "C":
                print("[" + (header.get("SentTime")) + "]" + message)
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

        except:
            time.sleep(0.01)


"""
Description:
    Function that is used to create and return the header for a specific message

Parameters:
    String: msg   //This is the message from which the header is created

Return:
    A header data struct with the following attributes:
        Sent   //Time message was sent
        Hash   //Hash value for the message
        Type   //Type of message, whether it is for confirmation or is to be printed by recipient
        Num    //Chronological ID of the message sent
"""
def get_header(msg):
    time = datetime.now()
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header = {
        "Sent": time.strftime("%m/%d/%Y, %H:%M"),
        "Hash": hash,
        "Type": "M",
        "Num": messages_sent
    }
    return header


"""
Description:
    Creates a sequence of bytes that represent the header and message to be sent

Parameters:
    Header Struct: header
    String: msg

Return:
    Byte sequence 
"""
def create_bytes_msg(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    return base64.b64encode(msgbytes.encode('ascii'))

"""
Description:
    Function that accumulates the header, msg and address information and 
    sends it to the desired location from the client socket

Parameters:
    Header Struct: header
    String: msg
    Address Object: address

Return
    None/Void
"""

def send_msg_with_header(header, msg, address):
    msgbytes = create_bytes_msg(header, msg)
    clientSocket.sendto(msgbytes, address)


"""
Description:
    Function that takes the message and address of where it must be sent
    and calls another 2 functions to send the message with a header

Parameters:
    String: msg
    Address Object: address

Return
    None/Void
"""
def send_msg(msg, address):
    global messages_sent
    send_msg_with_header(get_header(msg), msg, address)


"""
Description:
    Function that checks to see if there are any messages that are still required to be sent
    and if there are, then it loops for the number of messages to be sent and calls the necessary 
    functions to send the messages

Parameters:
    None

Return:
    None
"""
def send_messages():
    if len(arr_messages_pending) > 0:
        time.sleep(0.1)
        for i in range(0, len(arr_messages_pending), 1):
            if len(arr_messages_pending) > 0:
                global messages_sent
                msg = arr_messages_pending[i][1]
                head = arr_messages_pending[i][0]
                # possibility of using a different type here...
                head["Type"] = "C"
                send_msg_with_header(head, msg, address)

"""
Description:
    Function that checks to see if the latest message was received by the server and displays if it hasn't to the user.

Parameters:
    msgtuple, tuple that identifies an entry in arr_messages_pending

Return:
    None
"""

def is_offline(msgtuple):
    time.sleep(1.5)
    if msgtuple in arr_messages_pending:
        print("\x1B[3mThe server is offline. Message not delivered.")

"""
Description:
    Main method that instantiates the client, 
    creates a seperate thread for handling messages sent to this client,
    and creates a CLI to handle all user input

How it works:
    Sets up the necessary variables with the server address and port number
    Creates and starts the receiving thread    
    Loops to manage all user input
    Safely closes receiving thread before quiting client when exit command is executed

Paramters:
    None

Returns:
    None
"""
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

    message = 'connection established'
    header = get_header(message)
    send_msg(message, address)
    print("Welcome!")
    while True:
        # now we try to send messages that have not been received by the server
        send_messages()
        if (messages_sent == 0):
            message = input(
                'Type \"/login\ ' + '[USERNAME]\" to login.\nType \"/exit\" to exit.\nUse @[USERNAME] to send a direct message.\n')
        else:
            message = input()
            try:
                offline_check_thread.join()
            except:
                pass
        if message == exit_cmd:
            header = get_header(message)
            send_msg(message, address)
            receive_thread.join()
            sys.exit()
        if message != "":
            header = get_header(message)
            msgtuple = (header, message)
            arr_messages_pending.append(msgtuple)
            messages_sent += 1
            send_msg(message, address)
            offline_check_thread = Thread(target=is_offline, args=(msgtuple,))
            offline_check_thread.start()