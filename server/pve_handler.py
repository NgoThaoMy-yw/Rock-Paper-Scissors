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
