#bin/python
#server
import sys
import socket
import select
import signal
     
HOST = '' #Running For all Interface Available  in OS
SOCKET_LIST = [] # list for socket,connections
RECV_BUFFER = 8192
PORT = 9999
#User Interption 
def sigint_handler(signum, frame):
    print '\n user interrupt ! (ctrl+c) Shutting Down '
    print "[info] shutting down Chat Server  \n\n"
    sys.exit()  
    
signal.signal(signal.SIGINT, sigint_handler)

def chat_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #(Address Already In Use ) error solving using setsockopt
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    s=SOCKET_LIST.append(server_socket)
    
    print "Chat server started on port " + str(PORT)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        # select takes 4 arguments 1-readable,2-writable,3-exception,4-timeout
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "User  (%s, %s) connected" % addr
                # To Know By All User i.e Someone Entered In Chat room  
                broadcast(server_socket, sockfd, "[%s:%s] entered in chatting room\n" % addr)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        broadcast(server_socket, sock, "\r"   + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

                # exception 
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())         