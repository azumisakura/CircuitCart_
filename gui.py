# gui.py
import os
import sys
import random
import re
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFont, Image

def is_valid_cvsu_email(email: str) -> bool:
    """
    Accepts only official CvSU email addresses.
    Example: username@cvsu.edu.ph
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@cvsu\.edu\.ph$"
    return re.match(pattern, email) is not None


FONT_NAME = "Poppins"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT_FILE = os.path.join(ASSETS_DIR, "Poppins.ttf")


def register_font_from_file(ttf_path):
    if not os.path.isfile(ttf_path): return False
    try:
        if sys.platform.startswith("win"):
            import ctypes
            FR_PRIVATE = 0x10
            pathbuf = os.path.abspath(ttf_path)
            ctypes.windll.gdi32.AddFontResourceExW(pathbuf, FR_PRIVATE, 0)
            root = tk.Tk(); root.withdraw()
            families = set(tkfont.families(root)); root.destroy()
            return FONT_NAME in families
        else:
            root = tk.Tk(); root.withdraw()
            families = set(tkfont.families(root)); root.destroy()
            return FONT_NAME in families
    except Exception:
        return False


register_font_from_file(FONT_FILE)


def _rounded_rect(canvas, x1, y1, x2, y2, r=15, **kwargs):
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class CircuitLendGUI:
    def __init__(self, controller):
        self.c = controller
        self.root = tk.Tk()
        self.root.title("CircuitLend")
        self.root.geometry("360x780")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffffff")
        self._configure_styles()

        self._icons = {}
        self._ensure_icons()

        self.content_frame = tk.Frame(self.root, bg="#ffffff")
        self.content_frame.pack(fill="both", expand=True)

        self.nav_frame = None

        self._demo_items = [
            {"id": "Breadboard", "title": "Breadboard", "image": "breadboard.png", "desc": "Standard solderless breadboard.", "category": "Equipment"},
            {"id": "DC Power Supply", "title": "DC Power Supply", "image": "dc power supply.png", "desc": "Bench DC/AC power supply.", "category": "Equipment"},
            {"id": "AC Power Supply", "title": "AC Power Supply", "image": "AC_DC power supply.png", "desc": "AC power source.", "category": "Equipment"},
            {"id": "Digital Multimeter", "title": "Digital Multimeter", "image": "digital multimeter.png", "desc": "Digital multimeter.", "category": "Equipment"},
            {"id": "AC Ammeter", "title": "AC Ammeter", "image": "ac ammeter.png", "desc": "AC ammeter.", "category": "Equipment"},
            {"id": "AC Voltmeter", "title": "AC Voltmeter", "image": "ac voltmeter.png", "desc": "AC voltmeter.", "category": "Equipment"},
            {"id": "Analog Multimeter", "title": "Analog Multimeter", "image": "analog multimeter.png", "desc": "Analog multimeter.", "category": "Equipment"},
            {"id": "Resistors (10 Ω – 1 kΩ)", "title": "Resistors (10 Ω – 1 kΩ)", "image": "resistors.png", "desc": "Assorted resistors.", "category": "Components"},
            {"id": "Potentiometer", "title": "Potentiometer", "image": "potentiometer.png", "desc": "Adjustable potentiometer.", "category": "Components"},
            {"id": "Capacitors (0.1 µF – 100 µF)", "title": "Capacitors (0.1 µF – 100 µF)", "image": "capacitor.png", "desc": "Assorted capacitors.", "category": "Components"},
            {"id": "Inductors (10 mH – 1.389 H)", "title": "Inductors (10 mH – 1.389 H)", "image": "inductors.png", "desc": "Inductor assortment.", "category": "Components"},
            {"id": "Connecting Wires", "title": "Connecting Wires", "image": "connecting wires.png", "desc": "Jumper wires.", "category": "Accessories"},
            {"id": "Alligator Clips", "title": "Alligator Clips", "image": "alligator clips.png", "desc": "Clip leads.", "category": "Accessories"},
            {"id": "Switches", "title": "Switches", "image": "switch toggle.png", "desc": "Toggle switches.", "category": "Accessories"},
        ]
        self._active_category = None

        self._build_login()

    def _configure_styles(self):
        style = ttk.Style()
        style.configure("TButton", font=(FONT_NAME, 12))
        style.configure("TLabel", font=(FONT_NAME, 12))
        style.configure("TEntry", font=(FONT_NAME, 12))
        self.title_font = (FONT_NAME, 12)
        self.subtitle_font = (FONT_NAME, 12)
        self.normal_font = (FONT_NAME, 12)

    def _icon_path(self, filename):
        return os.path.join(ASSETS_DIR, filename)

    def _load_icon(self, filename, size=(48, 48)):
        path = self._icon_path(filename)
        try:
            img = Image.open(path).convert("RGBA")
            img = ImageOps.contain(img, size)
            photo = ImageTk.PhotoImage(img)
            self._icons[(filename, size)] = photo
            return photo
        except Exception:
            blank = Image.new("RGBA", size, (255, 255, 255, 0))
            photo = ImageTk.PhotoImage(blank)
            self._icons[(filename, size)] = photo
            return photo

    def _ensure_icons(self):
        self.home_icon = self._load_icon("home.png", size=(34, 34))
        self.borrowed_icon = self._load_icon("borrowed.png", size=(34, 34))
        self.cart_icon = self._load_icon("cart.png", size=(34, 34))
        self.reminders_icon = self._load_icon("reminders.png", size=(34, 34))
        self.messages_icon = self._load_icon("messages.png", size=(34, 34))
        self.settings_icon = self._load_icon("settings.png", size=(34, 34))

    def _create_bottom_nav(self):
        self.nav_frame = tk.Frame(self.root, bg="#ffffff")
        self.nav_frame.pack(side="bottom", fill="x")
        self.btn_home = tk.Button(self.nav_frame, image=self.home_icon, text="Home", compound="top",
                                  font=(FONT_NAME, 11, "bold"), bd=0, bg="#ffffff", activebackground="#ffffff",
                                  command=self._build_home)
        self.btn_borrowed = tk.Button(self.nav_frame, image=self.borrowed_icon, text="Borrowed", compound="top",
                                      font=(FONT_NAME, 11, "bold"), bd=0, bg="#ffffff", activebackground="#ffffff",
                                      command=self._build_borrowed)
        self.btn_reminders = tk.Button(self.nav_frame, image=self.reminders_icon, text="Reminders", compound="top",
                                       font=(FONT_NAME, 11, "bold"), bd=0, bg="#ffffff", activebackground="#ffffff",
                                       command=self._build_reminders)
        self.btn_settings = tk.Button(self.nav_frame, image=self.settings_icon, text="Settings", compound="top",
                                      font=(FONT_NAME, 11, "bold"), bd=0, bg="#ffffff", activebackground="#ffffff",
                                      command=self._build_settings)
        for b in (self.btn_home, self.btn_borrowed, self.btn_reminders, self.btn_settings):
            b.pack(side="left", expand=True, fill="both", padx=2, pady=4)

    def _clear(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def _short_title(self, title, max_chars=20):
        if len(title) <= max_chars:
            return title
        parts, out = title.split(), ""
        for p in parts:
            if len(out) + len(p) + (1 if out else 0) > max_chars - 3:
                break
            out = (out + " " + p).strip()
        if not out:
            out = title[:max_chars - 3]
        return out + "..."

    def _image_for_id(self, item_id, size=(40, 40)):
        for it in self._demo_items:
            if it["id"] == item_id:
                return self._load_icon(it.get("image"), size=size)
        # fallback guess based on first word
        guess = f"{item_id.lower().split()[0]}.png"
        return self._load_icon(guess, size=size)

    def _build_login(self):
        self._clear()
        active_tab = tk.StringVar(value="login")

        # --- Logo on top ---
        logo_img = self._load_icon("circuitcart_logo.png", size=(240, 100))
        tk.Label(self.content_frame, image=logo_img, bg="#ffffff").pack(pady=(100, 80))

        # --- Tab bar ---
        tab_bar = tk.Frame(self.content_frame, bg="#ffffff")
        tab_bar.pack(pady=(0, 10))
        tab_login = tk.Button(tab_bar, text="LOG IN", width=12, height=2,
                            font=(FONT_NAME, 12, "bold"),
                            command=lambda: switch_tab("login"))
        tab_signup = tk.Button(tab_bar, text="SIGN UP", width=12, height=2,
                            font=(FONT_NAME, 12, "bold"),
                            command=lambda: switch_tab("signup"))
        tab_login.pack(side="left", padx=4)
        tab_signup.pack(side="left", padx=4)

        def pink_entry(parent, textvar, show=None):
            e = tk.Entry(parent, textvariable=textvar, show=show,
                        font=(FONT_NAME, 12), bg="#ffffff", fg="#000000",
                        relief="flat", bd=0,
                        highlightthickness=2,
                        highlightbackground="#ff9898", highlightcolor="#ff9898")
            e.pack(fill="x", padx=20, pady=2, ipady=8, ipadx=10)
            return e

        # Login form
        login_frame = tk.Frame(self.content_frame, bg="#ffffff")
        tk.Label(login_frame, text="Student No.", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12)
        login_id = tk.StringVar(); pink_entry(login_frame, login_id)
        tk.Label(login_frame, text="Password", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12)
        login_pwd = tk.StringVar(); pink_entry(login_frame, login_pwd, show="*")

        def do_login():
            ok, msg = self.c.login(login_id.get(), login_pwd.get())
            (messagebox.showinfo if ok else messagebox.showerror)("Login", msg)
            if ok:
                if not self.nav_frame:
                    self._create_bottom_nav()
                self._build_home()

        tk.Button(login_frame, text="LOG IN", font=(FONT_NAME, 12, "bold"),
                bg="#ff9898", fg="#ffffff", bd=0,
                width=20, height=2, command=do_login).pack(pady=12)

        #Sign up form
        signup_frame = tk.Frame(self.content_frame, bg="#ffffff")
        tk.Label(signup_frame, text="Username", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12)
        namev = tk.StringVar(); pink_entry(signup_frame, namev)
        tk.Label(signup_frame, text="Student No.", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12)
        idv = tk.StringVar(); pink_entry(signup_frame, idv)
        tk.Label(signup_frame, text="CVSU Email", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12)
        emailv = tk.StringVar(); pink_entry(signup_frame, emailv)
        tk.Label(signup_frame, text="Password", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=12)
        pwdv = tk.StringVar(); pink_entry(signup_frame, pwdv, show="*")

        def do_signup():
            email = emailv.get().strip()

            if not is_valid_cvsu_email(email):
                messagebox.showerror(
                    "Invalid Email",
                    "Please use your official CvSU email (example@cvsu.edu.ph)"
                )
                return

            ok, msg = self.c.register(
                namev.get(),
                email=email,
                student_id=idv.get(),
                password=pwdv.get()
            )
            (messagebox.showinfo if ok else messagebox.showerror)("Sign up", msg)
            if ok:
                messagebox.showinfo("Sign up", "Account created successfully! Please log in.")
                self._build_login()  # balik sa login screen

        tk.Button(signup_frame, text="SIGN UP", font=(FONT_NAME, 12, "bold"),
                bg="#ff9898", fg="#ffffff", bd=0,
                width=20, height=2, command=do_signup).pack(pady=12)

        def switch_tab(tab):
            login_frame.pack_forget()
            signup_frame.pack_forget()
            if tab == "login":
                login_frame.pack(pady=10)
                tab_login.config(bg="#ffcccc")
                tab_signup.config(bg="#ffffff")
            else:
                signup_frame.pack(pady=10)
                tab_signup.config(bg="#ffcccc")
                tab_login.config(bg="#ffffff")

        switch_tab(active_tab.get())

    # Home
    def _build_home(self):
        self._build_item_grid(self._demo_items)

    def _build_item_grid(self, items=None, cols=2, thumb_size=(140, 90)):
        if items is None: items = self._demo_items
        self._clear()
        header = tk.Frame(self.content_frame, bg="#ffffff"); header.pack(fill="x", pady=6, padx=6)
        
        logo_img = self._load_icon("circuitcart_logo.png", size=(120, 40))
        tk.Label(header, image=logo_img, bg="#ffffff").pack(side="left", padx=10)

        right = tk.Frame(header, bg="#ffffff"); right.pack(side="right")
        tk.Button(right, image=self.cart_icon, bd=0, bg="#ffffff", activebackground="#ffffff", command=self._build_cart).pack(side="right", padx=(6, 0))
        tk.Button(right, image=self.messages_icon, bd=0, bg="#ffffff", activebackground="#ffffff", command=self._build_messages).pack(side="right", padx=(6, 0))

        cat_frame = tk.Frame(self.content_frame, bg="#ffffff"); cat_frame.pack(fill="x", padx=8, pady=(6, 4))
        tk.Label(cat_frame, text="Filter:", font=self.normal_font, bg="#ffffff").pack(side="left", padx=(0, 6))
        for cat in ["Equipment", "Components", "Accessories"]:
            ttk.Button(cat_frame, text=cat, command=lambda c=cat: self._set_category(c)).pack(side="left", padx=4)

        canvas = tk.Canvas(self.content_frame, highlightthickness=0, bg="#ffffff", width=340)
        frame = tk.Frame(canvas, bg="#ffffff")
        vsb = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        r = c = 0; card_w = 150; card_h = 200; padx = 6; pady = 6
        for it in items:
            card_container = tk.Frame(frame, width=card_w, height=card_h, bg="#ffffff")
            card_container.grid_propagate(False)
            card_container.grid(row=r, column=c, padx=padx, pady=pady, sticky="nsew")

            canv = tk.Canvas(card_container, width=card_w, height=card_h, highlightthickness=0, bg="#ffffff")
            canv.pack(fill="both", expand=True)
            _rounded_rect(canv, 2, 2, card_w - 2, card_h - 2, r=12, fill="#fd4d4e", outline="#fd4d4e")
            _rounded_rect(canv, 6, 6, card_w - 6, card_h - 6, r=10, fill="#ffffff", outline="#ffffff")

            inner = tk.Frame(card_container, bg="#ffffff"); inner.place(x=8, y=8, width=card_w - 16, height=card_h - 16)
            thumb = self._load_icon(it.get("image"), size=(int(card_w - 40), 70))
            tk.Button(inner, image=thumb, bd=0, bg="#ffffff", activebackground="#ffffff",
                      command=lambda item=it: self._show_item_detail(item)).pack(pady=(4, 2))
            short = self._short_title(it["title"], max_chars=18)
            title_lbl = tk.Label(inner, text=short, font=(FONT_NAME, 12, "bold"), bg="#ffffff", wraplength=card_w - 30, justify="center")
            title_lbl.pack(pady=(4, 0)); title_lbl.bind("<Button-1>", lambda e, item=it: self._show_item_detail(item))
            tk.Label(inner, text=f"Stock: {self.c.availability_of(it['id'])}", font=(FONT_NAME, 12), bg="#ffffff").pack(side="left", anchor="s", pady=(0, 4))

            c += 1
            if c >= cols:
                c = 0; r += 1

    def _set_category(self, cat):
        self._active_category = cat if self._active_category != cat else None
        if self._active_category:
            filtered = [it for it in self._demo_items if it["category"] == self._active_category]
        else:
            filtered = self._demo_items
        self._build_item_grid(filtered)

    # Detail
    def _show_item_detail(self, item):
        self._clear()

        top = tk.Frame(self.content_frame, bg="#ffffff")
        top.pack(fill="x", pady=6, padx=6)
        tk.Button(top, text="← Back", bg="#ffffff", activebackground="#ffffff", bd=0,
                  command=lambda: self._build_item_grid(self._demo_items)).pack(side="left")

        detail = tk.Frame(self.content_frame, bg="#ffffff")
        detail.pack(fill="both", expand=True, padx=8, pady=6)

        img_frame = tk.Frame(detail, bg="#ffffff")
        img_frame.pack(fill="x", pady=(4, 6))
        large = self._load_icon(item.get("image"), size=(300, 180))
        tk.Label(img_frame, image=large, bg="#ffffff").pack(anchor="center")

        tk.Label(detail, text=item["title"], font=(FONT_NAME, 12, "bold"), bg="#ffffff",
                 wraplength=320, justify="left").pack(anchor="w", pady=(2, 4))
        tk.Label(detail, text=item.get("desc", ""), font=(FONT_NAME, 12), bg="#ffffff",
                 wraplength=320, justify="left").pack(anchor="w", pady=(0, 6))
        tk.Label(detail, text=f"Stock: {self.c.availability_of(item['id'])}", font=(FONT_NAME, 12), bg="#ffffff").pack(anchor="w")
        tk.Label(detail, text="Condition: Good", font=(FONT_NAME, 12), bg="#ffffff").pack(anchor="w", pady=(0, 4))

        action_row = tk.Frame(detail, bg="#ffffff")
        action_row.pack(fill="x", pady=(8, 6))
        tk.Button(action_row, image=self.cart_icon, text="  Add to cart", compound="left",
                  font=(FONT_NAME, 12), bd=0, bg="#ffffff", activebackground="#ffffff",
                  command=lambda: self._add_from_detail(item)).pack(side="left", padx=(0, 6))

        def show_overlay():
            # Floating overlay 
            overlay_canvas = tk.Canvas(detail, width=300, height=200, bg="#ffffff", highlightthickness=0)
            overlay_canvas.place(relx=0.5, rely=0.5, anchor="center")
            _rounded_rect(overlay_canvas, 5, 5, 295, 195, r=15, fill="#ffffff", outline="#fd4d4e", width=2)

            overlay = tk.Frame(detail, bg="#ffffff")
            overlay.place(relx=0.5, rely=0.5, anchor="center", width=290, height=190)

            tk.Label(overlay, text="Borrow date (YYYY-MM-DD)", font=self.normal_font, bg="#ffffff").pack(padx=10, pady=(10, 2))
            borrow_var = tk.StringVar()
            ttk.Entry(overlay, textvariable=borrow_var).pack(padx=10, pady=(0, 8))

            tk.Label(overlay, text="Return date (YYYY-MM-DD)", font=self.normal_font, bg="#ffffff").pack(padx=10, pady=(6, 2))
            return_var = tk.StringVar()
            ttk.Entry(overlay, textvariable=return_var).pack(padx=10, pady=(0, 8))

            # Priority dropdown (normal / thesis / official_lab)
            priority_var = tk.StringVar(value="normal")
            tk.Label(overlay, text="Request type", font=self.normal_font, bg="#ffffff").pack(padx=10, pady=(6, 2))
            ttk.Combobox(overlay, textvariable=priority_var, values=["normal", "thesis", "official_lab"]).pack(padx=10, pady=(0, 8))

            def confirm_borrow():
                bdate = borrow_var.get().strip()
                rdate = return_var.get().strip()
                reason = priority_var.get()
                prioritize = reason in ["thesis", "official_lab"]
                if not bdate or not rdate:
                    messagebox.showwarning("Borrow", "Please enter both dates.")
                    return
                ok, msg = self.c.add_to_cart(item["id"])
                if not ok:
                    messagebox.showerror("Borrow", msg); return
                ok2, msg2 = self.c.submit_borrow(reason=reason, prioritize=prioritize, borrow_date=bdate, return_date=rdate)
                if ok2:
                    receipt = self.c.generate_receipt([item["id"]], bdate, rdate)
                    # Close overlay; show receipt overlay that stays until saved
                    overlay_canvas.destroy()
                    overlay.destroy()
                    self._show_inline_receipt(detail, receipt)
                else:
                    messagebox.showerror("Borrow", msg2)

            ttk.Button(overlay, text="Confirm Borrow", command=confirm_borrow).pack(pady=10)
            ttk.Button(overlay, text="Cancel", command=lambda: (overlay_canvas.destroy(), overlay.destroy())).pack(pady=(0, 10))

        tk.Button(action_row, image=self.borrowed_icon, text="  Borrow Now", compound="left",
                  font=(FONT_NAME, 12, "bold"), bd=0, bg="#ffffff", activebackground="#ffffff",
                  command=show_overlay).pack(side="right")

        #You might also like
        related_frame = tk.Frame(detail, bg="#ffffff")
        related_frame.pack(fill="x", pady=(10, 0))
        tk.Label(related_frame, text="You might also like", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", pady=(0, 6))

        rel_canvas = tk.Canvas(related_frame, height=92, highlightthickness=0, bg="#ffffff")
        rel_canvas.pack(side="left", fill="x", expand=True)
        rel_inner = tk.Frame(rel_canvas, bg="#ffffff")
        rel_canvas.create_window((0, 0), window=rel_inner, anchor="nw")
        rel_inner.bind("<Configure>", lambda e: rel_canvas.configure(scrollregion=rel_canvas.bbox("all")))

        pool = [it for it in self._demo_items if it["id"] != item["id"]]
        sample = random.sample(pool, min(4, len(pool)))
        small_w = 92; small_h = 80
        for i, it in enumerate(sample):
            rc = tk.Frame(rel_inner, width=small_w, height=small_h, bg="#ffffff")
            rc.grid_propagate(False); rc.grid(row=0, column=i, padx=6)
            canv = tk.Canvas(rc, width=small_w, height=small_h, highlightthickness=0, bg="#ffffff")
            canv.pack(fill="both", expand=True)
            _rounded_rect(canv, 2, 2, small_w - 2, small_h - 2, r=10, fill="#fd4d4e", outline="#fd4d4e")
            _rounded_rect(canv, 6, 6, small_w - 6, small_h - 6, r=8, fill="#ffffff", outline="#ffffff")
            inner = tk.Frame(rc, bg="#ffffff"); inner.place(x=6, y=6, width=small_w - 12, height=small_h - 12)
            thumb = self._load_icon(it.get("image"), size=(small_w - 28, 40))
            tk.Button(inner, image=thumb, bd=0, bg="#ffffff", activebackground="#ffffff",
                      command=lambda item=it: self._show_item_detail(item)).pack()
            tk.Label(inner, text=self._short_title(it["title"], max_chars=14), font=(FONT_NAME, 12), bg="#ffffff",
                     wraplength=small_w - 10, justify="center").pack()

    def _show_inline_receipt(self, parent, receipt):
        if not receipt:
            return
        canvas = tk.Canvas(parent, width=320, height=240, bg="#ffffff", highlightthickness=0)
        canvas.place(relx=0.5, rely=0.5, anchor="center")
        _rounded_rect(canvas, 5, 5, 315, 235, r=15, fill="#ffffff", outline="#fd4d4e", width=2)

        receipt_frame = tk.Frame(parent, bg="#ffffff")
        receipt_frame.place(relx=0.5, rely=0.5, anchor="center", width=310, height=230)

        lines = [
            f"Borrower: {receipt['borrower_name']} (ID: {receipt.get('student_id','')})",
            f"Email: {receipt.get('email','')}",
            "Items borrowed:",
        ] + receipt.get('items', []) + [
            f"Borrow date: {receipt['borrow_date']}",
            f"Return deadline: {receipt['return_date']}",
            f"Issued on: {receipt['issued_at']}",
            "",
            "Note: Present this receipt upon return."
        ]

        for line in lines:
            tk.Label(receipt_frame, text=line, font=(FONT_NAME, 12), bg="#ffffff",
                    anchor="w", justify="left", wraplength=300).pack(anchor="w")


    # Cart / Borrow 
    def _add_from_detail(self, item):
        ok, msg = self.c.add_to_cart(item["id"])
        (messagebox.showinfo if ok else messagebox.showerror)("Cart", msg)

    # Cart
    def _build_cart(self):
        self._clear()

        header = tk.Frame(self.content_frame, bg="#ffffff")
        header.pack(fill="x", pady=6, padx=8)
        tk.Label(header, text="Your cart", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(side="left")
        edit_mode = tk.BooleanVar(value=False)

        def toggle_edit():
            edit_mode.set(not edit_mode.get())
            redraw_items()

        tk.Button(header, text="Edit", font=(FONT_NAME, 12, "bold"), bg="#ffffff",
                  activebackground="#ffffff", bd=0, command=toggle_edit).pack(side="right")

        items = list(self.c.cart.items())
        selected = {it: tk.BooleanVar(value=False) for it in items}
        quantities = {it: tk.IntVar(value=1) for it in items}

        box = tk.Frame(self.content_frame, bg="#ffffff")
        box.pack(fill="both", expand=True, padx=8)

        def redraw_items():
            for widget in box.winfo_children():
                widget.destroy()
            for it in items:
                row = tk.Frame(box, bg="#ffffff")
                row.pack(fill="x", pady=4)

                # Checkbox
                tk.Checkbutton(row, variable=selected[it], bg="#ffffff").pack(side="left")

                thumb = self._image_for_id(it, size=(40, 40))
                # Keep a reference to avoid GC
                row.thumb = thumb
                tk.Label(row, image=thumb, bg="#ffffff").pack(side="left", padx=6)

                # Item name
                tk.Label(row, text=it, font=self.normal_font, bg="#ffffff").pack(side="left", padx=6)

                # Quantity selector
                qty_frame = tk.Frame(row, bg="#ffffff")
                qty_frame.pack(side="right", padx=6)

                def dec(item=it):
                    quantities[item].set(max(1, quantities[item].get() - 1))

                def inc(item=it):
                    quantities[item].set(quantities[item].get() + 1)

                tk.Button(qty_frame, text="−", width=2, bg="#eeeeee", command=dec).pack(side="left")
                tk.Label(qty_frame, textvariable=quantities[it], width=2, bg="#ffffff").pack(side="left")
                tk.Button(qty_frame, text="+", width=2, bg="#eeeeee", command=inc).pack(side="left")

                # Remove button (only in edit mode)
                if edit_mode.get():
                    def remove_item(id_to_remove=it):
                        ok, msg = self.c.remove_from_cart(id_to_remove)
                        if ok:
                            items.remove(id_to_remove)
                            selected.pop(id_to_remove, None)
                            quantities.pop(id_to_remove, None)
                            redraw_items()
                        messagebox.showinfo("Cart", msg)
                    tk.Button(row, text="Remove", bg="#ffdddd", command=remove_item).pack(side="right", padx=6)

        redraw_items()

        # Footer row
        footer = tk.Frame(self.content_frame, bg="#ffffff")
        footer.pack(fill="x", pady=10, padx=8)

        # Select all checkbox (left)
        def toggle_all():
            val = select_all_var.get()
            for v in selected.values():
                v.set(val)

        select_all_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            footer,
            text="Select all",
            variable=select_all_var,
            command=toggle_all,
            bg="#ffffff",
            font=(FONT_NAME, 12, "bold")
        ).pack(side="left")

        # Borrow selected 
        def borrow_selected():
            chosen_ids = [it for it in items if selected[it].get()]
            if not chosen_ids:
                messagebox.showwarning("Borrow", "No items selected.")
                return

            # Expand items by quantity
            expanded_items = []
            for it in chosen_ids:
                qty = max(1, quantities[it].get())
                expanded_items.extend([it] * qty)

            # Generate receipt directly
            receipt = self.c.generate_receipt(expanded_items, "2026-01-12", "2026-01-20")

            # Show receipt overlay
            self._show_inline_receipt(self.content_frame, receipt)

            # Send receipt to Messages tab
            if not hasattr(self.c, "messages"):
                self.c.messages = []
            self.c.messages.append(receipt)

            messagebox.showinfo("Borrow", "Borrow request submitted. Receipt sent to Messages.")

        tk.Button(footer, text="Borrow selected", font=(FONT_NAME, 12, "bold"),
                  bg="#ffffff", activebackground="#ffffff", bd=0,
                  command=borrow_selected).pack(side="right")

    # Borrowed (listed vertically)
    def _build_borrowed(self):
        self._clear()
        tk.Label(self.content_frame, text="Borrowed Items", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(pady=8)

        if not self.c.current_user:
            tk.Label(self.content_frame, text="Please log in.", font=(FONT_NAME, 12), bg="#ffffff").pack(pady=6)
            return

        frame = tk.Frame(self.content_frame, bg="#ffffff")
        frame.pack(fill="both", expand=True, padx=8, pady=6)

        for req in self.c.list_borrow_history():
            ts = req.get("timestamp", "")[:19]
            tk.Label(frame, text=f"{ts}", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w")
            for item in req.get("items", []):
                tk.Label(frame, text=f"   {item}", font=(FONT_NAME, 12), bg="#ffffff").pack(anchor="w")

    def _set_dates_for_last(self):
        if not self.c.current_user:
            messagebox.showwarning("Borrowed", "Please log in first."); return
        # Use floating overlay for dates (consistent UX)
        overlay_canvas = tk.Canvas(self.content_frame, width=300, height=180, bg="#ffffff", highlightthickness=0)
        overlay_canvas.place(relx=0.5, rely=0.5, anchor="center")
        _rounded_rect(overlay_canvas, 5, 5, 295, 175, r=15, fill="#ffffff", outline="#fd4d4e", width=2)
        overlay = tk.Frame(self.content_frame, bg="#ffffff")
        overlay.place(relx=0.5, rely=0.5, anchor="center", width=290, height=170)

        tk.Label(overlay, text="Borrow date (YYYY-MM-DD)", font=self.normal_font, bg="#ffffff").pack(padx=10, pady=(10, 2))
        bvar = tk.StringVar(); ttk.Entry(overlay, textvariable=bvar).pack(padx=10, pady=(0, 8))
        tk.Label(overlay, text="Return date (YYYY-MM-DD)", font=self.normal_font, bg="#ffffff").pack(padx=10, pady=(6, 2))
        rvar = tk.StringVar(); ttk.Entry(overlay, textvariable=rvar).pack(padx=10, pady=(0, 8))

        def save():
            borrow_date = bvar.get().strip()
            return_date = rvar.get().strip()
            if not (borrow_date and return_date):
                messagebox.showwarning("Borrowed", "Dates not set."); return
            history = self.c.list_borrow_history()
            if not history:
                messagebox.showwarning("Borrowed", "No borrow history found."); return
            last_items = history[-1].get("items", [])
            # Save reminder
            self.c.reminders.append({
                "user": self.c.current_user.name,
                "items": last_items,
                "borrow_date": borrow_date,
                "return_date": return_date
            })
            self.c._persist()
            # Show receipt overlay
            overlay_canvas.destroy(); overlay.destroy()
            r = self.c.generate_receipt(last_items, borrow_date, return_date)
            self._show_inline_receipt(self.content_frame, r)
            messagebox.showinfo("Borrowed", "Reminder saved. See Reminders tab.")

        ttk.Button(overlay, text="Save", command=save).pack(pady=10)
        ttk.Button(overlay, text="Cancel", command=lambda: (overlay_canvas.destroy(), overlay.destroy())).pack(pady=(0, 10))

    # Reminders
    def _build_reminders(self):
        self._clear()
        tk.Label(self.content_frame, text="Reminders", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(pady=8)

        canvas = tk.Canvas(self.content_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#ffffff")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for rem in self.c.list_reminders():
            borrow = rem.get("borrow_date", "")
            return_d = rem.get("return_date", "")
            row = tk.Frame(scroll_frame, bg="#ffffff")
            row.pack(fill="x", pady=(6,2))
            tk.Label(row, text=f"Borrow: {borrow}", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(side="left", padx=10)
            tk.Label(row, text=f"Return: {return_d}", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(side="left", padx=30)
            for item in rem.get("items", []):
                tk.Label(scroll_frame, text=f"   {item}", font=(FONT_NAME, 12), bg="#ffffff").pack(anchor="w")

        # Optional bottom button
        btn_frame = tk.Frame(self.content_frame, bg="#ffffff")
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Back", command=self._build_home).pack(side="right", padx=8)

    def _build_settings(self):
        self._clear()
        tk.Label(self.content_frame, text="Settings", font=(FONT_NAME, 14, "bold"), bg="#ffffff").pack(pady=10)

        #Account Info
        acct_frame = tk.Frame(self.content_frame, bg="#ffffff"); acct_frame.pack(fill="x", padx=12, pady=6)
        tk.Label(acct_frame, text="Account Settings", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", pady=(0, 6))

        if self.c.current_user:
            # Username row
            row1 = tk.Frame(acct_frame, bg="#ffffff"); row1.pack(fill="x", pady=4)
            tk.Label(row1, text="Username:", font=(FONT_NAME, 11), bg="#ffffff").pack(side="left")
            tk.Label(row1, text=self.c.current_user.name, font=(FONT_NAME, 11, "bold"), bg="#ffffff").pack(side="left", padx=6)
            tk.Button(row1, text="Edit", font=(FONT_NAME, 11, "bold"), bd=0,
                    bg="#ffffff", activebackground="#ffffff",
                    command=lambda: self._edit_username(self.content_frame)).pack(side="right")

            # Email row
            row2 = tk.Frame(acct_frame, bg="#ffffff"); row2.pack(fill="x", pady=4)
            tk.Label(row2, text="Email:", font=(FONT_NAME, 11), bg="#ffffff").pack(side="left")
            tk.Label(row2, text=self.c.current_user.email, font=(FONT_NAME, 11), bg="#ffffff").pack(side="left", padx=6)

            # Password row
            row3 = tk.Frame(acct_frame, bg="#ffffff"); row3.pack(fill="x", pady=4)
            tk.Label(row3, text="Password:", font=(FONT_NAME, 11), bg="#ffffff").pack(side="left")
            tk.Label(row3, text="********************", font=(FONT_NAME, 11), bg="#ffffff").pack(side="left", padx=6)
            tk.Button(row3, text="Edit", font=(FONT_NAME, 11, "bold"), bd=0,
                    bg="#ffffff", activebackground="#ffffff",
                    command=lambda: self._edit_password(self.content_frame)).pack(side="right")

        #Notification Settings
        notif_frame = tk.Frame(self.content_frame, bg="#ffffff"); notif_frame.pack(fill="x", padx=12, pady=6)
        tk.Label(notif_frame, text="Notification Settings", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", pady=(0,6))
        self.notif_var = tk.BooleanVar(value=True)
        tk.Checkbutton(notif_frame, text="Due date reminders", variable=self.notif_var,
                    font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w")

        tk.Label(notif_frame, text="Reminder time", font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w", pady=(6,2))
        self.reminder_time = tk.StringVar(value="1")
        tk.Radiobutton(notif_frame, text="1 day before", variable=self.reminder_time, value="1",
                    font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w")
        tk.Radiobutton(notif_frame, text="3 days before", variable=self.reminder_time, value="3",
                    font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w")

        #About Section
        about_frame = tk.Frame(self.content_frame, bg="#ffffff"); about_frame.pack(fill="x", padx=12, pady=10)
        tk.Label(about_frame, text="About", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", pady=(0,6))
        tk.Label(about_frame, text="Version: 1.0", font=(FONT_NAME, 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(about_frame, text="Developers:", font=(FONT_NAME, 11, "bold"), bg="#ffffff").pack(anchor="w")
        tk.Label(about_frame, text="  Dela Peña, Theresa Julliana B.", font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w")
        tk.Label(about_frame, text="  Ramboyong, Kirt Angelo D.", font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w")
        tk.Label(about_frame, text="  Lustico, Leivinze", font=(FONT_NAME, 11), bg="#ffffff").pack(anchor="w")
        tk.Label(about_frame, text="About App:", font=(FONT_NAME, 11, "bold"), bg="#ffffff").pack(anchor="w", pady=(6,2))
        tk.Label(about_frame, text="CircuitCart: Development and Optimization of a Smart Borrowing System for Electrical Laboratory Equipment Using Data Structures and Algorithmic Techniques",
                font=(FONT_NAME, 11), bg="#ffffff", wraplength=320, justify="left").pack(anchor="w")

        # Bottom Buttons
        btn_frame = tk.Frame(self.content_frame, bg="#ffffff"); btn_frame.pack(fill="x", padx=12, pady=12)
        tk.Button(btn_frame, text="Log out", font=(FONT_NAME, 12, "bold"), bd=0,
                bg="#ffffff", activebackground="#ffffff",
                command=self._logout).pack(fill="x", pady=4)
        tk.Button(btn_frame, text="Close", font=(FONT_NAME, 12, "bold"), bd=0,
                bg="#ffffff", activebackground="#ffffff",
                command=self._build_home).pack(fill="x", pady=4)

    def _edit_username(self, parent):
        newv = tk.StringVar()
        self._show_overlay(
            parent,
            "Change Username",
            [("New username", newv, None)],
            lambda vals: self.c.change_username(vals["New username"].strip())
        )

    def _edit_password(self, parent):
        oldv = tk.StringVar()
        newv = tk.StringVar()
        self._show_overlay(
            parent,
            "Change Password",
            [("Old password", oldv, "*"), ("New password", newv, "*")],
            lambda vals: self.c.change_password(vals["Old password"], vals["New password"])
        )

    def _logout(self):
        self.c.logout()
        messagebox.showinfo("Logout", "You have been logged out.")
        self._build_login()

    def _show_overlay(self, parent, title, fields, on_submit):
        # Floating overlay 
        overlay_canvas = tk.Canvas(parent, width=300, height=200, bg="#ffffff", highlightthickness=0)
        overlay_canvas.place(relx=0.5, rely=0.5, anchor="center")
        _rounded_rect(overlay_canvas, 5, 5, 295, 195, r=15, fill="#ffffff", outline="#fd4d4e", width=2)

        overlay = tk.Frame(parent, bg="#ffffff")
        overlay.place(relx=0.5, rely=0.5, anchor="center", width=290, height=190)

        tk.Label(overlay, text=title, font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(pady=(10, 6))

        entries = {}
        for label, var, show in fields:
            tk.Label(overlay, text=label, font=(FONT_NAME, 12), bg="#ffffff").pack(anchor="w", padx=10)
            e = ttk.Entry(overlay, textvariable=var, show=show)
            e.pack(fill="x", padx=10, pady=(0, 6))
            entries[label] = e

        def submit():
            ok, msg = on_submit({lbl: v.get() for lbl, v in [(l, var) for l, var, _ in fields]})
            (messagebox.showinfo if ok else messagebox.showerror)(title, msg)
            if ok:
                overlay_canvas.destroy()
                overlay.destroy()
                self._build_settings()

        ttk.Button(overlay, text="Save", command=submit).pack(pady=6)
        ttk.Button(overlay, text="Cancel", command=lambda: (overlay_canvas.destroy(), overlay.destroy())).pack()

    def _build_messages(self):
        self._clear()
        tk.Label(self.content_frame, text="Messages", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(pady=8)

        for msg in self.c.messages:
            tk.Label(self.content_frame, text="Receipt", font=(FONT_NAME, 12, "bold"), bg="#ffffff").pack(anchor="w", padx=8)
            for line in [
                f"Borrower: {msg['borrower_name']} (ID: {msg.get('student_id','')})",
                f"Email: {msg.get('email','')}",
                "Items borrowed:"
            ] + msg.get("items", []) + [
                f"Borrow date: {msg['borrow_date']}",
                f"Return deadline: {msg['return_date']}",
                f"Issued on: {msg['issued_at']}",
                "Note: Present this receipt upon return."
            ]:
                tk.Label(self.content_frame, text=line, font=(FONT_NAME, 12), bg="#ffffff").pack(anchor="w", padx=20)

    def run(self):
        self.root.mainloop()
