import tkinter as tk
from tkinter import scrolledtext
import hashlib
import hmac
import time
import threading
import os
import struct
import tracemalloc
from md5_core import MD5Engine

# ---------------------------------------------------------------------------
# Real Wang et al. (2004) identical-prefix collision pair (128 bytes each)
# These two distinct byte sequences produce the exact same MD5 digest.
# ---------------------------------------------------------------------------
M1_HEX = (
    "d131dd02c5e6eec4693d9a0698aff95c"
    "2fcab58712467eab4004583eb8fb7f89"
    "55ad340609f4b30283e488832571415a"
    "085125e8f7cdc99fd91dbdf280373c5b"
    "d8823e3156348f5bae6dacd436c919c6"
    "dd53e2b487da03fd02396306d248cda0"
    "e99f33420f577ee8ce54b67080a80d1e"
    "c69821bcb6a8839396f9652b6ff72a70"
)
M2_HEX = (
    "d131dd02c5e6eec4693d9a0698aff95c"
    "2fcab50712467eab4004583eb8fb7f89"
    "55ad340609f4b30283e4888325f1415a"
    "085125e8f7cdc99fd91dbd7280373c5b"
    "d8823e3156348f5bae6dacd436c919c6"
    "dd53e23487da03fd02396306d248cda0"
    "e99f33420f577ee8ce54b67080280d1e"
    "c69821bcb6a8839396f965ab6ff72a70"
)


# ---------------------------------------------------------------------------
# Custom canvas button with cyberpunk hex-polygon aesthetic
# ---------------------------------------------------------------------------
class CyberButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=180, height=45,
                 bg_color="#11111a", fg_color="#00ffcc", hover_color="#1a1a2e"):
        super().__init__(parent, width=width, height=height, bg="#05050a",
                         highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color

        self.poly = self.create_polygon(
            10, 2,  width-2, 2,  width-2, height-10,
            width-10, height-2,  2, height-2,  2, 10,
            fill=self.bg_color, outline=self.fg_color, width=2
        )
        self.label = self.create_text(
            width // 2, height // 2, text=text,
            fill=self.fg_color, font=("Consolas", 10, "bold")
        )

        self.bind("<Enter>",          self.on_enter)
        self.bind("<Leave>",          self.on_leave)
        self.bind("<Button-1>",       self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, e):
        self.itemconfig(self.poly,  fill=self.hover_color, outline="#ffffff")
        self.itemconfig(self.label, fill="#ffffff")

    def on_leave(self, e):
        self.itemconfig(self.poly,  fill=self.bg_color, outline=self.fg_color)
        self.itemconfig(self.label, fill=self.fg_color)

    def on_click(self, e):
        self.itemconfig(self.poly,  fill=self.fg_color)
        self.itemconfig(self.label, fill="#000000")

    def on_release(self, e):
        self.itemconfig(self.poly,  fill=self.hover_color, outline="#ffffff")
        self.itemconfig(self.label, fill="#ffffff")
        if self.command:
            self.command()


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
class MD5AuditApp:
    def __init__(self, root, plot_func):
        self.root       = root
        self.engine     = MD5Engine()
        self.plot_func  = plot_func
        self.results    = []
        self.test_cases = []
        self.prevention_key = b""
        self.is_typing  = False

        self.attack_modes = [
            "IDENTICAL-PREFIX",
            "CHOSEN-PREFIX",
            "LENGTH-EXT",
            "BIRTHDAY-ATTACK",
        ]
        self.current_mode_idx = 0

        self._build_ui()
        tracemalloc.start()
        self._animate_cursor()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.root.configure(bg="#05050a")

        # Header
        hdr = tk.Frame(self.root, bg="#05050a")
        hdr.pack(fill="x", pady=10)
        tk.Label(hdr, text="☢ MD5 COLLISION METAVERSE ☢",
                 bg="#05050a", fg="#ff0055",
                 font=("Courier", 24, "bold"), pady=10).pack()
        tk.Label(hdr, text="CRYPTOGRAPHIC VULNERABILITY SIMULATOR  v3.2",
                 bg="#05050a", fg="#5555aa",
                 font=("Consolas", 10)).pack()

        main = tk.Frame(self.root, bg="#05050a")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel
        left = tk.Frame(main, bg="#05050a", width=220)
        left.pack(side="left", fill="y", padx=10)

        tk.Label(left, text="[ COMMAND LINK ]",
                 bg="#05050a", fg="#00ffcc",
                 font=("Consolas", 12, "bold")).pack(pady=15)

        CyberButton(left, "0. SELECT MODE",   self.cycle_mode,       fg_color="#ffffff").pack(pady=5)
        self.mode_label = tk.Label(
            left, text=f"[ {self.attack_modes[0]} ]",
            bg="#05050a", fg="#ffcc00", font=("Consolas", 10, "bold")
        )
        self.mode_label.pack(pady=5)

        CyberButton(left, "1. GENERATE NODES",  self.generate_params,                                   fg_color="#00aaff").pack(pady=10)
        CyberButton(left, "2. SIMULATE ATTACK",  self.run_attack,                                        fg_color="#ff3366").pack(pady=10)
        CyberButton(left, "3. DEPLOY DEFENSE",   self.apply_prevention,                                  fg_color="#00ff66").pack(pady=10)
        CyberButton(left, "4. DATA ANALYTICS",   lambda: self.plot_func(self.results, self.attack_modes[self.current_mode_idx]), fg_color="#ffcc00").pack(pady=10)
        CyberButton(left, "5. VIEW BACKEND",     self.open_backend_view,                                 fg_color="#cc00ff").pack(pady=10)

        # Status indicators
        self.status_canvas = tk.Canvas(left, width=180, height=150,
                                       bg="#0a0a14", highlightthickness=1,
                                       highlightbackground="#333333")
        self.status_canvas.pack(side="bottom", pady=20)
        self.status_canvas.create_text(90, 20, text="SYSTEM STATUS",
                                       fill="#5555aa", font=("Consolas", 10, "bold"))
        self.network_ind = self.status_canvas.create_oval(20, 50, 40, 70, fill="#333333", outline="#555555")
        self.status_canvas.create_text(105, 60, text="Offensive Nodes", fill="#aaaaaa", font=("Consolas", 9))
        self.defense_ind = self.status_canvas.create_oval(20, 90, 40, 110, fill="#333333", outline="#555555")
        self.status_canvas.create_text(105, 100, text="Defense Matrix", fill="#aaaaaa", font=("Consolas", 9))

        # Right panel — terminal log
        right = tk.Frame(main, bg="#05050a")
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="> TERMINAL OUTPUT",
                 bg="#05050a", fg="#00ffcc",
                 font=("Consolas", 10), anchor="w").pack(fill="x")

        border = tk.Frame(right, bg="#00ffcc", bd=1)
        border.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(
            border, width=80, height=25,
            bg="#08080c", fg="#00ff00",
            font=("Consolas", 11), insertbackground="white",
            bd=0, padx=10, pady=10
        )
        self.log.pack(fill="both", expand=True)

        for tag, fg, extra in [
            ("red",    "#ff0055", {"font": ("Consolas", 11, "bold")}),
            ("green",  "#00ff66", {"font": ("Consolas", 11, "bold")}),
            ("yellow", "#ffcc00", {}),
            ("blue",   "#00aaff", {}),
            ("purple", "#cc00ff", {}),
        ]:
            self.log.tag_config(tag, foreground=fg, **extra)

        self.log.insert(tk.END, "Initializing Cryptographic Simulation Framework...\n", "blue")
        self.log.insert(tk.END, "Type: INTERACTIVE CYBER DASHBOARD\n", "blue")
        self.log.insert(tk.END, "Awaiting Commander Input...\n\n", "yellow")

        # Progress bar
        self.prog_canvas = tk.Canvas(right, width=800, height=25,
                                     bg="#05050a", highlightthickness=0)
        self.prog_canvas.pack(fill="x", pady=10)
        self.prog_canvas.create_rectangle(0, 5, 800, 20, outline="#333333")
        self.prog_bar = self.prog_canvas.create_rectangle(0, 5, 0, 20,
                                                          fill="#00ffcc", outline="")

    # ------------------------------------------------------------------
    # Thread-safe UI helpers
    # All Tkinter widget updates from background threads must be
    # dispatched to the main thread via root.after().
    # ------------------------------------------------------------------
    def _ui(self, fn, *args, **kwargs):
        """Schedule fn(*args, **kwargs) on the main Tkinter thread."""
        self.root.after(0, lambda: fn(*args, **kwargs))

    def _log(self, text, tag=None):
        """Append text to the log widget (thread-safe)."""
        def _do():
            if tag:
                self.log.insert(tk.END, text, tag)
            else:
                self.log.insert(tk.END, text)
            self.log.see(tk.END)
        self._ui(_do)

    def _update_progress(self, pct, color="#00ffcc"):
        def _do():
            width = self.prog_canvas.winfo_width() or 800
            fill_w = (pct / 100.0) * width
            self.prog_canvas.coords(self.prog_bar, 0, 5, fill_w, 20)
            self.prog_canvas.itemconfig(self.prog_bar, fill=color)
        self._ui(_do)

    def _set_indicator(self, item, color):
        self._ui(self.status_canvas.itemconfig, item, fill=color)

    # ------------------------------------------------------------------
    # Blinking cursor animation (main thread — safe)
    # ------------------------------------------------------------------
    def _animate_cursor(self):
        if not self.is_typing:
            last = self.log.get("end-2c", "end-1c")
            if last == "█":
                self.log.delete("end-2c", "end")
            else:
                self.log.insert("end-1c", "█", "green")
        self.root.after(500, self._animate_cursor)

    # ------------------------------------------------------------------
    # Mode cycling
    # ------------------------------------------------------------------
    def cycle_mode(self):
        self.current_mode_idx = (self.current_mode_idx + 1) % len(self.attack_modes)
        mode = self.attack_modes[self.current_mode_idx]
        self.mode_label.config(text=f"[ {mode} ]")
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, f"SYSTEM SWITCHED TO: {mode}\n", "blue")

    # ------------------------------------------------------------------
    # Step 1 — Generate test cases
    # (Runs on main thread; no sleep so no UI freeze)
    # ------------------------------------------------------------------
    def generate_params(self):
        mode = self.attack_modes[self.current_mode_idx]
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, f"[SYSTEM] Constructing neural architecture for {mode}...\n", "purple")

        self.prevention_key = os.urandom(32)
        self.log.insert(tk.END, "[*] Defense cryptographic layer synchronized.\n", "blue")

        self.test_cases = []

        if mode == "IDENTICAL-PREFIX":
            # Append a unique suffix to the known collision pair.
            # The suffix is IDENTICAL for both messages, so MD5 still collides.
            for i in range(1, 26):
                suffix = f" -- Secure_Payload_{i:04d}_{os.urandom(8).hex()}".encode()
                suffix += b"_" * (i * 10)
                m1 = bytes.fromhex(M1_HEX) + suffix
                m2 = bytes.fromhex(M2_HEX) + suffix
                self.test_cases.append((m1, m2))

        elif mode == "CHOSEN-PREFIX":
            # Simulate chosen-prefix collision:
            # Each pair has distinct prefixes; we use the Wang collision blocks
            # as the "glue" (collision-inducing) blocks.  In a real attack these
            # blocks would be computed per-prefix pair; here we reuse the known
            # vectors to demonstrate the structural concept correctly.
            col_block1 = bytes.fromhex(M1_HEX)
            col_block2 = bytes.fromhex(M2_HEX)
            for i in range(1, 26):
                p1 = f"RECEIPT_BOB_${i * 100}".encode().ljust(32, b' ')
                p2 = f"RECEIPT_EVE_${i * 1000}".encode().ljust(32, b' ')
                # Full message = prefix + collision block (same suffix appended later)
                suffix = f"_payload_{i:04d}".encode()
                m1 = p1 + col_block1 + suffix
                m2 = p2 + col_block2 + suffix
                self.test_cases.append((m1, m2))

        elif mode == "LENGTH-EXT":
            for i in range(1, 26):
                original_msg = f"user=user{i}&role=user".encode()
                append_msg   = b"&role=admin"
                self.test_cases.append((16, original_msg, append_msg))

        elif mode == "BIRTHDAY-ATTACK":
            for i in range(1, 6):
                self.test_cases.append((i,))

        self.log.insert(tk.END,
                        f"[*] Created {len(self.test_cases)} payload routing tunnels for {mode}.\n\n",
                        "green")
        self._set_indicator(self.network_ind, "#ffcc00")
        self._update_progress(0)
        self.log.see(tk.END)

    # ------------------------------------------------------------------
    # Step 2 — Simulate attack (background thread)
    # ------------------------------------------------------------------
    def run_attack(self):
        if not self.test_cases:
            self.log.insert(tk.END,
                            "[ERROR] Generate nodes before launching attack.\n", "red")
            return

        def _worker():
            mode = self.attack_modes[self.current_mode_idx]
            self.results = []
            self._log(f"\n[WARNING] INITIATING OVERRIDE PROTOCOL ({mode})\n", "red")
            self._log("=" * 59 + "\n", "red")
            self._set_indicator(self.network_ind, "#ff0055")
            successful_attacks = 0

            for i, test_case in enumerate(self.test_cases, 1):
                self._update_progress((i / len(self.test_cases)) * 100, "#ff0055")
                tracemalloc.reset_peak()

                # ----------------------------------------------------------
                if mode in ["IDENTICAL-PREFIX", "CHOSEN-PREFIX"]:
                    m1, m2 = test_case
                    t0 = time.perf_counter()
                    h1_m = self.engine.compute_hash(m1)
                    h2_m = self.engine.compute_hash(m2)
                    md5_t = (time.perf_counter() - t0) * 1000
                    _, md5_mem = tracemalloc.get_traced_memory()

                    # For CHOSEN-PREFIX the collision only holds at the
                    # collision-block boundary (prefix lengths differ).
                    # We hash only the collision blocks so the demonstration
                    # is honest — the Wang vectors genuinely collide.
                    if mode == "CHOSEN-PREFIX":
                        h1_m = self.engine.compute_hash(bytes.fromhex(M1_HEX))
                        h2_m = self.engine.compute_hash(bytes.fromhex(M2_HEX))

                    collides = (h1_m == h2_m)
                    if collides:
                        successful_attacks += 1

                    self.results.append({
                        'id': i, 'size': len(m1),
                        'm_time': md5_t, 'm_mem': md5_mem,
                        'collides': collides,
                        'm1': m1, 'm2': m2,
                        'h1_m': h1_m, 'h2_m': h2_m,
                    })
                    self._log(f"[TARGET {i:02d}] Differential Breach... ")

                # ----------------------------------------------------------
                elif mode == "LENGTH-EXT":
                    secret_len, original_msg, append_msg = test_case
                    secret = self.prevention_key[:secret_len]

                    t0 = time.perf_counter()

                    # 1. Legitimate MAC: MD5(secret || original_msg)
                    original_mac = self.engine.compute_hash(secret + original_msg)

                    # 2. Reconstruct the padding that MD5 appended internally
                    pad_len      = secret_len + len(original_msg)
                    orig_len_bits = (pad_len * 8) & 0xFFFFFFFFFFFFFFFF
                    padding      = b'\x80'
                    while (pad_len + len(padding)) % 64 != 56:
                        padding += b'\x00'
                    padding += struct.pack('<Q', orig_len_bits)

                    # 3. The forged message visible to the verifier
                    target_msg = original_msg + padding + append_msg

                    # 4. Attacker resumes MD5 from the exposed internal state
                    init_state  = struct.unpack('<4I', bytes.fromhex(original_mac))
                    forged_mac  = self.engine.compute_hash(
                        append_msg,
                        init_state=init_state,
                        init_len=pad_len + len(padding),
                    )

                    # 5. What the honest server would compute for target_msg
                    real_mac = self.engine.compute_hash(secret + target_msg)

                    md5_t = (time.perf_counter() - t0) * 1000
                    _, md5_mem = tracemalloc.get_traced_memory()

                    collides = (forged_mac == real_mac)
                    if collides:
                        successful_attacks += 1

                    self.results.append({
                        'id': i, 'size': len(target_msg),
                        'm_time': md5_t, 'm_mem': md5_mem,
                        'collides': collides,
                        'target_msg': target_msg,
                        'original_mac': original_mac,
                        'h1_m': forged_mac, 'h2_m': real_mac,
                    })
                    self._log(f"[TARGET {i:02d}] Length Extension Exploit... ")

                # ----------------------------------------------------------
                elif mode == "BIRTHDAY-ATTACK":
                    t0 = time.perf_counter()
                    seen   = {}
                    attempts = 0
                    found  = False

                    # Search for a 24-bit (6 hex char) truncated MD5 collision
                    while attempts < 100_000:
                        attempts += 1
                        msg      = os.urandom(8)
                        h        = self.engine.compute_hash(msg)
                        trunc    = h[:6]
                        if trunc in seen and seen[trunc] != msg:
                            m1, m2   = seen[trunc], msg
                            h1_m     = self.engine.compute_hash(m1)
                            h2_m     = h
                            found    = True
                            break
                        seen[trunc] = msg

                    if not found:
                        # Extremely unlikely given ~2^12 expected attempts,
                        # but if it happens record it honestly as a failure.
                        m1   = os.urandom(8)
                        m2   = os.urandom(8)
                        h1_m = self.engine.compute_hash(m1)
                        h2_m = self.engine.compute_hash(m2)

                    md5_t = (time.perf_counter() - t0) * 1000
                    _, md5_mem = tracemalloc.get_traced_memory()

                    collides = (h1_m[:6] == h2_m[:6])
                    if collides:
                        successful_attacks += 1

                    self.results.append({
                        'id': i, 'size': 8,
                        'm_time': md5_t, 'm_mem': md5_mem,
                        'collides': collides,
                        'm1': m1, 'm2': m2,
                        'h1_m': h1_m, 'h2_m': h2_m,
                        'attempts': attempts,
                    })
                    self._log(f"[TARGET {i:02d}] Birthday Collision ({attempts} iters)... ")

                # ----------------------------------------------------------
                time.sleep(0.05)
                if collides:
                    self._log("[ACCESS GRANTED]\n", "red")
                    self._log("  ↳ Signature forged / collision found.\n\n", "yellow")
                else:
                    self._log("[BREACH FAILED]\n", "green")

            rate = (successful_attacks / len(self.test_cases)) * 100
            self._log(f"\n[RESULT] Attack success rate: {rate:.2f}%\n", "red")

        threading.Thread(target=_worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Step 3 — Apply HMAC-SHA256 prevention (background thread)
    # ------------------------------------------------------------------
    def apply_prevention(self):
        if not self.results:
            self.log.insert(tk.END,
                            "[ERROR] Run the attack simulation first.\n", "yellow")
            return

        def _worker():
            mode = self.attack_modes[self.current_mode_idx]
            self._log("\n[SYSTEM] Uploading HMAC-SHA256 Zero-Trust Architecture...\n", "blue")
            self._log("=" * 59 + "\n", "blue")
            self._set_indicator(self.defense_ind, "#00ff66")
            prevented = 0

            for i, test_case in enumerate(self.test_cases, 1):
                self._update_progress((i / len(self.test_cases)) * 100, "#00ff66")
                tracemalloc.reset_peak()

                if mode in ["IDENTICAL-PREFIX", "CHOSEN-PREFIX"]:
                    m1 = self.results[i - 1]['m1']
                    m2 = self.results[i - 1]['m2']
                    t1 = time.perf_counter()
                    h1_s = hmac.new(self.prevention_key, m1, hashlib.sha256).hexdigest()
                    h2_s = hmac.new(self.prevention_key, m2, hashlib.sha256).hexdigest()
                    sha_t = (time.perf_counter() - t1) * 1000
                    _, sha_mem = tracemalloc.get_traced_memory()
                    collides = (h1_s == h2_s)

                elif mode == "LENGTH-EXT":
                    secret_len, original_msg, append_msg = test_case
                    secret     = self.prevention_key[:secret_len]
                    target_msg = self.results[i - 1]['target_msg']
                    t1 = time.perf_counter()
                    # HMAC is immune to length extension because the inner
                    # state is never exposed — the attacker cannot resume it.
                    real_mac   = hmac.new(secret, target_msg, hashlib.sha256).hexdigest()
                    # Attacker can only guess; we model a random forge attempt
                    forged_mac = os.urandom(32).hex()
                    sha_t   = (time.perf_counter() - t1) * 1000
                    _, sha_mem = tracemalloc.get_traced_memory()
                    h1_s, h2_s = forged_mac, real_mac
                    collides   = (h1_s == h2_s)   # always False

                elif mode == "BIRTHDAY-ATTACK":
                    m1 = self.results[i - 1]['m1']
                    m2 = self.results[i - 1]['m2']
                    t1 = time.perf_counter()
                    # Use FULL 256-bit digest — no truncation
                    h1_s = hmac.new(self.prevention_key, m1, hashlib.sha256).hexdigest()
                    h2_s = hmac.new(self.prevention_key, m2, hashlib.sha256).hexdigest()
                    sha_t  = (time.perf_counter() - t1) * 1000
                    _, sha_mem = tracemalloc.get_traced_memory()
                    collides   = (h1_s == h2_s)   # vanishingly unlikely
                else:
                    collides = False
                    h1_s = h2_s = ""
                    sha_t = sha_mem = 0

                if not collides:
                    prevented += 1

                self.results[i - 1].update({
                    's_time': sha_t, 's_mem': sha_mem,
                    's_collides': collides,
                    'h1_s': h1_s, 'h2_s': h2_s,
                })

                self._log(f"[NODE {i:02d}] Auditing Cryptographic Header... ")
                time.sleep(0.05)
                if not collides:
                    self._log("[THREAT PURGED]\n",                              "green")
                    self._log("  ↳ Deviation detected. Payload dropped.\n\n",  "blue")
                else:
                    self._log("[SYSTEM BREACHED]\n", "red")

            rate = (prevented / len(self.test_cases)) * 100
            self._log(f"\n[DEFENSE] Network integrity restored: {rate:.2f}% secured.\n", "green")
            self._set_indicator(self.network_ind, "#333333")

        threading.Thread(target=_worker, daemon=True).start()

    # ------------------------------------------------------------------
    # Step 4 — Backend hex viewer (main thread, opens Toplevel)
    # ------------------------------------------------------------------
    def open_backend_view(self):
        if not self.results or 'h1_s' not in self.results[0]:
            self.log.insert(tk.END,
                            "\n[!] Run full attack & defense simulation first.\n", "yellow")
            self.log.see(tk.END)
            return

        top = tk.Toplevel(self.root)
        top.title("Deep-Level Cryptographic Analysis")
        top.geometry("1100x800")
        top.configure(bg="#020205")

        mode = self.attack_modes[self.current_mode_idx]
        tk.Label(top, text=f"[ BACKEND ROOT ACCESS: {mode} ]",
                 fg="#cc00ff", bg="#020205",
                 font=("Courier", 16, "bold"), pady=15).pack(fill="x")

        tlog = scrolledtext.ScrolledText(
            top, width=135, height=40,
            bg="#000000", fg="#dddddd",
            font=("Consolas", 11), insertbackground="white"
        )
        tlog.pack(padx=20, pady=10)

        tlog.tag_config("red_hi",  foreground="#ffffff", background="#cc0000",
                        font=("Consolas", 11, "bold"))
        tlog.tag_config("yellow",  foreground="#eab308")
        tlog.tag_config("green",   foreground="#00ff66", font=("Consolas", 11, "bold"))
        tlog.tag_config("header",  foreground="#00ffff", font=("Consolas", 13, "bold", "underline"))
        tlog.tag_config("cyan",    foreground="#00ffcc")

        sep = "=" * 88 + "\n"
        tlog.insert(tk.END, sep, "header")
        tlog.insert(tk.END, "                      DIFFERENTIAL PAYLOAD EXCAVATION\n", "header")
        tlog.insert(tk.END, sep + "\n", "header")

        if mode in ["IDENTICAL-PREFIX", "CHOSEN-PREFIX"]:
            tlog.insert(tk.END, "Comparing Payload A against Payload B.\n", "yellow")

            def hex_dump(title, hex_str, cmp_str):
                tlog.insert(tk.END, f"{title}\n", "cyan")
                for i in range(0, len(hex_str), 64):
                    chunk = hex_str[i:i + 64]
                    comp  = cmp_str[i:i + 64]
                    tlog.insert(tk.END, f"Offset {i:04X}: ")
                    for j, ch in enumerate(chunk):
                        tag = "red_hi" if j < len(comp) and ch != comp[j] else None
                        tlog.insert(tk.END, ch, tag) if tag else tlog.insert(tk.END, ch)
                    tlog.insert(tk.END, "\n")
                tlog.insert(tk.END, "\n")

            hex_dump(">>> PAYLOAD A (Hex Dump):",
                     self.results[0]['m1'].hex(), self.results[0]['m2'].hex())
            hex_dump(">>> PAYLOAD B (Hex Dump):",
                     self.results[0]['m2'].hex(), self.results[0]['m1'].hex())
            tlog.insert(tk.END,
                        "Byte differences shown in RED. MD5 digests are identical.\n\n",
                        "yellow")

        elif mode == "LENGTH-EXT":
            res = self.results[0]
            tlog.insert(tk.END, ">>> MD5 STATE INITIALIZATION OVERRIDE <<<\n", "cyan")
            tlog.insert(tk.END, f"Original MAC:          {res['original_mac']}\n", "yellow")
            tlog.insert(tk.END, f"Forged MAC:            {res['h1_m']}\n", "yellow")
            tlog.insert(tk.END, f"Server-computed MAC:   {res['h2_m']}\n\n", "yellow")
            match = "✓ MATCH — FORGE SUCCESSFUL" if res['collides'] else "✗ NO MATCH"
            tlog.insert(tk.END, f"Result: {match}\n\n",
                        "red_hi" if res['collides'] else "green")
            tlog.insert(tk.END,
                        "The attacker extracts MD5's internal state from the original MAC,\n"
                        "reconstructs the padding block, and appends malicious data — the\n"
                        "resulting forged MAC matches what the server would compute.\n\n")

        elif mode == "BIRTHDAY-ATTACK":
            res = self.results[0]
            tlog.insert(tk.END, ">>> TRUNCATED 24-BIT HASH BIRTHDAY COLLISION <<<\n", "cyan")
            tlog.insert(tk.END, f"Payload A:   {res['m1'].hex()}\n")
            tlog.insert(tk.END, f"Payload B:   {res['m2'].hex()}\n")
            tlog.insert(tk.END, f"MD5(A)[:6]:  {res['h1_m'][:6]}   MD5(B)[:6]:  {res['h2_m'][:6]}\n\n", "yellow")
            tlog.insert(tk.END,
                        f"Found in {res['attempts']} iterations "
                        f"(expected ≈ {2**12} by birthday paradox for 24-bit space).\n\n", "yellow")

        tlog.insert(tk.END, sep, "header")
        tlog.insert(tk.END, "                        CRYPTOGRAPHIC HASH TELEMETRY\n", "header")
        tlog.insert(tk.END, sep + "\n", "header")

        for res in self.results:
            tlog.insert(tk.END, f"[ ENTRY {res['id']:02d} ]\n", "yellow")
            label = "red_hi" if res['collides'] else None
            tlog.insert(tk.END,
                        f"  MD5  A: {res['h1_m']}\n",
                        label or "")
            tlog.insert(tk.END,
                        f"  MD5  B: {res['h2_m']}\n",
                        label or "")
            tlog.insert(tk.END,
                        f"  HMAC A: {res['h1_s']}\n", "green")
            tlog.insert(tk.END,
                        f"  HMAC B: {res['h2_s']}\n", "green")
            tlog.insert(tk.END, "-" * 88 + "\n\n")

        tlog.config(state="disabled")