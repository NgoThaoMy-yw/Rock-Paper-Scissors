import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk

# PATH SETUP
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from client import SocketClient

# MAIN GUI CLASS
class GameGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Búa - Bao - Kéo Multiplayer")
        self.root.geometry("1200x900")
        self.root.configure(bg="#e0f7fa")

        self.client = SocketClient()
        self.username = ""
        self.running = True

        self.images = self.load_images()

        self.current_frame = None
        self.player_choice_label = None
        self.opponent_choice_label = None
        self.vs_label = None
        self.result_overlay = None
        self.text_result = None
        self.waiting_label = None
        self.waiting_dots = 0
        self.countdown_label = None
        self.last_effect_text = ""

        self.setup_login_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_game)
        self.root.mainloop()

    # IMAGE LOADER
    def load_images(self):
        assets = os.path.join(PROJECT_ROOT, "assets")

        def load(name, size):
            return ImageTk.PhotoImage(
                Image.open(os.path.join(assets, name)).resize(size)
            )

        return {
            "rock": load("rock.png", (220, 220)),
            "paper": load("paper.png", (220, 220)),
            "scissors": load("scissors.png", (220, 220)),
            "vs": load("vs.png", (150, 150)),
            "rock_btn": load("rock.png", (100, 100)),
            "paper_btn": load("paper.png", (100, 100)),
            "scissors_btn": load("scissors.png", (100, 100)),
        }

    # CORE HELPERS
    def clear_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.current_frame.pack(expand=True, fill="both")

    def safe_ui(self, fn, *args):
        self.root.after(0, lambda: fn(*args))

    # LOGIN
    def setup_login_screen(self):
        self.clear_screen()

        tk.Label(
            self.current_frame,
            text="BÚA - BAO - KÉO\nMULTIPLAYER",
            font=("Arial", 36, "bold"),
            bg="#e0f7fa",
            fg="#00695c",
        ).pack(pady=100)

        self.entry_username = tk.Entry(
            self.current_frame, font=("Arial", 18), width=25, justify="center"
        )
        self.entry_username.pack(pady=20)
        self.entry_username.focus()

        tk.Button(
            self.current_frame,
            text="KẾT NỐI SERVER",
            font=("Arial", 18, "bold"),
            bg="#009688",
            fg="white",
            width=20,
            height=2,
            command=self.connect_server,
        ).pack(pady=40)

        tk.Button(
            self.current_frame,
            text="THOÁT",
            font=("Arial", 14),
            bg="#c62828",
            fg="white",
            width=12,
            command=self.exit_game,
        ).pack(pady=10)

    # CONNECT
    def connect_server(self):
        self.username = self.entry_username.get().strip() or "Guest"

        if not self.client.connect():
            messagebox.showerror("Lỗi", "Không kết nối được server")
            return

        threading.Thread(target=self.listen_server, daemon=True).start()

    # MODE MENU
    def show_mode_selection(self):
        self.clear_screen()

        tk.Label(
            self.current_frame,
            text=f"Xin chào {self.username}",
            font=("Arial", 32, "bold"),
            bg="#e0f7fa",
        ).pack(pady=80)

        tk.Button(
            self.current_frame,
            text="CHƠI PvE",
            font=("Arial", 20),
            width=25,
            command=lambda: self.client.send_line("1"),
        ).pack(pady=15)

        tk.Button(
            self.current_frame,
            text="CHƠI PvP",
            font=("Arial", 20),
            width=25,
            command=self.start_pvp_waiting,
        ).pack(pady=15)

        tk.Button(
            self.current_frame,
            text="THOÁT GAME",
            font=("Arial", 16),
            bg="#c62828",
            fg="white",
            width=20,
            command=self.exit_game,
        ).pack(pady=40)

    # WAITING PvP
    def start_pvp_waiting(self):
        self.show_waiting_screen()
        self.client.send_line("2")

    def show_waiting_screen(self):
        self.clear_screen()
        self.waiting_dots = 0

        self.waiting_label = tk.Label(
            self.current_frame,
            text="Đang tìm đối thủ",
            font=("Arial", 30, "bold"),
            bg="#e0f7fa",
            fg="#00695c",
        )
        self.waiting_label.pack(expand=True)

        tk.Button(
            self.current_frame,
            text="VỀ TRANG CHỦ",
            font=("Arial", 16),
            bg="#546e7a",
            fg="white",
            width=18,
            command=self.back_to_home,
        ).pack(pady=30)

        self.animate_waiting()

    def animate_waiting(self):
        if (
            not self.running
            or not self.waiting_label
            or not self.waiting_label.winfo_exists()
        ):
            return

        self.waiting_dots = (self.waiting_dots + 1) % 4
        self.waiting_label.config(
            text="Đang tìm đối thủ" + "." * self.waiting_dots
        )
        self.root.after(500, self.animate_waiting)

    # GAME SCREEN
    def show_game_screen(self):
        self.clear_screen()

        main = tk.Frame(self.current_frame, bg="#e0f7fa")
        main.pack(expand=True, fill="both")

        self.text_result = scrolledtext.ScrolledText(
            main, height=7, font=("Arial", 11), state="disabled"
        )
        self.text_result.pack(fill="x", pady=5)

        display = tk.Frame(main, bg="#e0f7fa")
        display.pack(expand=True)

        self.player_choice_label = tk.Label(display, bg="#e0f7fa")
        self.player_choice_label.grid(row=0, column=0, padx=50)

        self.vs_label = tk.Label(display, image=self.images["vs"], bg="#e0f7fa")
        self.vs_label.grid(row=0, column=1)

        self.result_overlay = tk.Label(
            display, font=("Arial", 40, "bold"), bg="#e0f7fa"
        )
        self.result_overlay.grid(row=0, column=1)
        self.result_overlay.grid_remove()

        self.opponent_choice_label = tk.Label(display, bg="#e0f7fa")
        self.opponent_choice_label.grid(row=0, column=2, padx=50)

        self.countdown_label = tk.Label(
            display,
            font=("Arial", 36, "bold"),
            bg="#e0f7fa",
            fg="#455a64"
        )
        self.countdown_label.grid(row=1, column=1, pady=10)
        self.countdown_label.grid_remove()


        btns = tk.Frame(main, bg="#e0f7fa")
        btns.pack(pady=10)

        for c in ("rock", "paper", "scissors"):
            tk.Button(
                btns,
                image=self.images[f"{c}_btn"],
                command=lambda x=c: self.send_choice(x),
            ).pack(side="left", padx=20)

        # ---------- CONTROL BUTTONS ----------
        control = tk.Frame(main, bg="#e0f7fa")
        control.pack(pady=20)

        tk.Button(
            control,
            text="VỀ TRANG CHỦ",
            font=("Arial", 14),
            bg="#546e7a",
            fg="white",
            width=16,
            command=self.back_to_home,
        ).pack(side="left", padx=20)

        tk.Button(
            control,
            text="THOÁT GAME",
            font=("Arial", 14),
            bg="#c62828",
            fg="white",
            width=16,
            command=self.exit_game,
        ).pack(side="left", padx=20)

    # NETWORK
    def listen_server(self):
        while self.running:
            cmd, payload = self.client.recv_message()
            if not cmd:
                break

            if cmd == "SYS":
                self.handle_sys(payload)
            elif cmd == "TEXT":
                self.safe_ui(self.update_result, payload)
            elif cmd == "OPPONENT_CHOICE":
                self.safe_ui(self.show_opponent_choice, payload)
            elif cmd == "EFFECT":
                self.safe_ui(self.trigger_effect, payload)
            elif cmd == "COUNTDOWN":
                try:
                    self.safe_ui(self.start_countdown, int(payload))
                except:
                    pass

        self.running = False

    # SYS
    def handle_sys(self, payload):
        if payload == "ASK_NAME":
            self.client.send_line(self.username)
        elif payload == "ASK_MODE":
            self.safe_ui(self.show_mode_selection)
        elif payload == "MATCH_START":
            self.safe_ui(self.show_game_screen)
        elif payload == "ASK_MOVE":
            self.safe_ui(self.update_result, "Hãy chọn Búa / Bao / Kéo")

    # GAME LOGIC UI
    def update_result(self, text):
        if not self.text_result:
            return
        self.text_result.config(state="normal")
        self.text_result.insert("end", text + "\n")
        self.text_result.see("end")
        self.text_result.config(state="disabled")

    def send_choice(self, choice):
        self.client.send_line(choice)
        self.player_choice_label.config(image=self.images[choice])

    def show_opponent_choice(self, choice):
        self.opponent_choice_label.config(image=self.images.get(choice))

    def trigger_effect(self, status):
        text = {"WIN": "THẮNG", "LOSE": "THUA", "DRAW": "HÒA"}[status]
        color = {"WIN": "green", "LOSE": "red", "DRAW": "orange"}[status]

        self.last_effect_text = text

        self.vs_label.grid_remove()
        self.result_overlay.config(text=text, fg=color)
        self.result_overlay.grid()

    def start_countdown(self, sec):
        if sec > 0:
            self.countdown_label.config(text=f"Vòng mới sau {sec}")
            self.countdown_label.grid()
            self.root.after(1000, lambda: self.start_countdown(sec - 1))
        else:
            self.countdown_label.grid_remove()
            self.result_overlay.grid_remove()
            self.vs_label.grid()

            self.player_choice_label.config(image="")
            self.opponent_choice_label.config(image="")

    # NAVIGATION
    def back_to_home(self):
        try:
            self.client.send_line("quit_round")
        except:
            pass
        self.safe_ui(self.show_mode_selection)

    def exit_game(self):
        self.running = False
        try:
            self.client.send_line("quit")
        except:
            pass
        self.client.close()
        self.root.after(100, self.root.destroy)


# ENTRY
if __name__ == "__main__":
    GameGUI()
