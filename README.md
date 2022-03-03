# CSC3002FAssignment1

to get this working:
open udp port 13370 for incoming connections on your laptop
open cmd, type python -m http.server 13370 (that's just the port im using but ja)
then start the server.py, and type shit in client.py 

#NOTE
_**1 - currently when a client sends a message, there HAS to be a response or the whole
interface freezes.
2 - every time we receive a message, recv, we might be multiple messages
behind the one we were meant to receive for that request. So we need to make sure that
messages can be received and printed independently of the input and receive thread.
client seems to store and return messages received in the past with recv**_

What the CLI should do/enable:
-client types in:
"/exit"
sends messages and removes them from the 

"/login USERNAME"
(establish connection with server and assign that socket to that user)

-"@OTHER_USER message text here"
(will send that message to server, which then stores msg in array and then sends it to OTHER_USER)

-client just types text
e.g. "fjaslf jsldf"
(this get broadcast to all clients that the server has an active connection with)



PROTOCOL STUFF - 
i am tracking whether messages are received by the server - not whether they are delivered
-we should only ever get one response for a message sent a server

also i am using the hash incorrectly (probably) - i am just hashing the message part of the packet and then sending that to the
server and from the server back to the client and seeing if that matches. not hashing the whole packet or whatever

to do:
-msg count per client - client must send msg number and server must always send back a
response to the client saying it has received that msg number. client instance keeps track of all messages
sent (storing the: server address, msg, time, and whether it was received or not)
the next time a client sends a message that is received by the server, we then go through all the unsent
messages and send them again.

SERVER CRASHES WHEN CLIENT CONNECTS AGAIN

server has similar array/db: sender, receiver, msg, time, received?, type (broad/uni cast)

don't worry about encryption



