import socket
import threading
import os

# Constants
MAX_CONNECTIONS = 10
PORT = 5000
LENGTH = 10240
FORMAT = 'utf-8'

# setting up server
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)


def response(method, failure: bool, http, filetype=None, file_body=None):
    if not failure:
        status = 200
        status_message = 'OK'
    else:
        status = 404
        status_message = 'Not Found'

    response_message = f"HTTP/{http} {status} {status_message}\r\n\r\n"
    print("\n", response_message)

    if method == 'POST':
        return response_message

    else:
        if file_body is None:
            reply_message = response_message.encode(FORMAT) + b'\r\n'
            return reply_message
        else:
            if filetype == 'txt':
                print("Body: ", file_body)
                reply_message = response_message.encode(FORMAT) + file_body.encode(FORMAT) + b'\r\n'
                return reply_message
            else:
                reply_message = response_message.encode(FORMAT) + file_body + b'\r\n'
                return reply_message


def get_function(file, filetype):
    try:
        if os.path.exists(file):
            if filetype == 'txt':
                f = open(file, 'r')
                return f.read()
            else:
                f = open(file, 'rb')
                return f.read()
        else:
            print(f"\nFile [{file}] not found")
            return -1
    except IOError:
        print(f"\nIOError : {IOError}")
        return -1


def post_function(file, data):
    try:
        f = open(file, 'wb')
        f.write(data)
        return 0
    except IOError:
        print(f"\nIOError : {IOError}")
        return -1


def handle_client(connection, address):
    print(f"[NEW CONNECTION] {address} connected to server.")

    request = connection.recv(LENGTH)
    # request_length = len(request)
    print(f"[{address}] \n{request}")

    messages = request.split(b'\r\n')
    method_b = messages[0].split(b' ')[0]
    file_b = messages[0].split(b'/')[1].split(b' ')[0]
    file_type_b = messages[0].split(b'/')[1].split(b' ')[0].split(b'.')[1]
    http_b = messages[0].split(b'/')[2].split(b'\r\n')[0]
    method = method_b.decode(FORMAT)
    file = file_b.decode(FORMAT)
    file_type = file_type_b.decode(FORMAT)
    http = http_b.decode(FORMAT)
    print("\nmethod:", method)
    print("filename:", file)
    print("filetype:", file_type)
    print("http:", http)

    if method == 'GET':
        # file_content will have -1 if error occurred or will have the body of the file
        file_content = get_function(file, file_type)
        if file_content == -1:
            response_message = response(method, True, http, file_type)
        else:
            response_message = response(method, False, http, file_type, file_content)
        connection.send(response_message)
    else:
        data = request.split(b'\r\n\r\n')[1]
        flag = post_function(file, data)
        if flag == 0:
            response_message = response(method, False, http)
        else:
            response_message = response(method, True, http)

        connection.send(response_message.encode(FORMAT))

    # Closing connection
    connection.close()
    print(f"[CLOSING] {address} closed  ")


def start():
    server.listen(MAX_CONNECTIONS)
    print(f"[LISTENING] Server is listening on {SERVER} port {PORT}")
    while True:
        # block execution and waits for an incoming connection
        connection, address = server.accept()

        # creating new thread (connection)
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()

        # Printing total number of active threads
        print(f"[ACTIVE CONNECTIONS] : {threading.active_count() - 1}")


print("[STARTING] Server is starting.....")
start()
