# CSC3002FAssignment1

to get this working:
open udp port 13370 for incoming connections on your laptop
open cmd, type python -m http.server 13370 (that's just the port im using but ja)
then start the server.py, and type shit in client.py 


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
idk how they want this. we can either include it this stuff in the message
body and then parse the string, or we could actually add header info using 
dictionaries / json 

to do:
-msg count per client - client must send msg number and server must always send back a
response to the client saying it has received that msg number. client instance keeps track of all messages
sent (storing the: server address, msg, time, and whether it was received or not)
the next time a client sends a message that is received by the server, we then go through all the unsent
messages and send them again.

server has similar array/db: sender, receiver, msg, time, received?, type (broad/uni cast)

don't worry about encryption