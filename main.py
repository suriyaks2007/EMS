# main.py  ← RUN THIS TO START
import tkinter as tk
from tkinter import ttk
import math, random, subprocess, sys, os

try:
    from db.connection import get_cursor, get_db
    DB_OK = True
except Exception:
    DB_OK = False

# ── PALETTE ──────────────────────────────────
BG        = "#000814"
CYAN      = "#00ffff"
CYAN_DIM  = "#004d4d"
CYAN_GLOW = "#00e5e5"
CARD_BG   = "#0a0f1e"
CARD_BORDER="#00ffff"
BTN_BG    = "#06b6d4"
BTN_FG    = "#000814"
BTN_EXIT  = "#1e1e2e"
RED       = "#f87171"
GREEN     = "#4ade80"

# ── WINDOW ───────────────────────────────────
root = tk.Tk()
root.title("Event Management System — Login")
root.geometry("900x700")
root.resizable(False, False)
root.configure(bg=BG)

# ── CANVAS ───────────────────────────────────
canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

# ── NETWORK ──────────────────────────────────
W, H = 900, 700
NODE_COUNT, CONNECT_DIST, MAX_NODES = 70, 200, 110

class Node:
    def __init__(self, x=None, y=None, fast=False):
        self.x   = x if x is not None else random.uniform(0, W)
        self.y   = y if y is not None else random.uniform(0, H)
        speed    = random.uniform(0.5, 1.0) if fast else random.uniform(0.12, 0.30)
        angle    = random.uniform(0, math.tau)
        self.vx  = math.cos(angle) * speed
        self.vy  = math.sin(angle) * speed
        self.r   = random.uniform(1.5, 2.8)
        self.ttl = random.randint(320, 520) if fast else None
    def move(self):
        self.x += self.vx; self.y += self.vy
        if self.x < 0 or self.x > W: self.vx *= -1
        if self.y < 0 or self.y > H: self.vy *= -1
        if self.ttl is not None: self.ttl -= 1
    @property
    def alive(self): return self.ttl is None or self.ttl > 0

nodes = [Node() for _ in range(NODE_COUNT)]
_lids, _nids = [], []

def hex_alpha(base, a):
    r0,g0,b0 = int(BG[1:3],16),int(BG[3:5],16),int(BG[5:7],16)
    r1,g1,b1 = int(base[1:3],16),int(base[3:5],16),int(base[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(int(r0+(r1-r0)*a),int(g0+(g1-g0)*a),int(b0+(b1-b0)*a))

def on_click(e):
    if len(nodes) < MAX_NODES:
        for _ in range(4): nodes.append(Node(x=e.x, y=e.y, fast=True))

def animate():
    for i in _lids+_nids: canvas.delete(i)
    _lids.clear(); _nids.clear()
    for nd in nodes[:]:
        nd.move()
        if not nd.alive: nodes.remove(nd)
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            d = math.hypot(a.x-b.x, a.y-b.y)
            if d < CONNECT_DIST:
                t  = d/CONNECT_DIST
                al = (1+math.cos(math.pi*t))/2*0.6
                _lids.append(canvas.create_line(a.x,a.y,b.x,b.y,
                    fill=hex_alpha(CYAN,al*0.85),width=1))
    for nd in nodes:
        fade = (nd.ttl/520) if nd.ttl else 1.0
        sf   = (1+math.cos(math.pi*(1-fade)))/2
        col  = hex_alpha(CYAN_GLOW, max(0.15,sf*0.9))
        r    = nd.r*sf if nd.ttl else nd.r
        _nids.append(canvas.create_oval(nd.x-r,nd.y-r,nd.x+r,nd.y+r,fill=col,outline=""))
    canvas.tag_raise("ui")
    root.after(30, animate)

canvas.bind("<Button-1>", on_click)

# ── CORNER BRACKETS ──────────────────────────
L = 30
for cx,cy,dx,dy in [(0,0,1,1),(900,0,-1,1),(0,700,1,-1),(900,700,-1,-1)]:
    canvas.create_line(cx,cy,cx+dx*L,cy,fill=CYAN,width=2)
    canvas.create_line(cx,cy,cx,cy+dy*L,fill=CYAN,width=2)
canvas.create_text(886,690,anchor="e",text="EVENT MANAGEMENT SYSTEM  v2.0",
    font=("Courier New",9),fill=CYAN_DIM)

# ── CARD ─────────────────────────────────────
shadow = tk.Frame(canvas, bg="#003333", width=420, height=490)
sw = canvas.create_window(453,353,window=shadow)
card = tk.Frame(canvas, bg=CARD_BG, padx=44, pady=36,
                highlightthickness=2, highlightbackground=CARD_BORDER)
cw = canvas.create_window(449,349,window=card)
canvas.addtag_withtag("ui",sw); canvas.addtag_withtag("ui",cw)

# ── FONTS ─────────────────────────────────────
FT = ("Courier New",20,"bold")
FL = ("Courier New", 9,"bold")
FB = ("Courier New",10)
FN = ("Courier New",11,"bold")

# ── TITLE ────────────────────────────────────
tf = tk.Frame(card, bg=CARD_BG)
tf.pack(fill="x", pady=(0,6))
tk.Label(tf,text="◈  EVENT MANAGEMENT  ◈",font=FT,fg=CYAN_GLOW,bg=CARD_BG).pack()
tk.Label(tf,text="SYSTEM LOGIN",font=("Courier New",12,"bold"),fg=CYAN_DIM,bg=CARD_BG).pack()
tk.Frame(tf,bg=CYAN,height=1,width=320).pack(pady=(8,0))

# ── TOGGLE ───────────────────────────────────
login_type = tk.StringVar(value="user")
toggle_frame = tk.Frame(card, bg=CARD_BG)
toggle_frame.pack(fill="x", pady=(18,16))

btn_user  = tk.Button(toggle_frame,text="👤  USER", font=("Courier New",10,"bold"),
    relief="flat",bd=0,cursor="hand2",padx=16,pady=6,width=10)
btn_admin = tk.Button(toggle_frame,text="🔒  ADMIN",font=("Courier New",10,"bold"),
    relief="flat",bd=0,cursor="hand2",padx=16,pady=6,width=10)
tk.Frame(toggle_frame,bg=CARD_BG,width=30).pack(side="left")
btn_user.pack(side="left",padx=4)
btn_admin.pack(side="left",padx=4)

uid_label_var = tk.StringVar(value="  USER ID")

def set_login_type(val):
    login_type.set(val)
    if val=="user":
        btn_user.config(bg=BTN_BG,fg=BTN_FG,command=lambda:set_login_type("user"))
        btn_admin.config(bg="#1e1e2e",fg=CYAN_GLOW,command=lambda:set_login_type("admin"))
        uid_label_var.set("  USER ID")
    else:
        btn_user.config(bg="#1e1e2e",fg=CYAN_GLOW,command=lambda:set_login_type("user"))
        btn_admin.config(bg=BTN_BG,fg=BTN_FG,command=lambda:set_login_type("admin"))
        uid_label_var.set("  USERNAME")

btn_user.config(command=lambda:set_login_type("user"))
btn_admin.config(command=lambda:set_login_type("admin"))
set_login_type("user")

# ── INPUT BOX HELPER ─────────────────────────
def input_box(parent, label_var_or_str, is_password=False):
    outer = tk.Frame(parent, bg=CYAN, padx=1, pady=1)
    outer.pack(fill="x", pady=(0,14))
    inner = tk.Frame(outer, bg="#020c1b")
    inner.pack(fill="both")
    if isinstance(label_var_or_str, str):
        tk.Label(inner,text=f"  {label_var_or_str}",font=FL,
                 fg=CYAN_DIM,bg="#020c1b",anchor="w").pack(fill="x",pady=(4,0))
    else:
        tk.Label(inner,textvariable=label_var_or_str,font=FL,
                 fg=CYAN_DIM,bg="#020c1b",anchor="w").pack(fill="x",pady=(4,0))
    e = tk.Entry(inner,font=FB,fg=CYAN_GLOW,bg="#020c1b",
                 insertbackground=CYAN,relief="flat",bd=0,
                 highlightthickness=0,show="*" if is_password else "")
    e.pack(fill="x",padx=6,pady=(2,8))
    return e

id_entry   = input_box(card, uid_label_var)
pass_entry = input_box(card, "PASSWORD", is_password=True)

# ── RESULT ───────────────────────────────────
result = tk.Label(card,text="",font=("Courier New",10,"bold"),fg=RED,bg=CARD_BG)
result.pack(pady=(0,4))
def show_signup():
    signup_win = tk.Toplevel(root)
    signup_win.title("Sign Up")
    signup_win.geometry("420x500")
    signup_win.configure(bg=BG)
    signup_win.resizable(False, False)

    # Card
    card2 = tk.Frame(signup_win, bg=CARD_BG, padx=36, pady=30,
                     highlightthickness=2, highlightbackground=CYAN)
    card2.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card2, text="◈  CREATE ACCOUNT",
             font=("Courier New",14,"bold"),
             fg=CYAN_GLOW, bg=CARD_BG).pack(pady=(0,4))
    tk.Frame(card2, bg=CYAN, height=1).pack(fill="x", pady=(0,16))

    # Input helper
    def field(label):
        tk.Label(card2, text=label, font=("Courier New",9,"bold"),
                 fg=TEXT_DIM if 'TEXT_DIM' in dir() else CYAN_DIM,
                 bg=CARD_BG, anchor="w").pack(fill="x")
        outer = tk.Frame(card2, bg=CYAN, padx=1, pady=1)
        outer.pack(fill="x", pady=(2,10))
        inner = tk.Frame(outer, bg="#020c1b")
        inner.pack(fill="both")
        e = tk.Entry(inner, font=("Courier New",10),
                     fg=CYAN_GLOW, bg="#020c1b",
                     insertbackground=CYAN,
                     relief="flat", bd=4,
                     show="*" if "PASSWORD" in label else "")
        e.pack(fill="x", padx=4, pady=4)
        return e

    e_name  = field("FULL NAME")
    e_email = field("EMAIL")
    e_phone = field("PHONE NUMBER")
    e_pass  = field("PASSWORD")

    msg_lbl = tk.Label(card2, text="", font=("Courier New",10,"bold"),
                       fg=RED, bg=CARD_BG)
    msg_lbl.pack(pady=(0,8))

    def do_signup():
        name  = e_name.get().strip()
        email = e_email.get().strip()
        phone = e_phone.get().strip()
        pwd   = e_pass.get().strip()

        if not all([name, email, phone, pwd]):
            msg_lbl.config(text="⚠  Fill all fields.", fg=RED); return
        if len(phone) != 10 or not phone.isdigit():
            msg_lbl.config(text="⚠  Phone must be 10 digits.", fg=RED); return

        if not DB_OK:
            msg_lbl.config(text="⚠  No DB connection.", fg=RED); return

        try:
            cursor = get_cursor()
            # Check if email already exists
            cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
            if cursor.fetchone():
                msg_lbl.config(text="✗  Email already registered.", fg=RED); return

            cursor.execute(
                "INSERT INTO users(name, email, phone, password) VALUES(%s,%s,%s,%s)",
                (name, email, phone, pwd))
            get_db().commit()

            # Get new user_id
            cursor.execute("SELECT LAST_INSERT_ID()")
            new_id = cursor.fetchone()[0]

            msg_lbl.config(
                text=f"✔  Account created! Your User ID: {new_id}",
                fg="#4ade80")

            # Auto close after 2 seconds
            signup_win.after(2500, signup_win.destroy)

        except Exception as ex:
            msg_lbl.config(text=f"✗  {ex}", fg=RED)

    # Signup button
    sb = tk.Button(card2, text="⊕  CREATE ACCOUNT",
                   font=("Courier New",11,"bold"),
                   fg=BTN_FG, bg=BTN_BG,
                   relief="flat", bd=0,
                   cursor="hand2", padx=20, pady=8,
                   command=do_signup)
    sb.pack(fill="x", pady=(0,4))
    sb.bind("<Enter>", lambda e: sb.config(bg=CYAN_GLOW))
    sb.bind("<Leave>", lambda e: sb.config(bg=BTN_BG))

    signup_win.bind("<Return>", lambda e: do_signup())
# ── LOGIN LOGIC ──────────────────────────────
def do_login():
    uid  = id_entry.get().strip()
    pwd  = pass_entry.get().strip()
    mode = login_type.get()
    if not uid or not pwd:
        result.config(text="⚠  Fill in both fields.", fg=RED); return

    if not DB_OK:
        if mode=="user"  and uid=="1"     and pwd=="demo":  launch("user",uid)
        elif mode=="admin" and uid=="admin" and pwd=="admin123": launch("admin",uid)
        else: result.config(text="✗  Invalid credentials.", fg=RED)
        return

    cursor = get_cursor()
    if mode=="user":
        cursor.execute(
            "SELECT user_id, name FROM users WHERE user_id=%s AND password=%s",(uid,pwd))
        row = cursor.fetchone()
        if row:
            result.config(text=f"✔  Welcome, {row[1]}!", fg=GREEN)
            root.after(800, lambda: launch("user", row[0]))
        else:
            result.config(text="✗  Invalid User ID or Password.", fg=RED)
    else:
        cursor.execute(
            "SELECT admin_id, name FROM admins WHERE username=%s AND password=%s",(uid,pwd))
        row = cursor.fetchone()
        if row:
            result.config(text=f"✔  Welcome, Admin {row[1]}!", fg=GREEN)
            root.after(800, lambda: launch("admin", row[0]))
        else:
            result.config(text="✗  Invalid Username or Password.", fg=RED)

def launch(role, uid):
    root.destroy()
    base = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(base,"user","user_dashboard.py") if role=="user" \
             else os.path.join(base,"admin","admin_dashboard.py")
    subprocess.Popen([sys.executable, target, str(uid)])

root.bind("<Return>", lambda e: do_login())

# ── BUTTONS ──────────────────────────────────
def make_btn(parent, text, cmd, primary=True):
    bg  = BTN_BG    if primary else BTN_EXIT
    fg  = BTN_FG    if primary else CYAN_GLOW
    hbg = CYAN_GLOW if primary else "#2a2a3e"
    b = tk.Button(parent,text=text,font=FN,fg=fg,bg=bg,
                  activebackground=hbg,activeforeground=BTN_FG,
                  relief="flat",bd=0,cursor="hand2",
                  padx=20,pady=8,width=24,command=cmd)
    b.pack(pady=4)
    b.bind("<Enter>",lambda e:b.config(bg=hbg))
    b.bind("<Leave>",lambda e:b.config(bg=bg))

btn_row = tk.Frame(card, bg=CARD_BG)
btn_row.pack(fill="x", pady=(2,0))
make_btn(btn_row,"⊕  LOGIN",   do_login,     primary=True)
make_btn(btn_row,"✎  SIGN UP", show_signup,  primary=False)
make_btn(btn_row,"✕  EXIT",    root.destroy, primary=False)

animate()
root.mainloop()
