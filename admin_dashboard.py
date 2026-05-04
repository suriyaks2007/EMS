# admin/admin_dashboard.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tkinter as tk
from tkinter import ttk, messagebox

try:
    from db.connection import get_db
    db     = get_db()
    cursor = db.cursor(buffered=True)
    DB_OK  = True
except Exception as e:
    DB_OK  = False
    print(f"[Admin] DB Error: {e}")

def fresh_cursor():
    """Always returns a fresh buffered cursor."""
    return db.cursor(buffered=True) if DB_OK else None

ADMIN_ID = sys.argv[1] if len(sys.argv) > 1 else "1"

# ── PALETTE ──────────────────────────────────
BG        = "#000814"
CYAN      = "#00ffff"
CYAN_DIM  = "#004d4d"
CYAN_GLOW = "#00e5e5"
CARD_BG   = "#0a0f1e"
PANEL_BG  = "#020c1b"
BTN_BG    = "#06b6d4"
BTN_FG    = "#000814"
BTN_EXIT  = "#1e1e2e"
TEXT_MAIN = "#e0f7fa"
TEXT_DIM  = "#80deea"
RED       = "#f87171"
GREEN     = "#4ade80"
YELLOW    = "#fbbf24"
NAV_BG    = "#00080f"
NAV_SEL   = "#003344"

FT = ("Courier New",16,"bold")
FL = ("Courier New", 9,"bold")
FB = ("Courier New",10)
FN = ("Courier New",11,"bold")
FH = ("Courier New",13,"bold")
FS = ("Courier New", 9)

# ── WINDOW ───────────────────────────────────
root = tk.Tk()
root.title("Event Management System — Admin Dashboard")
root.geometry("1100x700")
root.resizable(False, False)
root.configure(bg=BG)

# ── TOP BAR ──────────────────────────────────
topbar = tk.Frame(root,bg=CARD_BG,height=52,
                  highlightthickness=1,highlightbackground=CYAN_DIM)
topbar.pack(fill="x",side="top")
topbar.pack_propagate(False)
tk.Label(topbar,text="◈  EVENT MANAGEMENT SYSTEM  —  ADMIN PANEL",
         font=FT,fg=CYAN_GLOW,bg=CARD_BG).pack(side="left",padx=20,pady=10)

def logout():
    root.destroy()
    import subprocess
    base = os.path.join(os.path.dirname(__file__),"..")
    subprocess.Popen([sys.executable,os.path.join(base,"main.py")])

tk.Button(topbar,text="⇦ LOGOUT",font=FL,fg=CYAN_GLOW,bg=BTN_EXIT,
          relief="flat",bd=0,padx=12,pady=6,cursor="hand2",
          command=logout).pack(side="right",padx=16,pady=10)

# ── BODY ─────────────────────────────────────
body = tk.Frame(root,bg=BG)
body.pack(fill="both",expand=True)

nav = tk.Frame(body,bg=NAV_BG,width=195,
               highlightthickness=1,highlightbackground=CYAN_DIM)
nav.pack(side="left",fill="y")
nav.pack_propagate(False)

content = tk.Frame(body,bg=BG)
content.pack(side="left",fill="both",expand=True)

# ── NAV ──────────────────────────────────────
NAV_ITEMS = [
    ("📊  DASHBOARD",    "dashboard"),
    ("🎪  EVENTS",       "events"),
    ("👥  REGISTRATIONS","registrations"),
    ("💳  PAYMENTS",     "payments"),
    ("⏳  WAITING LIST", "waiting"),
    ("🏢  ORGANIZERS",   "organizers"),
    ("👤  USERS",        "users"),
]
nav_buttons = {}

def show_panel(name):
    for n,b in nav_buttons.items():
        b.config(bg=NAV_SEL if n==name else NAV_BG,
                 fg=CYAN    if n==name else TEXT_DIM)
    for w in content.winfo_children(): w.destroy()
    panels[name]()

tk.Frame(nav,bg=CYAN_DIM,height=1).pack(fill="x",pady=(10,4))
tk.Label(nav,text="  NAVIGATION",font=FS,fg=CYAN_DIM,
         bg=NAV_BG,anchor="w").pack(fill="x",padx=10,pady=(0,6))

for label,name in NAV_ITEMS:
    b = tk.Button(nav,text=label,font=("Courier New",10,"bold"),
                  fg=TEXT_DIM,bg=NAV_BG,relief="flat",bd=0,
                  anchor="w",padx=14,pady=10,cursor="hand2",
                  command=lambda n=name:show_panel(n))
    b.pack(fill="x")
    nav_buttons[name] = b

tk.Frame(nav,bg=CYAN_DIM,height=1).pack(fill="x",pady=10)

# ── HELPERS ──────────────────────────────────
def make_table(parent, columns, height=16):
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Admin.Treeview",
        background=PANEL_BG,foreground=TEXT_MAIN,
        fieldbackground=PANEL_BG,rowheight=26,
        font=("Courier New",9))
    s.configure("Admin.Treeview.Heading",
        background=CARD_BG,foreground=CYAN_GLOW,
        font=("Courier New",9,"bold"),relief="flat")
    s.map("Admin.Treeview",
        background=[("selected","#003344")],
        foreground=[("selected",CYAN)])
    frame = tk.Frame(parent,bg=PANEL_BG,
                     highlightthickness=1,highlightbackground=CYAN_DIM)
    frame.pack(fill="both",expand=True,padx=18,pady=(0,14))
    vsb = ttk.Scrollbar(frame,orient="vertical")
    vsb.pack(side="right",fill="y")
    hsb = ttk.Scrollbar(frame,orient="horizontal")
    hsb.pack(side="bottom",fill="x")
    tree = ttk.Treeview(frame,columns=columns,show="headings",
                        style="Admin.Treeview",height=height,
                        yscrollcommand=vsb.set,xscrollcommand=hsb.set)
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    for col in columns:
        tree.heading(col,text=col.upper())
        tree.column(col,width=max(100,len(col)*12),anchor="w")
    tree.pack(fill="both",expand=True)
    return tree

def section_header(parent, title, subtitle=""):
    f = tk.Frame(parent,bg=BG)
    f.pack(fill="x",padx=18,pady=(16,10))
    tk.Label(f,text=title,font=FH,fg=CYAN_GLOW,bg=BG).pack(side="left")
    if subtitle:
        tk.Label(f,text=f"  {subtitle}",font=FS,fg=CYAN_DIM,bg=BG).pack(side="left",pady=2)
    tk.Frame(parent,bg=CYAN_DIM,height=1).pack(fill="x",padx=18,pady=(0,10))

def form_row(parent, label, row, col=0, width=22):
    tk.Label(parent,text=label,font=FL,fg=TEXT_DIM,bg=CARD_BG,anchor="w"
             ).grid(row=row,column=col*2,sticky="w",padx=(10,4),pady=5)
    e = tk.Entry(parent,font=FB,fg=CYAN_GLOW,bg=PANEL_BG,
                 insertbackground=CYAN,relief="flat",bd=4,
                 highlightthickness=1,highlightbackground=CYAN_DIM,width=width)
    e.grid(row=row,column=col*2+1,sticky="ew",padx=(0,14),pady=5)
    return e

def action_btn(parent, text, cmd, color=BTN_BG):
    fg  = BTN_FG if color==BTN_BG else TEXT_MAIN
    hbg = CYAN_GLOW if color==BTN_BG else "#3a3a4e"
    b = tk.Button(parent,text=text,font=("Courier New",10,"bold"),
                  fg=fg,bg=color,relief="flat",bd=0,
                  padx=14,pady=6,cursor="hand2",command=cmd)
    b.pack(side="left",padx=6)
    b.bind("<Enter>",lambda e:b.config(bg=hbg))
    b.bind("<Leave>",lambda e:b.config(bg=color))
    return b

def dropdown_row(parent, label, row, col, width=18):
    tk.Label(parent,text=label,font=FL,fg=TEXT_DIM,bg=CARD_BG,anchor="w"
             ).grid(row=row,column=col*2,sticky="w",padx=(10,4),pady=5)
    var = tk.StringVar()
    cb  = ttk.Combobox(parent,textvariable=var,width=width,state="readonly",font=FB)
    cb.grid(row=row,column=col*2+1,sticky="ew",padx=(0,14),pady=5)
    return var, cb

# ─────────────────────────────────────────────
#  PANEL 1 — DASHBOARD
# ─────────────────────────────────────────────
def panel_dashboard():
    section_header(content,"📊  DASHBOARD","live overview")
    cursor = fresh_cursor()
    sf = tk.Frame(content,bg=BG)
    sf.pack(fill="x",padx=18,pady=(0,16))

    def stat_card(label,value,col):
        f = tk.Frame(sf,bg=CARD_BG,width=158,height=90,
                     highlightthickness=1,highlightbackground=CYAN_DIM)
        f.grid(row=0,column=col,padx=6,pady=4)
        f.pack_propagate(False)
        tk.Label(f,text=value,font=("Courier New",22,"bold"),
                 fg=CYAN_GLOW,bg=CARD_BG).pack(pady=(10,2))
        tk.Label(f,text=label,font=FS,fg=TEXT_DIM,bg=CARD_BG).pack()

    if DB_OK:
        cursor.execute("SELECT COUNT(*) FROM events");               ev  = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registrations");        rg  = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users");                us  = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE payment_status='paid'")
        rev = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM waiting_list");         wl  = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM payments WHERE payment_status='pending'")
        pp  = cursor.fetchone()[0]
    else:
        ev,rg,us,rev,wl,pp = 5,24,8,12400,3,6

    stat_card("TOTAL EVENTS",    str(ev),  0)
    stat_card("REGISTRATIONS",   str(rg),  1)
    stat_card("USERS",           str(us),  2)
    stat_card("REVENUE (₹)",    f"₹{rev}", 3)
    stat_card("WAITING LIST",    str(wl),  4)
    stat_card("pending PAYMENTS",str(pp),  5)

    section_header(content,"🕐  RECENT REGISTRATIONS","last 10")
    tree = make_table(content,["reg_id","user","event","ticket","date"],height=10)
    if DB_OK:
        cursor.execute("""
            SELECT r.registration_id,u.name,e.event_name,r.ticket_code,r.registration_date
            FROM registrations r
            JOIN users  u ON r.user_id =u.user_id
            JOIN events e ON r.event_id=e.event_id
            ORDER BY r.registration_date DESC LIMIT 10
        """)
        for row in cursor.fetchall(): tree.insert("","end",values=row)

# ─────────────────────────────────────────────
#  PANEL 2 — EVENTS
# ─────────────────────────────────────────────
def panel_events():
    section_header(content,"🎪  EVENTS","add · edit · delete")
    cursor = fresh_cursor()

    form_card = tk.Frame(content,bg=CARD_BG,
                         highlightthickness=1,highlightbackground=CYAN_DIM)
    form_card.pack(fill="x",padx=18,pady=(0,12))
    tk.Label(form_card,text="  ADD / EDIT EVENT",font=FL,fg=CYAN_DIM,bg=CARD_BG
             ).grid(row=0,column=0,columnspan=6,sticky="w",padx=10,pady=(8,2))

    e_name  = form_row(form_card,"Event Name",        1,0)
    e_date  = form_row(form_card,"Date (YYYY-MM-DD)", 1,1)
    e_price = form_row(form_card,"Price (₹)",         1,2,width=12)
    e_cap   = form_row(form_card,"Capacity",          2,0,width=12)

    cat_var,cat_cb = dropdown_row(form_card,"Category",2,1)
    ven_var,ven_cb = dropdown_row(form_card,"Venue",   2,2)
    org_var,org_cb = dropdown_row(form_card,"Organizer",3,0,width=28)
    org_cb.grid(columnspan=2)   # span 2 columns for organizer

    cat_map,ven_map,org_map = {},{},{}
    if DB_OK:
        cursor.execute("SELECT category_id,category_name FROM categories")
        cat_map = {n:i for i,n in cursor.fetchall()}; cat_cb["values"]=list(cat_map)
        cursor.execute("SELECT venue_id,venue_name FROM venues")
        ven_map = {n:i for i,n in cursor.fetchall()}; ven_cb["values"]=list(ven_map)
        cursor.execute("SELECT organizer_id,name FROM organizers ORDER BY name")
        org_map = {n:i for i,n in cursor.fetchall()}; org_cb["values"]=list(org_map)

    selected_id = [None]
    st_lbl = tk.Label(form_card,text="",font=FL,fg=GREEN,bg=CARD_BG)
    st_lbl.grid(row=5,column=0,columnspan=6,sticky="w",padx=10,pady=(0,6))

    def clear_form():
        for e in [e_name,e_date,e_price,e_cap]: e.delete(0,"end")
        cat_var.set(""); ven_var.set(""); org_var.set("")
        selected_id[0]=None; st_lbl.config(text="")

    def save_event():
        if not DB_OK: st_lbl.config(text="⚠  No DB.",fg=RED); return
        n,d,p,c = (e_name.get().strip(),e_date.get().strip(),
                   e_price.get().strip(),e_cap.get().strip())
        cat,ven,org = cat_var.get(),ven_var.get(),org_var.get()
        if not all([n,d,p,c,cat,ven,org]):
            st_lbl.config(text="⚠  Fill all fields.",fg=RED); return
        try:
            cid,vid,oid = cat_map[cat],ven_map[ven],org_map[org]
            if selected_id[0]:
                cursor.execute("""UPDATE events SET event_name=%s,event_date=%s,
                    price=%s,capacity=%s,category_id=%s,venue_id=%s,organizer_id=%s
                    WHERE event_id=%s""",(n,d,p,c,cid,vid,oid,selected_id[0]))
                st_lbl.config(text="✔  Event updated.",fg=GREEN)
            else:
                cursor.execute("""INSERT INTO events
                    (event_name,event_date,price,capacity,category_id,venue_id,organizer_id)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)""",(n,d,p,c,cid,vid,oid))
                st_lbl.config(text="✔  Event added.",fg=GREEN)
            db.commit(); clear_form(); load_events()
        except Exception as ex: st_lbl.config(text=f"✗  {ex}",fg=RED)

    def delete_event():
        if not selected_id[0]:
            st_lbl.config(text="⚠  Select an event first.",fg=RED); return
        if messagebox.askyesno("Confirm","Delete this event?"):
            try:
                cursor.execute("DELETE FROM events WHERE event_id=%s",(selected_id[0],))
                db.commit(); st_lbl.config(text="✔  Deleted.",fg=GREEN)
                clear_form(); load_events()
            except Exception as ex: st_lbl.config(text=f"✗  {ex}",fg=RED)

    br = tk.Frame(form_card,bg=CARD_BG)
    br.grid(row=4,column=0,columnspan=6,sticky="w",padx=6,pady=6)
    action_btn(br,"💾  SAVE",   save_event)
    action_btn(br,"✕  CLEAR",  clear_form,   color="#1e1e2e")
    action_btn(br,"🗑  DELETE", delete_event, color="#7f1d1d")

    tree = make_table(content,
        ["id","event","category","venue","organizer","date","price","capacity","seats_left"],
        height=8)

    def on_select(e):
        sel = tree.selection()
        if not sel: return
        v = tree.item(sel[0])["values"]
        selected_id[0] = v[0]
        e_name.delete(0,"end");  e_name.insert(0,v[1])
        e_date.delete(0,"end");  e_date.insert(0,v[5])
        e_price.delete(0,"end"); e_price.insert(0,str(v[6]))
        e_cap.delete(0,"end");   e_cap.insert(0,v[7])
        if DB_OK:
            cursor.execute("""SELECT c.category_name,v.venue_name,o.name
                FROM events e
                JOIN categories c ON e.category_id =c.category_id
                JOIN venues     v ON e.venue_id    =v.venue_id
                JOIN organizers o ON e.organizer_id=o.organizer_id
                WHERE e.event_id=%s""",(v[0],))
            r = cursor.fetchone()
            if r: cat_var.set(r[0]); ven_var.set(r[1]); org_var.set(r[2])

    tree.bind("<<TreeviewSelect>>",on_select)

    def load_events():
        tree.delete(*tree.get_children())
        if not DB_OK: return
        cursor.execute("""
            SELECT e.event_id,e.event_name,c.category_name,v.venue_name,
                   o.name,e.event_date,e.price,e.capacity,
                   (e.capacity - COUNT(r.registration_id)) AS seats_left
            FROM events e
            JOIN categories c  ON e.category_id =c.category_id
            JOIN venues     v  ON e.venue_id    =v.venue_id
            JOIN organizers o  ON e.organizer_id=o.organizer_id
            LEFT JOIN registrations r ON e.event_id=r.event_id
            GROUP BY e.event_id ORDER BY e.event_date
        """)
        for row in cursor.fetchall(): tree.insert("","end",values=row)

    load_events()

# ─────────────────────────────────────────────
#  PANEL 3 — REGISTRATIONS
# ─────────────────────────────────────────────
def panel_registrations():
    section_header(content,"👥  REGISTRATIONS","all registrations")
    cursor = fresh_cursor()
    sf = tk.Frame(content,bg=BG)
    sf.pack(fill="x",padx=18,pady=(0,8))
    tk.Label(sf,text="Search:",font=FL,fg=TEXT_DIM,bg=BG).pack(side="left")
    sv = tk.StringVar()
    tk.Entry(sf,textvariable=sv,font=FB,fg=CYAN_GLOW,bg=PANEL_BG,
             insertbackground=CYAN,relief="flat",bd=4,width=30).pack(side="left",padx=8)

    tree = make_table(content,["reg_id","user_id","name","event","ticket","date"])

    def load(flt=""):
        tree.delete(*tree.get_children())
        if not DB_OK: return
        cursor.execute("""
            SELECT r.registration_id,r.user_id,u.name,
                   e.event_name,r.ticket_code,r.registration_date
            FROM registrations r
            JOIN users  u ON r.user_id =u.user_id
            JOIN events e ON r.event_id=e.event_id
            ORDER BY r.registration_date DESC
        """)
        for row in cursor.fetchall():
            if flt.lower() in str(row).lower(): tree.insert("","end",values=row)

    sv.trace_add("write",lambda *a:load(sv.get()))
    load()

# ─────────────────────────────────────────────
#  PANEL 4 — PAYMENTS
# ─────────────────────────────────────────────
def panel_payments():
    section_header(content,"💳  PAYMENTS","view & update payment status")
    cursor = fresh_cursor()
    ff = tk.Frame(content,bg=BG)
    ff.pack(fill="x",padx=18,pady=(0,8))
    tk.Label(ff,text="Filter:",font=FL,fg=TEXT_DIM,bg=BG).pack(side="left")
    flt_var = tk.StringVar(value="all")

    tree = make_table(content,["pay_id","reg_id","user","event","amount","method","status"])
    selected_pay = [None]

    def load_payments(flt="all"):
        tree.delete(*tree.get_children())
        if not DB_OK: return
        q = """SELECT p.payment_id,p.registration_id,u.name,e.event_name,
                      p.amount,p.payment_method,p.payment_status
               FROM payments p
               JOIN registrations r ON p.registration_id=r.registration_id
               JOIN users  u ON r.user_id =u.user_id
               JOIN events e ON r.event_id=e.event_id"""
        if flt!="all": q+=f" WHERE p.payment_status='{flt}'"
        q+=" ORDER BY p.payment_id DESC"
        cursor.execute(q)
        for row in cursor.fetchall():
            tag = "paid" if row[6]=="paid" else ("fail" if row[6]=="failed" else "pend")
            tree.insert("","end",values=row,tags=(tag,))
        tree.tag_configure("paid",foreground=GREEN)
        tree.tag_configure("fail",foreground=RED)
        tree.tag_configure("pend",foreground=YELLOW)

    for val,lbl in [("all","All"),("paid","paid"),("pending","pending"),("failed","failed")]:
        tk.Radiobutton(ff,text=lbl,variable=flt_var,value=val,
                       font=FB,fg=TEXT_DIM,bg=BG,selectcolor=PANEL_BG,
                       activebackground=BG,
                       command=lambda:load_payments(flt_var.get())
                       ).pack(side="left",padx=6)

    tree.bind("<<TreeviewSelect>>",
        lambda e: selected_pay.__setitem__(0,
            tree.item(tree.selection()[0])["values"][0] if tree.selection() else None))

    uf = tk.Frame(content,bg=BG)
    uf.pack(fill="x",padx=18,pady=(8,0))
    tk.Label(uf,text="Update selected to:",font=FL,fg=TEXT_DIM,bg=BG).pack(side="left")
    ns = tk.StringVar(value="paid")
    for val in ["paid","pending","failed"]:
        tk.Radiobutton(uf,text=val.capitalize(),variable=ns,value=val,
                       font=FB,fg=TEXT_DIM,bg=BG,selectcolor=PANEL_BG,
                       activebackground=BG).pack(side="left",padx=6)

    msg = tk.Label(uf,text="",font=FL,fg=GREEN,bg=BG)
    msg.pack(side="left",padx=10)

    def update_status():
        if not selected_pay[0]: msg.config(text="⚠  Select a row first.",fg=RED); return
        try:
            cursor.execute("UPDATE payments SET payment_status=%s WHERE payment_id=%s",
                           (ns.get(),selected_pay[0]))
            db.commit(); msg.config(text="✔  Status updated.",fg=GREEN)
            load_payments(flt_var.get())
        except Exception as ex: msg.config(text=f"✗  {ex}",fg=RED)

    action_btn(uf,"✔  UPDATE STATUS",update_status)
    load_payments()

# ─────────────────────────────────────────────
#  PANEL 5 — WAITING LIST
# ─────────────────────────────────────────────
def panel_waiting():
    section_header(content,"⏳  WAITING LIST","promote or remove entries")
    cursor = fresh_cursor()
    tree = make_table(content,["user_id","name","event","email","phone"])
    sel_row = [None]
    tree.bind("<<TreeviewSelect>>",
        lambda e: sel_row.__setitem__(0,
            tree.item(tree.selection()[0])["values"] if tree.selection() else None))

    bf = tk.Frame(content,bg=BG)
    bf.pack(fill="x",padx=18,pady=(8,0))
    msg = tk.Label(bf,text="",font=FL,fg=GREEN,bg=BG)

    def load_waiting():
        tree.delete(*tree.get_children())
        if not DB_OK: return
        cursor.execute("""
            SELECT w.user_id,u.name,e.event_name,u.email,u.phone
            FROM waiting_list w
            JOIN users  u ON w.user_id =u.user_id
            JOIN events e ON w.event_id=e.event_id
            ORDER BY w.user_id
        """)
        for row in cursor.fetchall(): tree.insert("","end",values=row)

    def promote():
        if not sel_row[0]: msg.config(text="⚠  Select a row first.",fg=RED); return
        uid,event_name = sel_row[0][0],sel_row[0][2]
        try:
            cursor.execute("SELECT event_id FROM events WHERE event_name=%s",(event_name,))
            eid=cursor.fetchone()[0]; ticket=f"TICK{uid}{eid}P"
            cursor.execute(
                "INSERT INTO registrations(user_id,event_id,ticket_code) VALUES(%s,%s,%s)",
                (uid,eid,ticket))
            cursor.execute(
                "DELETE FROM waiting_list WHERE user_id=%s AND event_id=%s",(uid,eid))
            db.commit(); msg.config(text=f"✔  Promoted! Ticket: {ticket}",fg=GREEN)
            load_waiting()
        except Exception as ex: msg.config(text=f"✗  {ex}",fg=RED)

    def remove():
        if not sel_row[0]: msg.config(text="⚠  Select a row first.",fg=RED); return
        uid,event_name = sel_row[0][0],sel_row[0][2]
        if messagebox.askyesno("Confirm","Remove from waiting list?"):
            try:
                cursor.execute("SELECT event_id FROM events WHERE event_name=%s",(event_name,))
                eid=cursor.fetchone()[0]
                cursor.execute(
                    "DELETE FROM waiting_list WHERE user_id=%s AND event_id=%s",(uid,eid))
                db.commit(); msg.config(text="✔  Removed.",fg=GREEN)
                load_waiting()
            except Exception as ex: msg.config(text=f"✗  {ex}",fg=RED)

    action_btn(bf,"⬆  PROMOTE TO REGISTERED",promote)
    action_btn(bf,"✕  REMOVE",               remove,color="#7f1d1d")
    msg.pack(side="left",padx=10)
    load_waiting()

# ─────────────────────────────────────────────
#  PANEL 6 — ORGANIZERS
# ─────────────────────────────────────────────
def panel_organizers():
    section_header(content,"🏢  ORGANIZERS","add · edit · delete")
    cursor = fresh_cursor()

    form_card = tk.Frame(content,bg=CARD_BG,
                         highlightthickness=1,highlightbackground=CYAN_DIM)
    form_card.pack(fill="x",padx=18,pady=(0,12))
    tk.Label(form_card,text="  ADD / EDIT ORGANIZER",font=FL,fg=CYAN_DIM,bg=CARD_BG
             ).grid(row=0,column=0,columnspan=6,sticky="w",padx=10,pady=(8,2))

    e_name  = form_row(form_card,"Name",  1,0)
    e_email = form_row(form_card,"Email", 1,1)
    e_phone = form_row(form_card,"Phone", 1,2)

    sel_id = [None]
    st_lbl = tk.Label(form_card,text="",font=FL,fg=GREEN,bg=CARD_BG)
    st_lbl.grid(row=4,column=0,columnspan=6,sticky="w",padx=10,pady=(0,6))

    def clear_form():
        for e in [e_name,e_email,e_phone]: e.delete(0,"end")
        sel_id[0]=None; st_lbl.config(text="")

    def save_org():
        if not DB_OK: st_lbl.config(text="⚠  No DB.",fg=RED); return
        n,em,ph = e_name.get().strip(),e_email.get().strip(),e_phone.get().strip()
        if not all([n,em,ph]):
            st_lbl.config(text="⚠  Fill all fields.",fg=RED); return
        try:
            if sel_id[0]:
                cursor.execute(
                    "UPDATE organizers SET name=%s,email=%s,phone=%s WHERE organizer_id=%s",
                    (n,em,ph,sel_id[0]))
                st_lbl.config(text="✔  Updated.",fg=GREEN)
            else:
                cursor.execute(
                    "INSERT INTO organizers(name,email,phone) VALUES(%s,%s,%s)",(n,em,ph))
                st_lbl.config(text="✔  Organizer added.",fg=GREEN)
            db.commit(); clear_form(); load_orgs()
        except Exception as ex: st_lbl.config(text=f"✗  {ex}",fg=RED)

    def delete_org():
        if not sel_id[0]: st_lbl.config(text="⚠  Select first.",fg=RED); return
        if messagebox.askyesno("Confirm","Delete this organizer?"):
            try:
                cursor.execute("DELETE FROM organizers WHERE organizer_id=%s",(sel_id[0],))
                db.commit(); st_lbl.config(text="✔  Deleted.",fg=GREEN)
                clear_form(); load_orgs()
            except Exception as ex: st_lbl.config(text=f"✗  {ex}",fg=RED)

    br = tk.Frame(form_card,bg=CARD_BG)
    br.grid(row=3,column=0,columnspan=6,sticky="w",padx=6,pady=6)
    action_btn(br,"💾  SAVE",   save_org)
    action_btn(br,"✕  CLEAR",  clear_form,  color="#1e1e2e")
    action_btn(br,"🗑  DELETE", delete_org, color="#7f1d1d")

    tree = make_table(content,["org_id","name","email","phone"],height=10)

    def on_select(e):
        sel = tree.selection()
        if not sel: return
        v = tree.item(sel[0])["values"]
        sel_id[0]=v[0]
        for entry,val in zip([e_name,e_email,e_phone],v[1:]):
            entry.delete(0,"end"); entry.insert(0,val)

    tree.bind("<<TreeviewSelect>>",on_select)

    def load_orgs():
        tree.delete(*tree.get_children())
        if not DB_OK: return
        cursor.execute(
            "SELECT organizer_id,name,email,phone FROM organizers ORDER BY name")
        for row in cursor.fetchall(): tree.insert("","end",values=row)

    load_orgs()

# ─────────────────────────────────────────────
#  PANEL 7 — USERS
# ─────────────────────────────────────────────
def panel_users():
    section_header(content,"👤  USERS","all registered users")
    cursor = fresh_cursor()
    tree = make_table(content,["user_id","name","email","phone","registered_on"])
    if DB_OK:
        cursor.execute(
            "SELECT user_id,name,email,phone,created_at FROM users ORDER BY user_id")
        for row in cursor.fetchall(): tree.insert("","end",values=row)

# ── PANEL REGISTRY + START ───────────────────
panels = {
    "dashboard":     panel_dashboard,
    "events":        panel_events,
    "registrations": panel_registrations,
    "payments":      panel_payments,
    "waiting":       panel_waiting,
    "organizers":    panel_organizers,
    "users":         panel_users,
}

show_panel("dashboard")
root.mainloop()
