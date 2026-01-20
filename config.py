import os

SERVER_HOST = "127.0.0.1"
PORT = 65432

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

CHOICES = ["rock", "paper", "scissors"]
CHOICES_VN = {
    "rock": "Búa",
    "paper": "Bao",
    "scissors": "Kéo"
}
