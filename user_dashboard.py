# user/user_dashboard.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tkinter as tk
from tkinter import ttk
import math, random

LOGGED_IN_USER = sys.argv[1] if len(sys.argv) > 1 else None

try:
    from db.connection import get_cursor, get_db
    cursor      = get_cursor()
    db          = get_db()
    cursor.execute("SELECT event_id, event_name FROM events")
    rows        = cursor.fetchall()
    event_dict  = {name: eid for eid, name in rows}
    event_names = list(event_dict.keys())
    DB_CONNECTED = True
except Exception:
    DB_CONNECTED = False
    event_dict  = {"Tech Summit 2025":1,"Music Fest":2,"Art Expo":3}
    event_names = list(event_dict.keys())

# ── PALETTE ──────────────────────────────────
BG         = "#000814"
CYAN       = "#00ffff"
CYAN_DIM   = "#004d4d"
CYAN_GLOW  = "#00e5e5"
CARD_BG    = "#0a0f1e"
CARD_BORDER= "#00ffff"
TEXT_MAIN  = "#e0f7fa"
BTN_BG     = "#06b6d4"
BTN_FG     = "#000814"
BTN_EXIT   = "#1e1e2e"
GREEN      = "#4ade80"
YELLOW     = "#fbbf24"
RED        = "#f87171"

# ── WINDOW ───────────────────────────────────
root = tk.Tk()
root.title("Event Management System — User Dashboard")
root.geometry("900x700")
root.resizable(False, False)
root.configure(bg=BG)

canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
canvas.place(x=0, y=0, relwidth=1, relheight=1)

# ── NETWORK ──────────────────────────────────
W, H = 900, 700
NODE_COUNT, CONNECT_DIST, MAX_NODES = 70, 200, 110

class Node:
    def __init__(self, x=None, y=None, fast=False):
        self.x   = x if x is not None else random.uniform(0, W)
        self.y   = y if y is not None else random.uniform(0, H)
        speed    = random.uniform(0.5,1.0) if fast else random.uniform(0.12,0.30)
        angle    = random.uniform(0, math.tau)
        self.vx  = math.cos(angle)*speed
        self.vy  = math.sin(angle)*speed
        self.r   = random.uniform(1.5, 2.8)
        self.ttl = random.randint(320,520) if fast else None
    def move(self):
        self.x+=self.vx; self.y+=self.vy
        if self.x<0 or self.x>W: self.vx*=-1
        if self.y<0 or self.y>H: self.vy*=-1
        if self.ttl is not None: self.ttl-=1
    @property
    def alive(self): return self.ttl is None or self.ttl>0

nodes = [Node() for _ in range(NODE_COUNT)]
_lids, _nids = [], []

def hex_alpha(base, a):
    r0,g0,b0=int(BG[1:3],16),int(BG[3:5],16),int(BG[5:7],16)
    r1,g1,b1=int(base[1:3],16),int(base[3:5],16),int(base[5:7],16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r0+(r1-r0)*a), int(g0+(g1-g0)*a), int(b0+(b1-b0)*a))

def on_canvas_click(e):
    if len(nodes)<MAX_NODES:
        for _ in range(4): nodes.append(Node(x=e.x,y=e.y,fast=True))

def animate_network():
    for i in _lids+_nids: canvas.delete(i)
    _lids.clear(); _nids.clear()
    for nd in nodes[:]:
        nd.move()
        if not nd.alive: nodes.remove(nd)
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            d=math.hypot(a.x-b.x,a.y-b.y)
            if d<CONNECT_DIST:
                t=d/CONNECT_DIST
                al=(1+math.cos(math.pi*t))/2*0.6
                _lids.append(canvas.create_line(a.x,a.y,b.x,b.y,
                    fill=hex_alpha(CYAN,al*0.85),width=1))
    for nd in nodes:
        fade=(nd.ttl/520) if nd.ttl else 1.0
        sf=(1+math.cos(math.pi*(1-fade)))/2
        col=hex_alpha(CYAN_GLOW,max(0.15,sf*0.9))
        r=nd.r*sf if nd.ttl else nd.r
        _nids.append(canvas.create_oval(nd.x-r,nd.y-r,nd.x+r,nd.y+r,fill=col,outline=""))
    canvas.tag_raise("card_group")
    root.after(30, animate_network)

canvas.bind("<Button-1>", on_canvas_click)

# ── CARD ─────────────────────────────────────
shadow = tk.Frame(canvas, bg="#003333", width=478, height=550)
sw     = canvas.create_window(452,352,window=shadow)
card   = tk.Frame(canvas, bg=CARD_BG, padx=44, pady=28,
                  highlightthickness=2, highlightbackground=CARD_BORDER)
cw     = canvas.create_window(448,348,window=card)
canvas.addtag_withtag("card_group",sw)
canvas.addtag_withtag("card_group",cw)

# ── FONTS ────────────────────────────────────
FT = ("Courier New",19,"bold")
FL = ("Courier New", 9,"bold")
FB = ("Courier New",10)
FN = ("Courier New",11,"bold")

# ── TITLE ────────────────────────────────────
tf = tk.Frame(card, bg=CARD_BG)
tf.pack(fill="x", pady=(0,16))
tk.Label(tf,text="◈  EVENT MANAGEMENT SYSTEM  ◈",
         font=FT,fg=CYAN_GLOW,bg=CARD_BG).pack()
tk.Frame(tf,bg=CYAN,height=1,width=360).pack(pady=(6,0))

# ── INPUT BOX HELPER ─────────────────────────
def input_box(parent, label_text, widget_fn):
    outer = tk.Frame(parent, bg=CYAN, padx=1, pady=1)
    outer.pack(fill="x", pady=(0,12))
    inner = tk.Frame(outer, bg="#020c1b")
    inner.pack(fill="both")
    tk.Label(inner, text=f"  {label_text}", font=FL,
             fg=CYAN_DIM, bg="#020c1b", anchor="w").pack(fill="x",pady=(4,0))
    w = widget_fn(inner)
    w.pack(fill="x", padx=6, pady=(2,8))
    return outer, w

# ── USER ID BOX ──────────────────────────────
def make_entry(parent):
    return tk.Entry(parent, font=FB, fg=CYAN_GLOW, bg="#020c1b",
                    insertbackground=CYAN, relief="flat", bd=0, highlightthickness=0)

_, user_entry = input_box(card, "USER ID", make_entry)
if LOGGED_IN_USER:
    user_entry.insert(0, LOGGED_IN_USER)
    user_entry.config(state="disabled")

# ── EVENT SELECTOR BOX ───────────────────────
style = ttk.Style()
style.theme_use("clam")
style.configure("Cyber.TCombobox",
    fieldbackground="#020c1b", background="#020c1b",
    foreground=CYAN_GLOW, selectbackground="#020c1b",
    selectforeground=CYAN_GLOW, bordercolor="#020c1b",
    arrowcolor=CYAN, relief="flat", font=("Courier New",10))
style.map("Cyber.TCombobox",
    fieldbackground=[("readonly","#020c1b")],
    foreground=[("readonly",CYAN_GLOW)])

def make_combo(parent):
    return ttk.Combobox(parent, values=event_names,
        style="Cyber.TCombobox", state="readonly", font=("Courier New",10))

_, event_combo = input_box(card, "SELECT EVENT", make_combo)

# ── INFO PANEL ───────────────────────────────
info_frame = tk.Frame(card, bg="#020c1b",
    highlightthickness=1, highlightbackground=CYAN_DIM)
info_frame.pack(fill="x", pady=(0,10))
info_label = tk.Label(info_frame,
    text="  — select an event to view details —",
    font=FB, fg=CYAN_DIM, bg="#020c1b",
    justify="left", anchor="w", padx=10, pady=8)
info_label.pack(fill="x")

# ── BUTTON HELPER ────────────────────────────
def make_button(parent, text, command, primary=True):
    bg  = BTN_BG    if primary else BTN_EXIT
    fg  = BTN_FG    if primary else CYAN_GLOW
    hbg = CYAN_GLOW if primary else "#2a2a3e"
    b = tk.Button(parent, text=text, font=FN, fg=fg, bg=bg,
                  activebackground=hbg, activeforeground=BTN_FG,
                  relief="flat", bd=0, cursor="hand2",
                  padx=20, pady=7, width=24, command=command)
    b.pack(pady=3)
    b.bind("<Enter>", lambda e: b.config(bg=hbg))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

result_label = tk.Label(card, text="", font=FN, fg=CYAN, bg=CARD_BG)

# ── SHOW EVENT DETAILS ───────────────────────
def show_event_details():
    event_name = event_combo.get()
    if not event_name:
        result_label.config(text="⚠  Please select an event.", fg=RED)
        return

    if DB_CONNECTED:
        event_id = event_dict[event_name]
        cur = db.cursor(buffered=True)
        cur.execute("""
            SELECT e.event_name, c.category_name, v.venue_name,
                   e.event_date, e.price, e.capacity,
                   o.name, o.phone
            FROM events e
            JOIN categories c ON e.category_id  = c.category_id
            JOIN venues     v ON e.venue_id     = v.venue_id
            JOIN organizers o ON e.organizer_id = o.organizer_id
            WHERE e.event_id=%s
        """, (event_id,))
        d = cur.fetchone()
        cur.execute(
            "SELECT COUNT(*) FROM registrations WHERE event_id=%s", (event_id,))
        remaining = d[5] - cur.fetchone()[0]
        cur.close()
        details = (
            f"  ▸ Event      : {d[0]}\n"
            f"  ▸ Category   : {d[1]}\n"
            f"  ▸ Venue      : {d[2]}\n"
            f"  ▸ Date       : {d[3]}\n"
            f"  ▸ Fee        : ₹{d[4]}\n"
            f"  ▸ Seats Left : {remaining}\n"
            f"  ▸ Organizer  : {d[6]}\n"
            f"  ▸ Contact    : {d[7]}"
        )
    else:
        details = (
            f"  ▸ Event      : {event_name}\n"
            f"  ▸ Category   : Demo\n"
            f"  ▸ Venue      : Coimbatore Hall\n"
            f"  ▸ Date       : 2025-12-01\n"
            f"  ▸ Fee        : ₹499\n"
            f"  ▸ Seats Left : 50\n"
            f"  ▸ Organizer  : Demo Org\n"
            f"  ▸ Contact    : 9000000000"
        )
    info_label.config(text=details, fg=TEXT_MAIN)
    result_label.config(text="")

# ── REGISTER ─────────────────────────────────
def register():
    user_id    = user_entry.get().strip()
    event_name = event_combo.get()
    if not event_name:
        result_label.config(text="⚠  Select an event first.", fg=RED); return
    if not user_id:
        result_label.config(text="⚠  Enter your User ID.", fg=RED); return

    if DB_CONNECTED:
        cur = db.cursor(buffered=True)
        event_id = event_dict[event_name]

        cur.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
        if cur.fetchone() is None:
            result_label.config(text="✗  Invalid User ID.", fg=RED)
            cur.close(); return

        cur.execute("SELECT capacity, price FROM events WHERE event_id=%s", (event_id,))
        ev_row   = cur.fetchone()
        capacity = ev_row[0]
        price    = ev_row[1]

        cur.execute("SELECT COUNT(*) FROM registrations WHERE event_id=%s", (event_id,))
        total = cur.fetchone()[0]

        if total < capacity:
            ticket = f"TICK{user_id}{event_id}"
            cur.execute(
                "INSERT INTO registrations(user_id,event_id,ticket_code) VALUES(%s,%s,%s)",
                (user_id, event_id, ticket))
            db.commit()

            # Get new registration_id and auto-create payment record
            cur.execute("SELECT LAST_INSERT_ID()")
            reg_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO payments(registration_id,amount,payment_method,payment_status) VALUES(%s,%s,%s,%s)",
                (reg_id, price, "pending", "pending"))
            db.commit()

            result_label.config(text=f"✔  Registered!  Ticket: {ticket}", fg=GREEN)
        else:
            cur.execute(
                "INSERT INTO waiting_list(user_id,event_id) VALUES(%s,%s)", (user_id,event_id))
            db.commit()
            result_label.config(text="⚡  Event Full → Added to Waiting List", fg=YELLOW)

        cur.close()
    else:
        ticket = f"TICK{user_id}{event_dict[event_name]}"
        result_label.config(text=f"✔  [Demo] Ticket: {ticket}", fg=GREEN)

# ── MY REGISTRATIONS ─────────────────────────
def my_registrations():
    user_id = user_entry.get().strip()
    if not user_id:
        result_label.config(text="⚠  No User ID found.", fg=RED); return

    win = tk.Toplevel(root)
    win.title("My Registrations")
    win.geometry("780x420")
    win.configure(bg=BG)
    win.resizable(False, False)

    # Header
    hf = tk.Frame(win, bg=CARD_BG, height=48,
                  highlightthickness=1, highlightbackground=CYAN_DIM)
    hf.pack(fill="x")
    hf.pack_propagate(False)
    tk.Label(hf, text=f"📋  MY REGISTRATIONS  —  User {user_id}",
             font=("Courier New",12,"bold"),
             fg=CYAN_GLOW, bg=CARD_BG).pack(side="left", padx=16, pady=10)
    tk.Button(hf, text="✕  CLOSE",
              font=("Courier New",9,"bold"),
              fg=CYAN_GLOW, bg=BTN_EXIT,
              relief="flat", bd=0, padx=10, pady=4,
              cursor="hand2", command=win.destroy
              ).pack(side="right", padx=12, pady=10)

    # Table style
    s = ttk.Style()
    s.configure("My.Treeview",
        background="#020c1b", foreground=TEXT_MAIN,
        fieldbackground="#020c1b", rowheight=26,
        font=("Courier New",9))
    s.configure("My.Treeview.Heading",
        background=CARD_BG, foreground=CYAN_GLOW,
        font=("Courier New",9,"bold"), relief="flat")
    s.map("My.Treeview",
        background=[("selected","#003344")],
        foreground=[("selected",CYAN)])

    frame = tk.Frame(win, bg="#020c1b",
                     highlightthickness=1, highlightbackground=CYAN_DIM)
    frame.pack(fill="both", expand=True, padx=16, pady=12)

    vsb = ttk.Scrollbar(frame, orient="vertical")
    vsb.pack(side="right", fill="y")

    cols = ["ticket","event","date","venue","fee","payment_status"]
    tree = ttk.Treeview(frame, columns=cols, show="headings",
                        style="My.Treeview", height=12,
                        yscrollcommand=vsb.set)
    vsb.config(command=tree.yview)

    widths = [120, 180, 110, 150, 70, 110]
    for col, w in zip(cols, widths):
        tree.heading(col, text=col.upper().replace("_"," "))
        tree.column(col, width=w, anchor="w")
    tree.pack(fill="both", expand=True)

    tree.tag_configure("paid",    foreground=GREEN)
    tree.tag_configure("pending", foreground=YELLOW)
    tree.tag_configure("failed",  foreground=RED)

    if DB_CONNECTED:
        try:
            cur = db.cursor(buffered=True)
            cur.execute("""
                SELECT r.ticket_code, e.event_name, e.event_date,
                       v.venue_name, e.price,
                       COALESCE(p.payment_status, 'no payment')
                FROM registrations r
                JOIN events  e ON r.event_id = e.event_id
                JOIN venues  v ON e.venue_id  = v.venue_id
                LEFT JOIN payments p ON p.registration_id = r.registration_id
                WHERE r.user_id = %s
                ORDER BY r.registration_date DESC
            """, (user_id,))
            rows = cur.fetchall()
            cur.close()
            if rows:
                for row in rows:
                    tag = row[5] if row[5] in ["paid","pending","failed"] else ""
                    tree.insert("", "end", values=row, tags=(tag,))
            else:
                tree.insert("", "end",
                    values=("—","No registrations found","—","—","—","—"))
        except Exception as ex:
            tree.insert("", "end", values=(f"Error: {ex}","","","","",""))
    else:
        tree.insert("", "end",
            values=("TICK101","Tech Summit","2025-12-01","Demo Hall","499","paid"))

# ── BUTTONS ──────────────────────────────────
btn_row = tk.Frame(card, bg=CARD_BG)
btn_row.pack(fill="x", pady=(6,0))
make_button(btn_row, "⌕  EVENT DETAILS",    show_event_details, primary=True)
make_button(btn_row, "⊕  REGISTER",         register,           primary=True)
make_button(btn_row, "📋  MY REGISTRATIONS", my_registrations,   primary=True)
make_button(btn_row, "✕  EXIT",             root.destroy,        primary=False)
result_label.pack(pady=(6,0))

# ── CORNER BRACKETS ──────────────────────────
L = 30
for cx,cy,dx,dy in [(0,0,1,1),(900,0,-1,1),(0,700,1,-1),(900,700,-1,-1)]:
    canvas.create_line(cx,cy,cx+dx*L,cy,fill=CYAN,width=2)
    canvas.create_line(cx,cy,cx,cy+dy*L,fill=CYAN,width=2)
status = "● CONNECTED" if DB_CONNECTED else "● DEMO MODE"
canvas.create_text(14,690,anchor="w",text=status,
    font=("Courier New",9),fill=GREEN if DB_CONNECTED else YELLOW)
canvas.create_text(886,690,anchor="e",text="EVENT MANAGEMENT SYSTEM  v2.0",
    font=("Courier New",9),fill=CYAN_DIM)

animate_network()
root.mainloop()
