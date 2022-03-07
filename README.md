tests, add sending thread, print all users, ordered messages
what should we do when order is not correct

# CSC3002FAssignment1
_**This is CLI chat application using UDP with unicast, broadcast and login functionality. 
Reliability is created through **_


#Protocol
_**The protocol we are using to ensure reliability uses a dictionary containing the date the message
was sent, the hash of the message itself (into a fixed 8 character size), and the type of message - Type M
is a normal message, Type C is a confirmation message. This dictionary is added to the front of every message
sent. When the server receives a message, it unpacks the dictionary / message, hashes the message again, and then
sends a confirmation back to the client. The client has a separate thread running to receive messages, and if a
confirmation message with a hash and date that matches a message that has been sent, then that message is removed 
from pending messages and added to received/confirmed messages. **_

Chat commands:
"/exit" - removes user from the server's client list and displays to chat
"/login USERNAME" - changes the default name of the client to USERNAME on the server
"@OTHER_USER message text here" - direct message to OTHER_USER if user exists
"typing anything" - Broadcasts message to all clients


#setup HTTP server
- Open udp port 13370 for incoming connections.
- Open cmd, type "python -m http.server 13370" 






