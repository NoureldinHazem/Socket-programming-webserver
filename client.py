from socket import *
import time
import sys


def POST_Request_Message(file, host, version):
    message = "POST /" + file + " HTTP/"+version+"\r\n"
    Host = "Host: " + host + "\r\n\r\n"
    f1 = open(file, 'rb')
    body = f1.read()
    f1.close()
    return bytes(message + Host, "UTF-8") + body + b'\r\n'


def recv_timeout(the_socket, timeout=2):
    the_socket.setblocking(0)

    total_data = bytearray()
    data = '';

    begin = time.time()
    while 1:
        if total_data and time.time() - begin > timeout:
            break

        elif time.time() - begin > timeout * 2:
            break

        try:
            data = the_socket.recv(8192)
            if data:
                total_data.extend(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    return total_data


def GET_Request_Message(file, host, version):
    message = "GET /" + file + " HTTP/"+version+"\r\n"
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
    host = com.split()[2]

    for i in range(len(cache)):
        if cache[i][0] == file and host==cache[i][1]:
            return i
    return -1



if __name__ == '__main__':
    # bash arguments added
    if len(sys.argv) == 2:
        commands_file = sys.argv[1]
    else:
        commands_file = "input.txt"
    f = open(commands_file, 'r')
    cache = []
    version="1.0"
    i=0
    while True:
        
        line = f.readline()
        if not line:
            break
        command, filename, ip_address, Port_num = Line_Parsing(line)
        if version=="1.1" and i==0:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((ip_address, Port_num))
            i=2
        if command == 'GET':
            index=CheckCache(line, cache)
            
            if index!=-1:
                print("file is already in cache and already imported\r\n")
                print("Old response:")
                print(cache[index][2])
                print()
                continue
            if version=="1.0":
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect((ip_address, Port_num))
            clientSocket.send(GET_Request_Message(filename, ip_address, version))

        elif command == 'POST':
            if version=="1.0":
                clientSocket = socket(AF_INET, SOCK_STREAM)
                clientSocket.connect((ip_address, Port_num))
            clientSocket.send(POST_Request_Message(filename, ip_address, version))

        print("Message Received: \n ")

        if command == 'GET':
            GET_Data = recv_timeout(clientSocket)
            data = GET_Data.split(b'\r\n\r\n')[1]
            print(GET_Data.split(b'\r\n\r\n')[0].decode("UTF-8"))
            status = GET_Data.split(b'\r\n\r\n')[0].split(b' ')[1].decode("UTF-8")
            if status != '404':
                temp_file = filename
                filename = "Client get/" +ip_address+"_"+ filename
                f2 = open(filename, "wb")
                f2.write(data)
                f2.close()
                cache.append([temp_file,ip_address,(GET_Data.split(b'\r\n\r\n')[0].decode("UTF-8"))])

        elif command == 'POST':
            Response_received = recv_timeout(clientSocket)
            print(Response_received.decode("UTF-8"))

    f.close()
    clientSocket.close()
    print("Closing connection...\n\n")
