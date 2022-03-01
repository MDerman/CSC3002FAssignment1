import sys
from socket import *
from threading import Thread


def processMessage(msg, clientAddress):

    if clientAddress not in clients.keys():
        if login_cmd not in msg[0:len(login_cmd)]:
            unicast_msg("Welcome! Don't forget to login to receive direct messages!", clientAddress)
            client_name = "Client " + str(len(clients))
            clients[clientAddress] = client_name

    if login_cmd in msg[0:len(login_cmd)]:
        client_name = (msg.replace(login_cmd + ' ', '')).split(" ")[0]
        clients[clientAddress] = client_name
        join_msg = f'Welcome {client_name}!'
        unicast_msg(join_msg, clientAddress)

    # if we are ending the session we need to remove the socket instance
    if msg == exit_cmd:
        print(f'{clients[clientAddress]} has disconnected ')
        unicast_msg('You are leaving the room...', clientAddress)
        client_name = clients[clientAddress]
        del clients[clientAddress]
        broadcast_msg(f'{client_name} has left the room!', clientAddress)

    # are we unicasting or broadcasting
    elif '@' in msg[0]:
        try:
            recepientName, msg = msg[1:].split(' ', 1)
            try:
                RecipientAddress = clients.get(recepientName)
            except:
                errormsg = recepientName + " not found. Please make sure you have entered the username correctly."
                unicast_msg(errormsg)
        except:
            print("An error occurred.")

        unicast_msg(msg, RecipientAddress)
        unicast_msg(CONFIRMATIONMSGWHERECLIENTDOESNTPRINT, clientAddress)
        print(msg)
    else:
        broadcast_msg(msg, clientAddress)

def broadcast_msg(msg, clientAddress):
    #here I use clientAddress to be the one who sent the message to be broadcast
    #or the one user who doesn't need to see the broadcast - so this is technically
    #not used a "true broadcast"
    print(msg)
    for client in clients:
        if (clientAddress != client):
            serverSocket.sendto(msg.encode(), client)
        else:
            unicast_msg(CONFIRMATIONMSGWHERECLIENTDOESNTPRINT, client)

def unicast_msg(msg, client):
    serverSocket.sendto(msg.encode(), client)

def check_for_client_connections(serverSocket, bufferSize):
    while True:
        msg, clientAddress = serverSocket.recvfrom(bufferSize)
        processMessage(msg.decode(), clientAddress)


if __name__ == "__main__":

    clients = {}
    port = 13370
    bufferSize = 2048

    exit_cmd = "/exit"
    login_cmd = "/login"
    CONFIRMATIONMSGWHERECLIENTDOESNTPRINT = "CONFIRMATIONMSGWHERECLIENTDOESNTPRINT"

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
