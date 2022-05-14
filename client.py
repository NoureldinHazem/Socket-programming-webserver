# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from socket import *
import time
import sys


def POST_Request_Message(file, host):
    message = "POST /" + file + " HTTP/1.0\r\n"
    Host = "Host: " + host + "\r\n\r\n"
    f1 = open(file, 'rb')
    body = f1.read()
    f1.close()
    return bytes(message + Host, "UTF-8") + body + b'\r\n'


def recv_timeout(the_socket, timeout=2):
    # make socket non blocking
    the_socket.setblocking(0)

    # total data partwise in an array
    total_data = bytearray()
    data = '';

    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break

        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break

        # recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.extend(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    # total_data1=' '.join([bytes(item) for item in total_data])
    # join all parts to make final string
    return total_data


def GET_Request_Message(file, host):
    message = "GET /" + file + " HTTP/1.0\r\n"
    body = "Host: " + host + "\r\n\r\n"
    message = bytes(message + body, "UTF-8")
    return message


def Line_Parsing(Line):
    inputs = Line.split()
    if len(inputs) == 4:
        port_num = inputs[3]
    else:
        port_num = int(80)
    return inputs[0], inputs[1], inputs[2], int(port_num)


def CheckCache(com, cache):
    file = com.split()[1]
    host=com.split()[2]
    for i in range(len(cache)):
        if cache[i][0] == file and host==cache[i][1]:
            return i
    return -1



    return False


if __name__ == '__main__':
    commands_file = "input.txt"
    f = open(commands_file, 'r')
    cache = []
    while True:

        line = f.readline()
        if not line:
            break
        command, filename, ip_address, Port_num = Line_Parsing(line)
        if command == 'GET':
            #print(CheckCache(line,cache))
            index=CheckCache(line, cache)
            if index!=-1:
                #print(CheckCache(line, cache))
                print("file is already in cache and already imported\r\n")
                print("Old response:")
                print(cache[index][2])
                print()
                continue
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((ip_address, Port_num))
            clientSocket.send(GET_Request_Message(filename, ip_address))

        elif command == 'POST':
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((ip_address, Port_num))
            clientSocket.send(POST_Request_Message(filename, ip_address))

        print("Message Received: \n ")

        if command == 'GET':
            GET_Data = recv_timeout(clientSocket)
            data = GET_Data.split(b'\r\n\r\n')[1]
            print(GET_Data.split(b'\r\n\r\n')[0].decode("UTF-8"))
            filename = "Client get/" +ip_address+"_"+ filename
            f2 = open(filename, "wb")
            f2.write(data)
            f2.close()
            cache.append([filename,ip_address,(GET_Data.split(b'\r\n\r\n')[0].decode("UTF-8"))])

        elif command == 'POST':
            Response_received = clientSocket.recv(2048)
            print(Response_received.decode("UTF-8"))

        print("Closing connection...\n\n")
    f.close()
    clientSocket.close()
