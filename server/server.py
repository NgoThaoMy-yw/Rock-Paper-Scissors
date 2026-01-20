import socket, threading, time
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


from config import SERVER_HOST, PORT
from utils import send, recv_line, log
from pve_handler import play_pve
from pvp_handler import handle_pvp_room

waiting_pvp = []
lock = threading.Lock()

def client_thread(conn, addr):
    log(f"[CONNECT] {addr}")
    send(conn, "SYS:ASK_NAME")
    username = recv_line(conn)
    if not username:
        conn.close()
        return

    send(conn, "SYS:ASK_MODE")
    mode = recv_line(conn)

    if mode == "1":
        play_pve(conn, username)
        return

    if mode == "2":
        with lock:
            waiting_pvp.append((conn, username))
        return   # GIAO SOCKET CHO PvP THREAD

    conn.close()

def matchmaker():
    while True:
        with lock:
            if len(waiting_pvp) >= 2:
                c1, n1 = waiting_pvp.pop(0)
                c2, n2 = waiting_pvp.pop(0)
                threading.Thread(
                    target=handle_pvp_room,
                    args=(c1, n1, c2, n2),
                    daemon=True
                ).start()
        time.sleep(0.2)

def main():
    threading.Thread(target=matchmaker, daemon=True).start()
    sock = socket.socket()
    sock.bind((SERVER_HOST, PORT))
    sock.listen()
    log("Server started")

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
