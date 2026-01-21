import time
from config import CHOICES
from game_logic import determine_winner
from player_manager import update_score
from utils import send, recv_line, log

def handle_pvp_room(c1, n1, c2, n2):
    log(f"[PvP START] {n1} vs {n2}")

    send(c1, "SYS:MATCH_START")
    send(c2, "SYS:MATCH_START")

    while True:
        send(c1, "SYS:ASK_MOVE")
        send(c2, "SYS:ASK_MOVE")

        a = recv_line(c1)
        b = recv_line(c2)

        if a in (None, "quit", "quit_round") or b in (None, "quit", "quit_round"):
            break

        if a not in CHOICES or b not in CHOICES:
            continue

        send(c1, f"OPPONENT_CHOICE:{b}")
        send(c2, f"OPPONENT_CHOICE:{a}")

        winner, _ = determine_winner(a, b)

        if winner == "p1":
            update_score(n1, 1)
            send(c1, "EFFECT:WIN")
            send(c2, "EFFECT:LOSE")
        elif winner == "p2":
            update_score(n2, 1)
            send(c1, "EFFECT:LOSE")
            send(c2, "EFFECT:WIN")
        else:
            send(c1, "EFFECT:DRAW")
            send(c2, "EFFECT:DRAW")

        send(c1, "COUNTDOWN:3")
        send(c2, "COUNTDOWN:3")
        time.sleep(3)

    send(c1, "SYS:MATCH_END")
    send(c2, "SYS:MATCH_END")
    c1.close()
    c2.close()
    log(f"[PvP END] {n1} vs {n2}")
