import socket
import pickle
from threading import Thread
from user import User

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "192.168.1.16"
PORT = 5500
MAX_CONNECTIONS = 10
HEADERSIZE = 10
DISCONNECT_MSG = "{DISCONNECT}"

SERVER_SOCKET.bind((HOST, PORT))
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

active_users = []


def disconnect_client(user):
    user.CLIENT_SOCKET.close()
    print(f"{user.ADDRESS} disconnected")
    broadcast(f"{user.name} disconnected", user)

    i = 0
    for active_user in active_users:
        if active_user.identifier == user.identifier:
            del active_users[i]
            break
        i = i + 1


def broadcast(msg, sender):
    if not len(msg):
        return

    data = {
        'sender_name': sender.name,
        'message': msg
    }
    message = pickle.dumps(data)
    message = bytes(f"{len(message):<{HEADERSIZE}}", "utf-8") + message

    for active_user in active_users:
        if active_user is not sender:
            active_user.CLIENT_SOCKET.send(message)


def handle_communication(user):
    CLIENT_SOCKET = user.CLIENT_SOCKET
    new_user = True
    new_msg = True
    full_msg = ''

    while True:
        try:
            msg = CLIENT_SOCKET.recv(HEADERSIZE).decode("utf-8")
            if len(msg):
                if new_msg:
                    full_msg_len = int(msg)
                    new_msg = False
                else:
                    full_msg += msg

                if len(full_msg) == full_msg_len:
                    if full_msg == DISCONNECT_MSG:
                        disconnect_client(user)
                        break

                    elif new_user:
                        user.set_name(full_msg)
                        new_user = False

                    else:
                        broadcast(full_msg, user)

                    full_msg = ""
                    new_msg = True

        except KeyboardInterrupt:
            print("Shutting down server")
            CLIENT_SOCKET.close()
            break

        except Exception as e:
            print(f"[EXCEPTION] {e}")
            disconnect_client(user)
            break


def wait_for_connection():
    while True:
        try:
            CLIENT_SOCKET, ADDRESS = SERVER_SOCKET.accept()
            user = User(CLIENT_SOCKET, ADDRESS)
            print(user.ADDRESS)
            active_users.append(user)
            print(f"[NEW_CONNECTION] {ADDRESS}")

            Thread(target=handle_communication, args=(user,)).start()

        except KeyboardInterrupt:
            print("Shutting down server")
            SERVER_SOCKET.close()

        except Exception as e:
            print(f"[EXCEPTION] {e}")
            break


if __name__ == "__main__":
    SERVER_SOCKET.listen(MAX_CONNECTIONS)
    print("[STARTED] Waiting for client(s) to connect")

    ACCEPT_THREAD = Thread(target=wait_for_connection)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()

    SERVER_SOCKET.close()
