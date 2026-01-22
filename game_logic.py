from config import CHOICES_VN

def determine_winner(p1, p2):
    if p1 == p2:
        return "tie", "Hòa"
    if (
        (p1 == "rock" and p2 == "scissors") or
        (p1 == "paper" and p2 == "rock") or
        (p1 == "scissors" and p2 == "paper")
    ):
        return "p1", "Thắng"
    return "p2", "Thua"

def format_choice(choice):
    return CHOICES_VN.get(choice, choice)
