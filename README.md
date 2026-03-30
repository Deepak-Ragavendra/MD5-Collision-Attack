# ☢ MD5 Collision Attack & Prevention Simulator

<p align="center">
  <img src="https://img.shields.io/badge/Cryptography-MD5-red?style=for-the-badge">
  <img src="https://img.shields.io/badge/Security-Attacks-orange?style=for-the-badge">
  <img src="https://img.shields.io/badge/Defense-HMAC--SHA256-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge">
</p>

---

## 🚀 Overview

An interactive cryptographic attack simulator demonstrating real vulnerabilities in the MD5 hashing algorithm, contrasted with a secure HMAC-SHA256 defense. The MD5 engine is implemented from scratch following RFC 1321 — no `hashlib.md5()` is used for the attack demonstrations.

---

## ⚡ Features

* Custom MD5 engine built from scratch (RFC 1321 compliant)
* Real Wang et al. (2004) collision vectors for identical-prefix attacks
* Four distinct attack mode simulations
* Thread-safe interactive GUI (Tkinter)
* 6-panel forensic graph analytics (matplotlib)
* Backend hex dump viewer with byte-level diff highlighting

---

## 📁 Project Structure

```
├── main.py          ← Entry point
├── gui.py           ← Tkinter UI + all attack/defense logic
├── md5_core.py      ← Custom MD5 engine (RFC 1321)
├── graphs.py        ← Matplotlib forensic analysis panels
└── README.md
```

---

## 🎯 Attack Modes

### 🔴 1. Identical-Prefix Collision

Two different messages that produce the exact same MD5 digest.

```
M1 ≠ M2
MD5(M1) = MD5(M2)
```

Uses real Wang et al. (2004) 128-byte collision vectors. A unique suffix is appended to both messages — since the suffix is identical, the collision property is preserved.

---

### 🔴 2. Chosen-Prefix Collision

Two messages with *different* prefixes are made to collide using computed collision-inducing blocks.

```
MD5(Prefix1 || CollisionBlock1) = MD5(Prefix2 || CollisionBlock2)
```

The Wang collision vectors serve as the collision blocks in this simulation. In a real attack, these blocks would be computed per-prefix pair (as done in the 2008 Rogue CA certificate attack).

---

### 🔴 3. Length Extension Attack

An attacker who knows `MD5(secret || message)` and the length of `secret` can forge a valid MAC for `secret || message || padding || malicious_data` — without knowing the secret itself.

```
Known:   MD5(secret || message)  +  len(secret)
Forged:  MD5(secret || message || padding || "&role=admin")
```

This works because MD5 exposes its internal chaining state in the final digest output. The simulator reconstructs that state and resumes hashing.

**HMAC-SHA256 is immune** — the inner state is never exposed.

---

### 🔴 4. Birthday Attack

Exploits the birthday paradox to find a collision in a truncated (24-bit) MD5 digest space. Expected collisions arise after approximately √(2²⁴) ≈ 4,096 random attempts.

```
Find M1 ≠ M2 such that MD5(M1)[:24 bits] = MD5(M2)[:24 bits]
```

The full 256-bit HMAC-SHA256 digest is used in the defense panel, making a collision computationally infeasible.

---

## 🛡 Defense: HMAC-SHA256

| Property | MD5 | HMAC-SHA256 |
|---|---|---|
| Collision resistant | ❌ Broken | ✅ Secure |
| Length extension resistant | ❌ Vulnerable | ✅ Immune |
| Key-based authentication | ❌ No | ✅ Yes |
| Digest size | 128-bit | 256-bit |

---

## 🖥️ Setup

### Requirements

```bash
pip install matplotlib
```

Python 3.8+ required. All other dependencies (`tkinter`, `hashlib`, `hmac`, `struct`) are part of the standard library.

### Run

```bash
python main.py
```

---

## 📋 Usage

Follow the steps in order using the left panel buttons:

| Step | Button | Action |
|---|---|---|
| 0 | SELECT MODE | Cycle through the four attack modes |
| 1 | GENERATE NODES | Build test case payloads for the selected mode |
| 2 | SIMULATE ATTACK | Execute the attack and record results |
| 3 | DEPLOY DEFENSE | Apply HMAC-SHA256 and measure prevention |
| 4 | DATA ANALYTICS | Open 6-panel forensic graph window |
| 5 | VIEW BACKEND | Open hex dump and hash telemetry viewer |

> Steps 1 → 2 → 3 must be completed in order before Analytics or Backend will display results.

---

## 📊 Forensic Graph Panels

1. **Attack Success Rate** — MD5 breach rate vs. HMAC-SHA256 breach rate
2. **Time vs Parameter Size** — Execution latency as payload size grows
3. **Integrity Validation Rate** — Percentage of payloads correctly validated
4. **Latency Distribution** — Box plot of MD5 vs. HMAC-SHA256 overhead
5. **Security Improvement Breakdown** — Pie chart of gain from switching to HMAC
6. **Memory Allocation** — Bytes allocated per payload size for both algorithms

---

## 📚 References

* RFC 1321 — The MD5 Message-Digest Algorithm (Rivest, 1992)
* Wang, X. & Yu, H. (2005). *How to Break MD5 and Other Hash Functions.* EUROCRYPT 2005.
* Lenstra et al. (2008). *MD5 considered harmful today: Creating a rogue CA certificate.*
* RFC 2104 — HMAC: Keyed-Hashing for Message Authentication

---

## 👨‍💻 Authors

Deepak Ragavendra Panbhukarasu || 
Nagarajan Venugopal || 
Andrew Sundaradhas || 