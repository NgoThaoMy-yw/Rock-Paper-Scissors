import random
from config import CHOICES
from game_logic import determine_winner, format_choice
from player_manager import update_score
from utils import send, recv_line, log

def play_pve(conn, username):
    score = 0
    log(f"[PvE START] {username}")

    send(conn, "SYS:MATCH_START")
    send(conn, "TEXT:PvE – Chơi với máy")

   while True:
        send(conn, "SYS:ASK_MOVE")
        choice = recv_line(conn)

        if choice in (None, "quit", "quit_round"):
            send(conn, "SYS:MATCH_END")
            return

        if choice not in CHOICES:
            send(conn, "TEXT:Lựa chọn không hợp lệ")
            continue

        bot = random.choice(CHOICES)
        send(conn, f"OPPONENT_CHOICE:{bot}")

        result, _ = determine_winner(choice, bot)
