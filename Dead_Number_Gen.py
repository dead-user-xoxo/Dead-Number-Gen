import os
import json
import random
import tkinter as tk

SEEN_FILE = os.path.join(os.path.expanduser("~"), ".random_phone_gen_seen.json")

rng = random.SystemRandom()


def load_seen():
    """Load the set of previously generated numbers from disk."""
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return set(data)
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        pass
    return set()


def save_seen(seen_set):
    """Persist the set of generated numbers to disk (best effort)."""
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_set), f)
    except OSError:
        
        pass



def rand_digit():
    return str(rng.randint(0, 9))


def rand_digits(n):
    return "".join(rand_digit() for _ in range(n))



def gen_usa_ca():
    
    while True:
        area = str(rng.randint(2, 9)) + rand_digits(2)
        if area[1:] != "11":  # avoid N11 codes like 411/911
            break
    exchange = str(rng.randint(2, 9)) + rand_digits(2)
    line = rand_digits(4)
    return f"+1 ({area}) {exchange}-{line}"


def gen_uk():
    return f"+44 7{rand_digits(3)} {rand_digits(6)}"


def gen_australia():
    return f"+61 4{rand_digits(2)} {rand_digits(3)} {rand_digits(3)}"


def gen_germany():
    return f"+49 1{rand_digits(2)} {rand_digits(7)}"


def gen_france():
    first = rng.choice(["6", "7"])
    return f"+33 {first}{rand_digits(2)} {rand_digits(3)} {rand_digits(3)}"


def gen_italy():
    return f"+39 3{rand_digits(2)} {rand_digits(3)} {rand_digits(4)}"


def gen_spain():
    return f"+34 6{rand_digits(2)} {rand_digits(3)} {rand_digits(3)}"


def gen_japan():
    return f"+81 90-{rand_digits(4)}-{rand_digits(4)}"


def gen_china():
    return f"+86 1{rand_digits(2)} {rand_digits(4)} {rand_digits(4)}"


def gen_india():
    first = rng.choice(["6", "7", "8", "9"])
    return f"+91 {first}{rand_digits(4)} {rand_digits(5)}"


def gen_brazil():
    area = str(rng.randint(11, 99))
    return f"+55 ({area}) 9{rand_digits(4)}-{rand_digits(4)}"


def gen_mexico():
    return f"+52 {rand_digits(3)} {rand_digits(3)} {rand_digits(4)}"


def gen_russia():
    return f"+7 9{rand_digits(2)} {rand_digits(3)}-{rand_digits(2)}-{rand_digits(2)}"


def gen_south_korea():
    return f"+82 10-{rand_digits(4)}-{rand_digits(4)}"


def gen_netherlands():
    return f"+31 6 {rand_digits(8)}"


def gen_sweden():
    return f"+46 7{rand_digits(1)} {rand_digits(3)} {rand_digits(2)} {rand_digits(2)}"


def gen_switzerland():
    return f"+41 7{rand_digits(1)} {rand_digits(3)} {rand_digits(2)} {rand_digits(2)}"


def gen_ireland():
    return f"+353 8{rand_digits(1)} {rand_digits(3)} {rand_digits(4)}"


def gen_new_zealand():
    return f"+64 2{rand_digits(1)} {rand_digits(3)} {rand_digits(4)}"


def gen_south_africa():
    return f"+27 {rand_digits(2)} {rand_digits(3)} {rand_digits(4)}"


def gen_uae():
    return f"+971 5{rand_digits(1)} {rand_digits(3)} {rand_digits(4)}"


def gen_singapore():
    first = rng.choice(["8", "9"])
    return f"+65 {first}{rand_digits(3)} {rand_digits(4)}"


def gen_turkey():
    return f"+90 5{rand_digits(2)} {rand_digits(3)} {rand_digits(2)} {rand_digits(2)}"


def gen_argentina():
    return f"+54 9 11 {rand_digits(4)}-{rand_digits(4)}"


COUNTRIES = [
    {"name": "USA", "gen": gen_usa_ca},
    {"name": "UK", "gen": gen_uk},
    {"name": "Canada", "gen": gen_usa_ca},
    {"name": "Australia", "gen": gen_australia},
    {"name": "Germany", "gen": gen_germany},
    {"name": "France", "gen": gen_france},
    {"name": "Italy", "gen": gen_italy},
    {"name": "Spain", "gen": gen_spain},
    {"name": "Japan", "gen": gen_japan},
    {"name": "China", "gen": gen_china},
    {"name": "India", "gen": gen_india},
    {"name": "Brazil", "gen": gen_brazil},
    {"name": "Mexico", "gen": gen_mexico},
    {"name": "Russia", "gen": gen_russia},
    {"name": "South Korea", "gen": gen_south_korea},
    {"name": "Netherlands", "gen": gen_netherlands},
    {"name": "Sweden", "gen": gen_sweden},
    {"name": "Switzerland", "gen": gen_switzerland},
    {"name": "Ireland", "gen": gen_ireland},
    {"name": "New Zealand", "gen": gen_new_zealand},
    {"name": "South Africa", "gen": gen_south_africa},
    {"name": "UAE", "gen": gen_uae},
    {"name": "Singapore", "gen": gen_singapore},
    {"name": "Turkey", "gen": gen_turkey},
    {"name": "Argentina", "gen": gen_argentina},
]

BG = "black"
FG = "red"


# ------------------------------------------------------------------
# Main application
# ------------------------------------------------------------------
class PhoneNumberGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dead Phone Gen")
        self.root.geometry("480x620")
        self.root.minsize(420, 480)
        self.root.configure(bg=BG)

        self.seen_numbers = load_seen()
        self.current_country = None
        self.loading_after_id = None
        self.copy_status_after_id = None

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(expand=True, fill="both")

        self.show_country_list()

    # ---------------- frame / state management ----------------
    def clear_container(self):
        # Cancel any pending scheduled callbacks so a stale loading
        # animation or copy-status reset can't fire on a new screen.
        if self.loading_after_id is not None:
            try:
                self.root.after_cancel(self.loading_after_id)
            except Exception:
                pass
            self.loading_after_id = None

        if self.copy_status_after_id is not None:
            try:
                self.root.after_cancel(self.copy_status_after_id)
            except Exception:
                pass
            self.copy_status_after_id = None

        # Remove mouse-wheel bindings from the country list screen so
        # they don't linger and act on a destroyed widget elsewhere.
        self.root.unbind_all("<MouseWheel>")
        self.root.unbind_all("<Button-4>")
        self.root.unbind_all("<Button-5>")

        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------------- screen: country list ----------------
    def show_country_list(self):
        self.current_country = None
        self.clear_container()

        tk.Label(
            self.container, text="Dead Phone Gen",
            font=("Helvetica", 28, "bold"), bg=BG, fg=FG
        ).pack(pady=(20, 0))

        tk.Label(
            self.container, text="Select a Country",
            font=("Helvetica", 20, "bold"), bg=BG, fg=FG
        ).pack(pady=(5, 10))

        list_area = tk.Frame(self.container, bg=BG)
        list_area.pack(expand=True, fill="both", padx=15, pady=(0, 15))

        canvas = tk.Canvas(list_area, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            list_area, orient="vertical", command=canvas.yview,
            bg=BG, troughcolor=BG, activebackground=FG
        )
        list_frame = tk.Frame(canvas, bg=BG)

        list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            delta = event.delta
            if delta:
                canvas.yview_scroll(int(-1 * (delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)          # Windows / macOS
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux

        for idx, country in enumerate(COUNTRIES, start=1):
            btn = tk.Button(
                list_frame,
                text=f"{idx}. {country['name']}",
                font=("Helvetica", 13),
                bg=BG, fg=FG,
                activebackground=FG, activeforeground=BG,
                relief="solid", bd=1,
                width=28, anchor="w",
                command=lambda c=country: self.select_country(c),
            )
            # pady here gives the "spaces between" the user asked for
            btn.pack(pady=6, padx=6, fill="x")

    def select_country(self, country):
        self.current_country = country
        self.show_loading()

    # ---------------- screen: loading ----------------
    def show_loading(self):
        self.clear_container()

        country = self.current_country
        wrapper = tk.Frame(self.container, bg=BG)
        wrapper.pack(expand=True, fill="both")

        tk.Label(
            wrapper, text=country["name"] if country else "",
            font=("Helvetica", 22, "bold"), bg=BG, fg=FG
        ).pack(pady=(70, 10))

        tk.Label(
            wrapper, text="Loading...",
            font=("Helvetica", 18), bg=BG, fg=FG
        ).pack(pady=(0, 25))

        self.status_label = tk.Label(
            wrapper, text="Status: starting up...",
            font=("Helvetica", 12), bg=BG, fg=FG
        )
        self.status_label.pack(pady=10)

        self._loading_messages = [
            "Status: connecting to the network...",
            "Status: making number...",
            "Status: checking the format...",
            "Status: making sure it's unique...",
            "Status: finalizing...",
        ]
        self._loading_step = 0
        self.loading_after_id = self.root.after(250, self.advance_loading)

    def advance_loading(self):
        # Guard: if the user somehow navigated away, do nothing.
        if not hasattr(self, "status_label") or not self.status_label.winfo_exists():
            return

        if self._loading_step < len(self._loading_messages):
            self.status_label.config(text=self._loading_messages[self._loading_step])
            self._loading_step += 1
            self.loading_after_id = self.root.after(350, self.advance_loading)
        else:
            self.loading_after_id = None
            self.generate_and_show()

    # ---------------- number generation ----------------
    def generate_unique_number(self, country):
        candidate = country["gen"]()
        attempts = 0
        # Try until we get one never seen before (extremely likely on
        # the first try given the size of the number space).
        while candidate in self.seen_numbers and attempts < 5000:
            candidate = country["gen"]()
            attempts += 1
        self.seen_numbers.add(candidate)
        save_seen(self.seen_numbers)
        return candidate

    def generate_and_show(self):
        country = self.current_country
        if country is None:
            # Safety net: shouldn't happen, but never crash.
            self.show_country_list()
            return
        number = self.generate_unique_number(country)
        self.show_result(country, number)

    # ---------------- screen: result ----------------
    def show_result(self, country, number):
        self.clear_container()
        wrapper = tk.Frame(self.container, bg=BG)
        wrapper.pack(expand=True, fill="both")

        tk.Label(
            wrapper, text=country["name"],
            font=("Helvetica", 22, "bold"), bg=BG, fg=FG
        ).pack(pady=(50, 20))

        tk.Label(
            wrapper, text=number,
            font=("Helvetica", 20, "bold"), bg=BG, fg=FG
        ).pack(pady=10)

        self.copy_status = tk.Label(
            wrapper, text="", font=("Helvetica", 10), bg=BG, fg=FG
        )
        self.copy_status.pack(pady=(0, 20))

        btn_frame = tk.Frame(wrapper, bg=BG)
        btn_frame.pack(pady=20)

        def make_btn(parent, text, cmd, col):
            b = tk.Button(
                parent, text=text, font=("Helvetica", 12),
                bg=BG, fg=FG, activebackground=FG, activeforeground=BG,
                relief="solid", bd=1, width=12, command=cmd,
            )
            b.grid(row=0, column=col, padx=8, pady=6)
            return b

        make_btn(btn_frame, "Copy", lambda: self.copy_to_clipboard(number), 0)
        make_btn(btn_frame, "Regenerate", self.regenerate, 1)
        make_btn(btn_frame, "Back", self.go_back, 2)

    def regenerate(self):
        # Uses self.current_country, which is still set to whatever
        # country the user picked -- so regenerate always stays on
        # the same country and shows the loading screen again.
        if self.current_country is None:
            self.show_country_list()
            return
        self.show_loading()

    def go_back(self):
        # Clear the country before returning, so picking a new one
        # afterwards can never accidentally reuse the old selection.
        self.current_country = None
        self.show_country_list()

    def copy_to_clipboard(self, number):
        self.root.clipboard_clear()
        self.root.clipboard_append(number)
        self.root.update()  # required on some platforms to keep clipboard content
        if hasattr(self, "copy_status") and self.copy_status.winfo_exists():
            self.copy_status.config(text="Copied to clipboard!")
            self.copy_status_after_id = self.root.after(1500, self._clear_copy_status)

    def _clear_copy_status(self):
        self.copy_status_after_id = None
        if hasattr(self, "copy_status") and self.copy_status.winfo_exists():
            self.copy_status.config(text="")


def main():
    root = tk.Tk()
    PhoneNumberGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()