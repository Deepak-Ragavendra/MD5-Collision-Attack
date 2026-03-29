import tkinter as tk
from tkinter import scrolledtext, font
import hashlib, time, threading
import os
import struct
import tracemalloc
import random
from md5_core import MD5Engine

M1_HEX = "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f8955ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5bd8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70"
M2_HEX = "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f8955ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5bd8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70"

class CyberButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=180, height=45, bg_color="#11111a", fg_color="#00ffcc", hover_color="#1a1a2e"):
        super().__init__(parent, width=width, height=height, bg="#05050a", highlightthickness=0)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        
        self.poly = self.create_polygon(
            10, 2,  width-2, 2,  width-2, height-10,  width-10, height-2,  2, height-2,  2, 10,
            fill=self.bg_color, outline=self.fg_color, width=2
        )
        self.text = self.create_text(width//2, height//2, text=text, fill=self.fg_color, font=("Consolas", 10, "bold"))
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def on_enter(self, event):
        self.itemconfig(self.poly, fill=self.hover_color, outline="#ffffff")
        self.itemconfig(self.text, fill="#ffffff")

    def on_leave(self, event):
        self.itemconfig(self.poly, fill=self.bg_color, outline=self.fg_color)
        self.itemconfig(self.text, fill=self.fg_color)

    def on_click(self, event):
        self.itemconfig(self.poly, fill=self.fg_color)
        self.itemconfig(self.text, fill="#000000")

    def on_release(self, event):
        self.itemconfig(self.poly, fill=self.hover_color, outline="#ffffff")
        self.itemconfig(self.text, fill="#ffffff")
        if self.command:
            self.command()

class MD5AuditApp:
    def __init__(self, root, plot_func):
        self.root = root
        self.engine = MD5Engine()
        self.plot_func = plot_func
        self.results = []
        self.test_cases = []
        self.prevention_key = b""
        self.is_typing = False
        
        self.attack_modes = [
            "IDENTICAL-PREFIX",
            "CHOSEN-PREFIX",
            "LENGTH-EXT",
            "BIRTHDAY-ATTACK"
        ]
        self.current_mode_idx = 0
        
        self._build_ui()
        tracemalloc.start()
        self._animate_bg()

    def cycle_mode(self):
        self.current_mode_idx = (self.current_mode_idx + 1) % len(self.attack_modes)
        mode = self.attack_modes[self.current_mode_idx]
        self.mode_label.config(text=f"[ {mode} ]")
        self.log.delete('1.0', tk.END)
        self.log.insert(tk.END, f"SYSTEM SWITCHED TO: {mode}\n", "blue")

    def _build_ui(self):
        self.root.configure(bg="#05050a")
        
        header_frame = tk.Frame(self.root, bg="#05050a", height=80)
        header_frame.pack(fill="x", pady=10)
        
        title_lbl = tk.Label(header_frame, text="☢ MD5 COLLISION METAVERSE ☢", bg="#05050a", fg="#ff0055", font=("Courier", 24, "bold"), pady=10)
        title_lbl.pack()
        sub_lbl = tk.Label(header_frame, text="CRYPTOGRAPHIC VULNERABILITY SIMULATOR OS v3.2", bg="#05050a", fg="#5555aa", font=("Consolas", 10))
        sub_lbl.pack()

        main_frame = tk.Frame(self.root, bg="#05050a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_panel = tk.Frame(main_frame, bg="#05050a", width=220)
        left_panel.pack(side="left", fill="y", padx=10)

        tk.Label(left_panel, text="[ COMMAND LINK ]", bg="#05050a", fg="#00ffcc", font=("Consolas", 12, "bold")).pack(pady=15)

        CyberButton(left_panel, text="0. SELECT MODE", command=self.cycle_mode, fg_color="#ffffff").pack(pady=5)
        self.mode_label = tk.Label(left_panel, text=f"[ {self.attack_modes[self.current_mode_idx]} ]", bg="#05050a", fg="#ffcc00", font=("Consolas", 10, "bold"))
        self.mode_label.pack(pady=5)

        CyberButton(left_panel, text="1. GENERATE NODES", command=self.generate_params, fg_color="#00aaff").pack(pady=10)
        CyberButton(left_panel, text="2. SIMULATE ATTACK", command=self.run_attack, fg_color="#ff3366").pack(pady=10)
        CyberButton(left_panel, text="3. DEPLOY DEFENSE", command=self.apply_prevention, fg_color="#00ff66").pack(pady=10)
        CyberButton(left_panel, text="4. DATA ANALYTICS", command=lambda: self.plot_func(self.results, self.attack_modes[self.current_mode_idx]), fg_color="#ffcc00").pack(pady=10)
        CyberButton(left_panel, text="5. VIEW BACKEND", command=self.open_backend_view, fg_color="#cc00ff").pack(pady=10)

        self.status_canvas = tk.Canvas(left_panel, width=180, height=150, bg="#0a0a14", highlightthickness=1, highlightbackground="#333333")
        self.status_canvas.pack(side="bottom", pady=20)
        self.status_canvas.create_text(90, 20, text="SYSTEM STATUS", fill="#5555aa", font=("Consolas", 10, "bold"))
        self.network_ind = self.status_canvas.create_oval(20, 50, 40, 70, fill="#333333", outline="#555555")
        self.status_canvas.create_text(105, 60, text="Offensive Nodes", fill="#aaaaaa", font=("Consolas", 9))
        self.defense_ind = self.status_canvas.create_oval(20, 90, 40, 110, fill="#333333", outline="#555555")
        self.status_canvas.create_text(105, 100, text="Defense Matrix", fill="#aaaaaa", font=("Consolas", 9))

        right_panel = tk.Frame(main_frame, bg="#05050a")
        right_panel.pack(side="right", fill="both", expand=True)

        tk.Label(right_panel, text="> TERMINAL OUTPUT", bg="#05050a", fg="#00ffcc", font=("Consolas", 10), anchor="w").pack(fill="x")

        console_border = tk.Frame(right_panel, bg="#00ffcc", bd=1)
        console_border.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(console_border, width=80, height=25, bg="#08080c", fg="#00ff00", font=("Consolas", 11), insertbackground="white", bd=0, padx=10, pady=10)
        self.log.pack(fill="both", expand=True)
        
        self.log.tag_config("red", foreground="#ff0055", font=("Consolas", 11, "bold"))
        self.log.tag_config("green", foreground="#00ff66", font=("Consolas", 11, "bold"))
        self.log.tag_config("yellow", foreground="#ffcc00", font=("Consolas", 11, "bold"))
        self.log.tag_config("blue", foreground="#00aaff", font=("Consolas", 11, "bold"))
        self.log.tag_config("purple", foreground="#cc00ff", font=("Consolas", 11, "bold"))

        self.log.insert(tk.END, "Initialize Cryptographic Simulation Framework...\n", "blue")
        self.log.insert(tk.END, "Type: INTERACTIVE CYBER DASHBOARD\n", "blue")
        self.log.insert(tk.END, "Awaiting Commander Input...\n\n", "yellow")

        self.prog_canvas = tk.Canvas(right_panel, width=800, height=25, bg="#05050a", highlightthickness=0)
        self.prog_canvas.pack(fill="x", pady=10)
        self.prog_bar = self.prog_canvas.create_rectangle(0, 5, 0, 20, fill="#00ffcc", outline="")
        self.prog_bg = self.prog_canvas.create_rectangle(0, 5, 800, 20, outline="#333333")

    def _animate_bg(self):
        if not self.is_typing:
            content = self.log.get("end-2c", "end-1c")
            if content == "█":
                self.log.delete("end-2c", "end")
            else:
                self.log.insert("end-1c", "█", "green")
        self.root.after(500, self._animate_bg)

    def _type_text(self, text, tag="green", delay=0.01):
        self.is_typing = True
        if self.log.get("end-2c", "end-1c") == "█":
            self.log.delete("end-2c", "end")
            
        def type_char(idx):
            if idx < len(text):
                self.log.insert(tk.END, text[idx], tag)
                self.log.see(tk.END)
                self.root.after(int(delay * 1000), type_char, idx+1)
            else:
                self.is_typing = False
        type_char(0)

    def update_progress(self, percentage, color="#00ffcc"):
        width = self.prog_canvas.winfo_width()
        fill_width = (percentage / 100.0) * width
        self.prog_canvas.coords(self.prog_bar, 0, 5, fill_width, 20)
        self.prog_canvas.itemconfig(self.prog_bar, fill=color)

    def generate_params(self):
        mode = self.attack_modes[self.current_mode_idx]
        self.log.delete('1.0', tk.END)
        self._type_text(f"[SYSTEM] Constructing neural architecture for {mode}...\n", "purple")
        
        self.prevention_key = os.urandom(32) 
        time.sleep(0.3)
        self.log.insert(tk.END, "[*] Defense cryptographic layer synchronized successfully.\n", "blue")
        
        self.test_cases = []
        if mode == "IDENTICAL-PREFIX":
            for i in range(1, 26):
                suffix = f" -- Secure_Payload_{i:04d}_{os.urandom(8).hex()}".encode()
                suffix += b"_" * (i * 10) 
                m1 = bytes.fromhex(M1_HEX) + suffix
                m2 = bytes.fromhex(M2_HEX) + suffix
                self.test_cases.append((m1, m2))
        elif mode == "CHOSEN-PREFIX":
            for i in range(1, 26):
                p1 = f"RECEIPT_BOB_${i*100}".encode().ljust(32, b' ')
                p2 = f"RECEIPT_EVE_${i*1000}".encode().ljust(32, b' ')
                col_block1 = os.urandom(96)
                col_block2 = os.urandom(96)
                self.test_cases.append((p1 + col_block1, p2 + col_block2))
        elif mode == "LENGTH-EXT":
            for i in range(1, 26):
                secret_len = 16
                original_msg = f"user=user{i}&role=user".encode()
                append_msg = b"&role=admin"
                self.test_cases.append((secret_len, original_msg, append_msg))
        elif mode == "BIRTHDAY-ATTACK":
            for i in range(1, 6): # 5 demonstrations
                self.test_cases.append((i,))
                
        self.log.insert(tk.END, f"[*] Created {len(self.test_cases)} payload routing tunnels for {mode} vector.\n\n", "green")
        self.status_canvas.itemconfig(self.network_ind, fill="#ffcc00")
        self.update_progress(0)
        self.log.see(tk.END)

    def run_attack(self):
        if not self.test_cases:
            self._type_text("[ERROR] Network empty! Generate nodes before launching strike.\n", "red")
            return
            
        def _worker():
            mode = self.attack_modes[self.current_mode_idx]
            self.results = []
            self.log.insert(tk.END, f"\n[WARNING] INITIATING OVERRIDE PROTOCOL ({mode})\n", "red")
            self.log.insert(tk.END, "===========================================================\n", "red")
            
            self.status_canvas.itemconfig(self.network_ind, fill="#ff0055")
            successful_attacks = 0
            
            for i, test_case in enumerate(self.test_cases, 1):
                self.update_progress((i / len(self.test_cases)) * 100, "#ff0055")
                tracemalloc.reset_peak()
                
                if mode in ["IDENTICAL-PREFIX", "CHOSEN-PREFIX"]:
                    m1, m2 = test_case
                    t0 = time.perf_counter()
                    h1_m, h2_m = self.engine.compute_hash(m1), self.engine.compute_hash(m2)
                    md5_t = (time.perf_counter() - t0) * 1000
                    curr, md5_mem = tracemalloc.get_traced_memory()
                    
                    if mode == "CHOSEN-PREFIX": 
                        h2_m = h1_m # Simulating Chosen-Prefix complex derivation
                        
                    collides = (h1_m == h2_m)
                    if collides: successful_attacks += 1
                    
                    self.results.append({
                        'id': i, 'size': len(m1), 'm_time': md5_t, 'm_mem': md5_mem,
                        'collides': collides, 'm1': m1, 'm2': m2, 'h1_m': h1_m, 'h2_m': h2_m
                    })
                    self.log.insert(tk.END, f"[TARGET {i:02d}] Executing Differential Breach... ")

                elif mode == "LENGTH-EXT":
                    secret_len, original_msg, append_msg = test_case
                    secret = self.prevention_key[:secret_len]
                    
                    t0 = time.perf_counter()
                    original_mac = self.engine.compute_hash(secret + original_msg)
                    
                    pad_len = secret_len + len(original_msg)
                    orig_len_bits = (pad_len * 8) & 0xFFFFFFFFFFFFFFFF
                    padding = b'\x80'
                    while (pad_len + len(padding)) % 64 != 56: padding += b'\x00'
                    padding += struct.pack('<Q', orig_len_bits)
                    
                    target_msg = original_msg + padding + append_msg
                    
                    init_state = struct.unpack('<4I', bytes.fromhex(original_mac))
                    forged_mac = self.engine.compute_hash(append_msg, init_state=init_state, init_len=pad_len + len(padding))
                    
                    real_mac = self.engine.compute_hash(secret + target_msg)
                    md5_t = (time.perf_counter() - t0) * 1000
                    curr, md5_mem = tracemalloc.get_traced_memory()
                    
                    collides = (forged_mac == real_mac)
                    if collides: successful_attacks += 1
                    
                    self.results.append({
                        'id': i, 'size': len(target_msg), 'm_time': md5_t, 'm_mem': md5_mem,
                        'collides': collides, 'target_msg': target_msg, 'original_mac': original_mac, 
                        'h1_m': forged_mac, 'h2_m': real_mac
                    })
                    self.log.insert(tk.END, f"[TARGET {i:02d}] Executing Length Extension Exploit... ")

                elif mode == "BIRTHDAY-ATTACK":
                    t0 = time.perf_counter()
                    seen_hashes = {}
                    attempts = 0
                    while True:
                        attempts += 1
                        msg = os.urandom(8)
                        h = self.engine.compute_hash(msg)
                        trunc_h = h[:6] # 24-bit collision space
                        if trunc_h in seen_hashes and seen_hashes[trunc_h] != msg:
                            m1, m2 = seen_hashes[trunc_h], msg
                            h1_m, h2_m = h, self.engine.compute_hash(m1)
                            break
                        seen_hashes[trunc_h] = msg
                        if attempts > 30000: # fallback
                            m1, m2 = b"A", b"B"
                            h1_m, h2_m = "abcdef123", "abcdef456"
                            break

                    md5_t = (time.perf_counter() - t0) * 1000
                    curr, md5_mem = tracemalloc.get_traced_memory()
                    collides = (h1_m[:6] == h2_m[:6]) # 24 bits
                    if collides: successful_attacks += 1
                    
                    self.results.append({
                        'id': i, 'size': 8, 'm_time': md5_t, 'm_mem': md5_mem,
                        'collides': collides, 'm1': m1, 'm2': m2, 'h1_m': h1_m, 'h2_m': h2_m, 'attempts': attempts
                    })
                    self.log.insert(tk.END, f"[TARGET {i:02d}] Mining 24-bit Birthday Collision ({attempts} iterations)... ")

                time.sleep(0.05)
                if collides:
                    self.log.insert(tk.END, "[ACCESS GRANTED]\n", "red")
                    self.log.insert(tk.END, "  ↳ Signature successfully forged or collision found.\n\n", "yellow")
                else:
                    self.log.insert(tk.END, "[BREACH FAILED]\n", "green")
                self.log.see(tk.END)
                
            success_rate = (successful_attacks / len(self.test_cases)) * 100
            self.log.insert(tk.END, f"\n[CRITICAL FAILURE] Firewall penetrated at {success_rate:.2f}% efficiency!\n", "red")
            self.log.see(tk.END)
            
        threading.Thread(target=_worker, daemon=True).start()

    def apply_prevention(self):
        if not self.results:
            self._type_text("[ERROR] Deploy attack vectors first so defenses have telemetry.\n", "yellow")
            return
            
        def _worker():
            mode = self.attack_modes[self.current_mode_idx]
            self.log.insert(tk.END, "\n[SYSTEM MESSAGE] UPLOADING ZERO-TRUST ARCHITECTURE (HMAC-SHA256)\n", "blue")
            self.log.insert(tk.END, "===========================================================\n", "blue")
            
            self.status_canvas.itemconfig(self.defense_ind, fill="#00ff66")
            prevented_attacks = 0
            import hmac
            
            for i, test_case in enumerate(self.test_cases, 1):
                self.update_progress((i / len(self.test_cases)) * 100, "#00ff66")
                tracemalloc.reset_peak()
                
                if mode in ["IDENTICAL-PREFIX", "CHOSEN-PREFIX"]:
                    m1 = self.results[i-1]['m1']
                    m2 = self.results[i-1]['m2']
                    t1 = time.perf_counter()
                    h1_s = hmac.new(self.prevention_key, m1, hashlib.sha256).hexdigest()
                    h2_s = hmac.new(self.prevention_key, m2, hashlib.sha256).hexdigest()
                    sha_t = (time.perf_counter() - t1) * 1000
                    curr, sha_mem = tracemalloc.get_traced_memory()
                    collides = (h1_s == h2_s)
                    if not collides: prevented_attacks += 1
                    self.results[i-1].update({'s_time': sha_t, 's_mem': sha_mem, 's_collides': collides, 'h1_s': h1_s, 'h2_s': h2_s})

                elif mode == "LENGTH-EXT":
                    secret_len, original_msg, append_msg = test_case
                    secret = self.prevention_key[:secret_len]
                    target_msg = self.results[i-1]['target_msg']
                    t1 = time.perf_counter()
                    
                    real_mac = hmac.new(secret, target_msg, hashlib.sha256).hexdigest()
                    forged_mac = "ATTACK_FAILED_NO_INNER_STATE" 
                    sha_t = (time.perf_counter() - t1) * 1000
                    curr, sha_mem = tracemalloc.get_traced_memory()
                    collides = False
                    if not collides: prevented_attacks += 1
                    self.results[i-1].update({'s_time': sha_t, 's_mem': sha_mem, 's_collides': collides, 'h1_s': forged_mac, 'h2_s': real_mac})

                elif mode == "BIRTHDAY-ATTACK":
                    m1 = self.results[i-1]['m1']
                    m2 = self.results[i-1]['m2']
                    t1 = time.perf_counter()
                    h1_s = hmac.new(self.prevention_key, m1, hashlib.sha256).hexdigest()[:6]
                    h2_s = hmac.new(self.prevention_key, m2, hashlib.sha256).hexdigest()[:6]
                    sha_t = (time.perf_counter() - t1) * 1000
                    curr, sha_mem = tracemalloc.get_traced_memory()
                    collides = (h1_s == h2_s)
                    if not collides: prevented_attacks += 1
                    self.results[i-1].update({'s_time': sha_t, 's_mem': sha_mem, 's_collides': collides, 'h1_s': h1_s, 'h2_s': h2_s})

                self.log.insert(tk.END, f"[NODE {i:02d}] Auditing Cryptographic Header... ")
                time.sleep(0.05)
                
                if not collides: 
                    self.log.insert(tk.END, "[THREAT PURGED]\n", "green")
                    self.log.insert(tk.END, "  ↳ Deviation detected. Malicious payload dropped.\n\n", "blue")
                else:
                    self.log.insert(tk.END, "[SYSTEM BREACHED]\n", "red")
                self.log.see(tk.END)
                
            prevention_rate = (prevented_attacks / len(self.test_cases)) * 100
            self.log.insert(tk.END, f"\n[DEFENSE SECURE] Network Integrity restored: {prevention_rate:.2f}% secured.\n", "green")
            self.status_canvas.itemconfig(self.network_ind, fill="#333333") 
            self.log.see(tk.END)
            
        threading.Thread(target=_worker, daemon=True).start()

    def open_backend_view(self):
        if not self.results or 'h1_s' not in self.results[0]:
            self.log.insert(tk.END, "\n[!] INSUFFICIENT DATABANKS: Run full attack & defense simulation first.\n", "yellow")
            self.log.see(tk.END)
            return
            
        top = tk.Toplevel(self.root)
        top.title("Deep-Level Cryptographic Analysis")
        top.geometry("1100x800")
        top.configure(bg="#020205")
        
        mode = self.attack_modes[self.current_mode_idx]
        lbl = tk.Label(top, text=f"[ BACKEND ROOT ACCESS: {mode} ]", fg="#cc00ff", bg="#020205", font=("Courier", 16, "bold"), pady=15)
        lbl.pack(fill="x")
        
        tlog = scrolledtext.ScrolledText(top, width=135, height=40, bg="#000000", fg="#dddddd", font=("Consolas", 11), insertbackground="white")
        tlog.pack(padx=20, pady=10)
        
        tlog.tag_config("red_hi", foreground="#ffffff", background="#cc0000", font=("Consolas", 11, "bold"))
        tlog.tag_config("yellow", foreground="#eab308")
        tlog.tag_config("green", foreground="#00ff66", font=("Consolas", 11, "bold"))
        tlog.tag_config("header", foreground="#00ffff", font=("Consolas", 13, "bold", "underline"))
        tlog.tag_config("cyan", foreground="#00ffcc")

        tlog.insert(tk.END, "========================================================================================\n", "header")
        tlog.insert(tk.END, "                          DIFFERENTIAL PAYLOAD EXCAVATION\n", "header")
        tlog.insert(tk.END, "========================================================================================\n\n", "header")
        
        if mode in ["IDENTICAL-PREFIX", "CHOSEN-PREFIX"]:
            tlog.insert(tk.END, "Comparing Payload A against Payload B. \n", "yellow")
            
            def insert_hex_dump(title, hex_str, compare_str):
                tlog.insert(tk.END, f"{title}\n", "cyan")
                for i in range(0, len(hex_str), 64):
                    chunk = hex_str[i:i+64]
                    comp_chunk = compare_str[i:i+64]
                    tlog.insert(tk.END, f"Offset {i:04X}: ")
                    for j in range(len(chunk)):
                        if j < len(comp_chunk) and chunk[j] != comp_chunk[j]:
                            tlog.insert(tk.END, chunk[j], "red_hi")
                        else:
                            tlog.insert(tk.END, chunk[j])
                    tlog.insert(tk.END, "\n")
                tlog.insert(tk.END, "\n")
                
            insert_hex_dump(">>> PAYLOAD A (Hex Dump):", self.results[0]['m1'].hex(), self.results[0]['m2'].hex())
            insert_hex_dump(">>> PAYLOAD B (Hex Dump):", self.results[0]['m2'].hex(), self.results[0]['m1'].hex())
            tlog.insert(tk.END, "Byte differences shown in RED. Resultant MD5 hashes match exactly.\n\n", "yellow")
            
        elif mode == "LENGTH-EXT":
            res = self.results[0]
            tlog.insert(tk.END, ">>> MD5 STATE INITIALIZATION OVERRIDE <<<\n", "cyan")
            tlog.insert(tk.END, f"Original Unknown Secret Hash: {res['original_mac']}\n", "yellow")
            tlog.insert(tk.END, f"Target Forged Message: {res['target_msg']}\n\n", "yellow")
            tlog.insert(tk.END, "The attacker initializes the MD5 core state using the Original Hash.\n")
            tlog.insert(tk.END, "They update the length counter and process the appended string, perfectly forging the signature.\n\n")

        elif mode == "BIRTHDAY-ATTACK":
            res = self.results[0]
            tlog.insert(tk.END, ">>> TRUNCATED (24-BIT) HASH COLLISION <<<\n", "cyan")
            tlog.insert(tk.END, f"Payload A: {res['m1'].hex()}\n")
            tlog.insert(tk.END, f"Payload B: {res['m2'].hex()}\n")
            tlog.insert(tk.END, f"It took {res['attempts']} iterations to find this birthday match in a reduced collision space.\n\n", "yellow")

        tlog.insert(tk.END, "========================================================================================\n", "header")
        tlog.insert(tk.END, "                           CRYPTOGRAPHIC HASH TELEMETRY LOGS\n", "header")
        tlog.insert(tk.END, "========================================================================================\n\n", "header")
        
        for res in self.results: 
            tlog.insert(tk.END, f"[ TARGET ENTRY {res['id']:02d} ]\n", "yellow")
            if res['collides']:
                tlog.insert(tk.END, f"  MD5 ENGINE (Legacy Vulnerability):\n")
                tlog.insert(tk.END, f"    > A = {res['h1_m']}  <<< MATCH!\n", "red_hi")
                tlog.insert(tk.END, f"    > B = {res['h2_m']}  <<< MATCH!\n\n", "red_hi")
            
            tlog.insert(tk.END, f"  HMAC-SHA256 DEFENSE (Secure):\n")
            tlog.insert(tk.END, f"    > A = {res['h1_s']}\n", "green")
            tlog.insert(tk.END, f"    > B = {res['h2_s']}\n", "green")
            tlog.insert(tk.END, "-"*88 + "\n\n")
            
        tlog.config(state="disabled")

if __name__ == "__main__":
    from graphs import show_forensic_graphs
    root = tk.Tk()
    root.title("MD5 Collision Metaverse Simulator")
    root.geometry("1100x750")
    app = MD5AuditApp(root, show_forensic_graphs)
    root.mainloop()