import socket
from threading import Thread
import pickle

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "192.168.1.16"
PORT = 5500
HEADERSIZE = 10
DISCONNECT_MSG = "{DISCONNECT}"

SOCKET.connect((HOST, PORT))


def receive():
    new_msg = True
    full_msg = b""

    while True:
        try:
            msg = SOCKET.recv(HEADERSIZE)
            if len(msg):
                if new_msg:
                    new_msg = False
                    full_msg_len = int(msg)
                else:
                    full_msg += msg

                if len(full_msg) == full_msg_len:
                    full_msg = pickle.loads(full_msg)
                    message = f"{full_msg['sender_name']}> {full_msg['message']}"
                    print(message)
                    full_msg = b""
                    new_msg = True

        except Exception as e:
            SOCKET.close()
            print(f"{e}.\nYou are disconnected from the server")
            break


def send():
    new_user = True
    while True:
        try:
            if new_user:
                msg = input("Name: ")
                new_user = False
            else:
                content = input("Message: ")
                msg = f"{len(content):<{HEADERSIZE}}" + content
                SOCKET.send(msg.encode("utf-8"))
                if content == DISCONNECT_MSG:
                    break

        except:
            SOCKET.close()
            print("You are disconnected from the server")
            break


if __name__ == "__main__":
    Thread(target=receive).start()
    Thread(target=send).start()
