import base64
import time
from operator import truediv
import sys
from socket import *
from threading import Thread
import json
from datetime import datetime
import hashlib

"""
Description:
    Function that is used to create and return the header for a specific message

Parameters:
    String: msg   //This is the message from which the header is created

Return:
    A header data struct with the following attriutes:
        Sent   //Time message was sent
        Hash   //Hash value for the message
        Type   //Type of message, whether it is for confirmation or is to be printed by recipient
        Num    //Chronological ID of the message sent
"""
def get_header(msg):
    time = datetime.now()
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header = {
        "SentTime": time.strftime("%m/%d/%Y, %H:%M"),
        "Hash": hash,
        "Type" : "M",
        "Num": -1
    }
    return header


"""
Description:
    Function that checks to see if a specified client name has alrerady been used

Parameters:
    String: client_name

Returns:
    Boolean  //whether or not the name has been taken
"""
def is_client_name_taken(client_name):
    global clients_dict
    for client in clients_dict.values():
        if client == client_name:
            return True
    return False


"""
Description:
    Function that returns the address of a specified client

Parameters:
    Client name

Returns:
    Address Object
"""
def get_address_from_client_name(client_name):
    for client_tuple in clients_dict.items():
        if client_tuple[1] == client_name:
            return client_tuple[0]
    return None


"""
Description:
    Function that receives message data and a client address
    And then based on the information, it decides the correct mode of operation
    such as to broadcast or unicast the message, throw an error or intiate a client to disconnect 

How it works:
    Checks to see if the client in the message exists and executes necessary response
    Checks to see if it is a login instruction and executes necessary response
    Checks to see if is is an exit command and executes necessary response
    Checks to see if it is a direct or broadcast message and executes necessary response

Parameters:
    Data Object: data
    Address Object: clientAddress

Return:
    An error in special circumstances
"""
def processMessage(data, clientAddress):
    msg = data[1]
    header = data[0]

  
    if clientAddress not in clients_dict.keys():
        # add client to clients dictionary
        client_name = "Client " + str(len(clients_dict))
        clients_dict[clientAddress] = client_name
        if (login_cmd not in msg[0:len(login_cmd)]):
            if (msg != exit_cmd):
                unicast_msg(header, "[Server] Don't forget to login to receive direct messages!", clientAddress)
            else:
                unicast_msg(header, "[Server] Why are you leaving so soon?", clientAddress)

    elif login_cmd in msg[0:len(login_cmd)]:
        client_name = (msg.replace(login_cmd + ' ', '')).split(" ")[0]
        if is_client_name_taken(client_name):
            error_msg = "[Server] Sorry, that name is taken. Try another."
            unicast_msg(get_header(error_msg), error_msg, clientAddress)
        else:
            clients_dict[clientAddress] = client_name
            join_msg = '[Server] Welcome {}!'.format(client_name)
            unicast_msg(get_header(join_msg), join_msg, clientAddress)
            broadcast_msg(get_header(msg),"[Broadcast from: Server] " +str(client_name)+" has just come online!", clientAddress)
    elif msg == exit_cmd:
        print(f'{clients_dict[clientAddress]} has disconnected ')
        unicast_msg(get_header(msg), '[Server] You are leaving the room...', clientAddress)
        client_name = clients_dict[clientAddress]
        del clients_dict[clientAddress]
        global c
        for i in range(0,len(arr_client_ordering)):
            if arr_client_ordering[i][0] == clientAddress:
                del arr_client_ordering[i]
        broadcast_msg(get_header(msg), "[Broadcast from: Server] " + str(client_name) + " has left the chat room!", clientAddress)

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

        if recipient_exists(recipient_name):    
            msg = "[Direct Message from: " + clients_dict[clientAddress] + "] " + msg
            unicast_msg(get_header(msg), msg, RecipientAddress)
            print(msg)
        else:
            msgs = "[Server] The user: "+ recipient_name +" does not exist"
            unicast_msg(get_header(msg), msgs, clientAddress)
    else:
        print("[" + clients_dict[clientAddress] + "] " + msg)
        msg = "[Broadcast from: " + clients_dict[clientAddress] + "] " + msg
        broadcast_msg(get_header(msg), msg, clientAddress)


"""
Description:
    Function that decodes a sequence of bytes into the original message and header
    And sends a confirmation message to the client to validate the message received
    Before finally returning the header and message decoded from the byte sequence

Parameters:
    bytes: bytemessage
    Client Object: client

Returns:
    Header Struct: header
    String: msg
"""
def parse_message_from_client(bytesmessage, client):
    #get header and message
    bytesmessage = str(base64.b64decode(bytesmessage))
    dictString, bytesmessage = bytesmessage.split('<END>', 2)
    dictString = dictString[2:]
    msg = bytesmessage[:-1]
    header = json.loads((dictString.replace("'", "\"")))

    #if (header["Type"] == "R"):
    #    print("received")
    ##now we check if this message has been received in the right order
    #message_number = header["Num"]
    # exists = False
    # for i in arr_client_ordering:
    #     if i[0] == client:
    #         t = i[1]
    #         t += 1
    #         stored_msg_num = t
    #         i = (client, t)
    #         exists = True
    ##commenting out ordering checks for now, this makes sense if a message
    # if not exists:
    #     arr_client_ordering.append((client, 1))
    #     stored_msg_num = 1
    # if message_number != stored_msg_num:
    #     print("A message was from " + clients_dict.get(client) + " was not received by the server.")
    #     stored_msg_num += 1

    #now we confirm
    send_confirmation_message(msg, header, client)

    receivedMessages.append(header)
    return header, msg


"""
Description:
    Function that takes the received message, header and client object and then 
    decodes this data before sending it to the client to validate that the message received 
    has not been corrupted

Parameters:
    Header Struct: header
    Client Object: client
    String: msg

Returns:
    None - Void
"""
def send_confirmation_message(msg, header, client):
    hash = int(hashlib.sha256(msg.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    header["Hash"] = hash
    header["Type"] = "C"
    msgbytes = (str(header) + "<END>")
    msgbytes = base64.b64encode(msgbytes.encode('ascii'))
    serverSocket.sendto(msgbytes, client)


"""
Description:
    Function that takes a header struct and message string and converts it into a bytes sequence
    before returning the byte sequence

Parameters:
    Header Struct: header
    String: msg

Returns:
    byte sequencee: msgbytes
"""
def make_message(header, msg):
    msgbytes = (str(header) + "<END>" + msg)
    msgbytes = base64.b64encode(msgbytes.encode('ascii'))
    return msgbytes


"""
Description:
    Function that checks to see if a specified recipient exists
    and returns the necessary response

Parameters:
    String: name

Returns:
    boolean   //true if the client exists
"""
def recipient_exists(name):
    if is_client_name_taken(name):
        return True
    else:
        return False


"""
Description:
    Function that takes a header struct, message and senders address
    and then proceeds to broadcast the message by calling the unicast function to all other members

Parameters:
    Header Struct: header
    String: msg
    Address Object: clientAddress

Returns:
    None
"""
def broadcast_msg(header, msg, clientAddress):
    #here we use clientAddress to be the one who sent the message to be broadcast
    for client in clients_dict:
        if (clientAddress != client):
            unicast_msg(header, msg, client)


"""
Description:
    Function that turns the message into a byte squence and then
    sends the message to the specified client

Parameters:
    Header Struct: header
    String: msg
    Client Object: client

Returns:
    None
"""
def unicast_msg(header, msg, client):
    bytesmsg = make_message(header, msg)
    serverSocket.sendto(bytesmsg, client)


"""
Description:    
    Function that continuously loops and waits for a message to arrive at the server socket
    before calling a function to parse any received message to execute the correct operation

Paraneters:
    socket: serverSocket
    int: bufferSize

Returns:
    None
"""
def check_for_client_connections(serverSocket, bufferSize):
    while True:
        #try:
            msg, clientAddress = serverSocket.recvfrom(bufferSize)
            processMessage(parse_message_from_client(msg, clientAddress), clientAddress)
        # except:
        #     time.sleep(0.1)


"""
Description:
    Main method that instantiates the server and declares all necessary variables for operation
    Calls function to listen at the server socket for any incoming messages from clients

Parameters:
    None

Returns:
    None
"""
if __name__ == "__main__":

    arr_client_ordering = []
    clients_dict = {}
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
