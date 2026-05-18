import tkinter as tk
from tkinter import messagebox
import math

X     = "X"
O     = "O"
EMPTY = None

WINS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
    (0, 4, 8), (2, 4, 6),             # diagonales
]

def Player(s: list) -> str:
    """Retorna el jugador cuyo turno es (X o O)."""
    return X if s.count(X) <= s.count(O) else O


def Actions(s: list) -> list:
    """Retorna lista de índices de celdas vacías."""
    return [i for i, c in enumerate(s) if c is EMPTY]


def Result(s: list, a: int) -> list:
    """Aplica la acción a en el estado s y retorna nuevo estado."""
    ns = s[:]
    ns[a] = Player(s)
    return ns


def winner(s: list):
    """Retorna el ganador (X/O) o None."""
    for a, b, c in WINS:
        if s[a] and s[a] == s[b] == s[c]:
            return s[a]
    return None


def Terminal(s: list) -> bool:
    """True si el juego terminó (hay ganador o no hay movimientos)."""
    return winner(s) is not None or len(Actions(s)) == 0


def Utility(s: list, ai_player: str) -> int:
    """
    Evalúa el estado terminal:
      +1  si gana la IA
      -1  si gana el humano
       0  empate
    """
    w = winner(s)
    if w == ai_player:
        return 1
    elif w is not None:
        return -1
    return 0


def winning_line(s: list):
    """Retorna la tupla (a,b,c) ganadora o None."""
    for combo in WINS:
        a, b, c = combo
        if s[a] and s[a] == s[b] == s[c]:
            return combo
    return None

def minimax(s: list, alpha: float, beta: float,
            is_max: bool, ai_player: str) -> tuple:
    """
    Algoritmo Minimax con poda Alpha-Beta.
    Retorna (score, mejor_acción).
    """
    if Terminal(s):
        return Utility(s, ai_player), None

    best_action = None

    if is_max:
        best_score = -math.inf
        for a in Actions(s):
            score, _ = minimax(Result(s, a), alpha, beta, False, ai_player)
            if score > best_score:
                best_score, best_action = score, a
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
    else:
        best_score = math.inf
        for a in Actions(s):
            score, _ = minimax(Result(s, a), alpha, beta, True, ai_player)
            if score < best_score:
                best_score, best_action = score, a
            beta = min(beta, best_score)
            if alpha >= beta:
                break

    return best_score, best_action


def best_move(s: list, ai_player: str) -> int:
    """Retorna el mejor movimiento para la IA."""
    _, action = minimax(s, -math.inf, math.inf, True, ai_player)
    return action

class TresEnRaya:

    # Paleta de colores
    BG          = "#F8F7F4"
    SURFACE     = "#FFFFFF"
    BORDER      = "#E0DED8"
    TEXT_MAIN   = "#1A1A1A"
    TEXT_MUTED  = "#6B6B6B"
    BLUE_FILL   = "#EBF3FC"
    BLUE_TEXT   = "#1A5F9E"
    RED_FILL    = "#FCEAEA"
    RED_TEXT    = "#A32D2D"
    GREEN_FILL  = "#EAF5EF"
    GREEN_TEXT  = "#2E7D4F"
    AMBER_TEXT  = "#7A4F0B"
    CELL_HOVER  = "#F0EEE8"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TRES EN RAYA")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)

        # Estado
        self.board       = [EMPTY] * 9
        self.human       = X
        self.ai          = O
        self.game_over   = False
        self.scores      = {X: 0, O: 0, "D": 0}
        self.buttons     = []

        self._build_ui()
        self._new_game()

    def _build_ui(self):
        pad = dict(padx=20, pady=10)

        # Título
        tk.Label(
            self.root, text="Tres en Raya",
            font=("Helvetica Neue", 22, "bold"),
            bg=self.BG, fg=self.TEXT_MAIN
        ).pack(pady=(20, 0))

        tk.Label(
            self.root, text="HMMM X Y O",
            font=("Helvetica Neue", 11),
            bg=self.BG, fg=self.TEXT_MUTED
        ).pack(pady=(2, 12))

        # Selector de jugador
        sel_frame = tk.Frame(self.root, bg=self.BG)
        sel_frame.pack()
        tk.Label(sel_frame, text="Jugar como:", bg=self.BG,
                 fg=self.TEXT_MUTED, font=("Helvetica Neue", 12)).pack(side=tk.LEFT, padx=4)
        self.player_var = tk.StringVar(value=X)
        for val, label in [(X, "❌ X (primero)"), (O, "⭕ O (segundo)")]:
            tk.Radiobutton(
                sel_frame, text=label, variable=self.player_var,
                value=val, bg=self.BG, fg=self.TEXT_MAIN,
                font=("Helvetica Neue", 12), activebackground=self.BG,
                command=self._new_game
            ).pack(side=tk.LEFT, padx=8)

        # Marcador
        score_frame = tk.Frame(self.root, bg=self.BG)
        score_frame.pack(pady=12)
        self.lbl_score_x = self._pill(score_frame, "❌  0", self.RED_FILL, self.RED_TEXT)
        self.lbl_score_d = self._pill(score_frame, "🤝  0", "#F1EFE8", self.TEXT_MUTED)
        self.lbl_score_o = self._pill(score_frame, "⭕  0", self.BLUE_FILL, self.BLUE_TEXT)
        for w in [self.lbl_score_x, self.lbl_score_d, self.lbl_score_o]:
            w.pack(side=tk.LEFT, padx=6)

        # Estado
        self.lbl_status = tk.Label(
            self.root, text="", font=("Helvetica Neue", 13),
            bg=self.BG, fg=self.TEXT_MUTED, height=1
        )
        self.lbl_status.pack(pady=(0, 8))

        # Tablero
        board_frame = tk.Frame(self.root, bg=self.BG)
        board_frame.pack(**pad)
        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                board_frame, text="", font=("Helvetica Neue", 36),
                width=3, height=1,
                bg=self.SURFACE, fg=self.TEXT_MAIN,
                relief=tk.FLAT, bd=0,
                highlightthickness=1, highlightbackground=self.BORDER,
                activebackground=self.CELL_HOVER,
                command=lambda idx=i: self._human_move(idx)
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5,
                     ipadx=8, ipady=8)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
            self.buttons.append(btn)

        ctrl = tk.Frame(self.root, bg=self.BG)
        ctrl.pack(pady=(8, 4))
        tk.Button(
            ctrl, text="Nueva partida",
            font=("Helvetica Neue", 12), bg=self.BLUE_FILL,
            fg=self.BLUE_TEXT, relief=tk.FLAT, bd=0,
            padx=16, pady=6, cursor="hand2",
            activebackground="#d6e9f8",
            command=self._new_game
        ).pack(side=tk.LEFT, padx=6)
        tk.Button(
            ctrl, text="Ver metodo activo",
            font=("Helvetica Neue", 12), bg=self.SURFACE,
            fg=self.TEXT_MUTED, relief=tk.FLAT, bd=0,
            padx=16, pady=6, cursor="hand2",
            highlightthickness=1, highlightbackground=self.BORDER,
            activebackground=self.CELL_HOVER,
            command=self._show_info
        ).pack(side=tk.LEFT, padx=6)

        self.info_frame = tk.LabelFrame(
            self.root, text="  mas?  ",
            font=("Helvetica Neue", 11), bg=self.BG,
            fg=self.TEXT_MUTED, bd=1, relief=tk.SOLID,
            labelanchor="n"
        )
        self.lbl_info = tk.Label(
            self.info_frame, text="", font=("Courier New", 10),
            bg=self.BG, fg=self.TEXT_MAIN, justify=tk.LEFT, padx=12, pady=8
        )
        self.lbl_info.pack()
        self.info_visible = False

        tk.Label(self.root, text="", bg=self.BG).pack(pady=4)

    def _pill(self, parent, text, bg, fg):
        return tk.Label(
            parent, text=text, bg=bg, fg=fg,
            font=("Helvetica Neue", 13, "bold"),
            padx=14, pady=4,
            relief=tk.FLAT, bd=0
        )

    def _on_hover(self, btn, entering):
        if btn["state"] == tk.NORMAL and btn["text"] == "":
            btn.configure(bg=self.CELL_HOVER if entering else self.SURFACE)

    def _new_game(self):
        self.human     = self.player_var.get()
        self.ai        = O if self.human == X else X
        self.board     = [EMPTY] * 9
        self.game_over = False
        for btn in self.buttons:
            btn.configure(text="", bg=self.SURFACE,
                          fg=self.TEXT_MAIN, state=tk.NORMAL)
        self._set_status("Tu turno" if Player(self.board) == self.human
                         else "IA pensando…")
        if Player(self.board) == self.ai:
            self.root.after(400, self._ai_move)

    def _human_move(self, idx):
        if self.game_over or self.board[idx] or Player(self.board) != self.human:
            return
        self.board[idx] = self.human
        sym = "❌" if self.human == X else "⭕"
        self.buttons[idx].configure(text=sym, state=tk.DISABLED,
                                    disabledforeground=self.TEXT_MAIN)
        if self._check_end():
            return
        self._set_status("IA pensando…")
        self.root.after(300, self._ai_move)

    def _ai_move(self):
        move = best_move(self.board, self.ai)
        if move is None:
            self._check_end()
            return
        self.board[move] = self.ai
        sym = "⭕" if self.ai == O else "❌"
        self.buttons[move].configure(text=sym, state=tk.DISABLED,
                                     disabledforeground=self.TEXT_MAIN)
        if self._check_end():
            return
        self._set_status("Tu turno")

    def _check_end(self) -> bool:
        w    = winner(self.board)
        line = winning_line(self.board)

        if w:
            self._highlight_win(line, w)
            if w == self.human:
                self.scores[self.human] += 1
                self._set_status("🎉 ¡Ganaste!")
            else:
                self.scores[self.ai] += 1
                self._set_status("😤 Ganó la IA")
            self._update_score()
            self.game_over = True
            self._disable_all()
            return True

        if Terminal(self.board):
            self.scores["D"] += 1
            self._set_status("🤝 Empate")
            self._update_score()
            self.game_over = True
            return True

        return False

    def _highlight_win(self, line, w):
        fill = self.GREEN_FILL if w == self.human else self.RED_FILL
        fg   = self.GREEN_TEXT if w == self.human else self.RED_TEXT
        for i in line:
            self.buttons[i].configure(bg=fill, disabledforeground=fg)

    def _disable_all(self):
        for btn in self.buttons:
            btn.configure(state=tk.DISABLED)

    def _set_status(self, msg):
        self.lbl_status.configure(text=msg)

    def _update_score(self):
        hx = self.scores[self.human]
        ao = self.scores[self.ai]
        d  = self.scores["D"]
        self.lbl_score_x.configure(text=f"❌  {hx}")
        self.lbl_score_o.configure(text=f"⭕  {ao}")
        self.lbl_score_d.configure(text=f"🤝  {d}")

    def _show_info(self):
        if self.info_visible:
            self.info_frame.pack_forget()
            self.info_visible = False
            return

        s = self.board
        p = Player(s)
        acts = Actions(s)
        term = Terminal(s)
        util = Utility(s, self.ai)

        info = (
            f"  Player(s)   = {p!r:5}  → jugador actual\n"
            f"  Actions(s)  = {acts}  → celdas libres\n"
            f"  Terminal(s) = {term!s:5}  → ¿juego terminado?\n"
            f"  Utility(s)  = {util:+d}       → valor del estado actual\n"
            f"\n"
            f"  Minimax     + Alpha-Beta Pruning activo\n"
            f"  Profundidad = ilimitada (9 celdas)\n"
        )
        self.lbl_info.configure(text=info)
        self.info_frame.pack(padx=20, pady=(0, 16), fill=tk.X)
        self.info_visible = True

if __name__ == "__main__":
    root = tk.Tk()
    app  = TresEnRaya(root)
    root.mainloop()
