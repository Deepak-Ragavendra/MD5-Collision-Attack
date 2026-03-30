import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox


def show_forensic_graphs(results, attack_mode="IDENTICAL-PREFIX"):
    if not results or 's_time' not in results[0]:
        messagebox.showerror("Error", "Please Run Attack and Apply Prevention first!")
        return

    fig, axs = plt.subplots(2, 3, figsize=(16, 9))
    fig.patch.set_facecolor("#0f0f1a")
    fig.suptitle(f"Forensic Analysis: {attack_mode}", color="#00ffcc", fontsize=18, fontweight='bold')

    # --- Compute rates ---
    attack_success    = sum(1 for r in results if r.get('collides', False)) / len(results) * 100
    prevention_success = sum(1 for r in results if not r.get('s_collides', True)) / len(results) * 100

    sizes  = [r['size']  for r in results]
    m_times = [r['m_time'] for r in results]
    s_times = [r['s_time'] for r in results]
    m_mem  = [r['m_mem']  for r in results]
    s_mem  = [r['s_mem']  for r in results]

    # 1. Attack Success Rate
    axs[0, 0].bar(
        ['MD5 (Vulnerable)', 'HMAC-SHA256 (Defense)'],
        [attack_success, 100 - prevention_success],
        color=['#ef4444', '#22c55e']
    )
    axs[0, 0].set_title("1. Attack Success Rate (%)", color="white")
    axs[0, 0].set_ylim(0, 110)

    # 2. Execution Time vs Parameter Size
    axs[0, 1].plot(sizes, m_times, label='MD5 Execution', color='#ef4444', marker='o')
    axs[0, 1].plot(sizes, s_times, label='HMAC-SHA256',   color='#22c55e', marker='x')
    axs[0, 1].set_title("2. Time vs Parameter Size (ms)", color="white")
    axs[0, 1].set_xlabel("Size (bytes)", color="white")
    axs[0, 1].legend(facecolor="#16213e", labelcolor="white")

    # 3. Integrity Validation Rate
    axs[0, 2].bar(
        ['MD5 Integrity', 'HMAC-SHA256 Integrity'],
        [100 - attack_success, prevention_success],
        color=['#ef4444', '#22c55e']
    )
    axs[0, 2].set_title("3. Integrity Validation Rate (%)", color="white")
    axs[0, 2].set_ylim(0, 110)

    # 4. Latency Distribution
    axs[1, 0].boxplot(
        [m_times, s_times],
        labels=['MD5', 'HMAC-SHA256'],
        patch_artist=True,
        boxprops=dict(facecolor="#16213e", color="white"),
        medianprops=dict(color="#00ffcc"),
        whiskerprops=dict(color="white"),
        capprops=dict(color="white"),
        flierprops=dict(markerfacecolor='#ef4444', marker='o')
    )
    axs[1, 0].set_title("4. Latency Overhead Distribution", color="white")

    # 5. Security Improvement Pie
    improvement = prevention_success - (100 - attack_success)
    if improvement <= 0:
        axs[1, 1].pie(
            [100], labels=['No Improvement / Already Secure'],
            colors=['#ef4444'], autopct='%1.1f%%',
            textprops={'color': "white"}
        )
    else:
        axs[1, 1].pie(
            [100 - improvement, improvement],
            labels=['Still Vulnerable', 'Security Improvement'],
            colors=['#ef4444', '#22c55e'],
            autopct='%1.1f%%',
            textprops={'color': "white"}
        )
    axs[1, 1].set_title("5. Security Improvement Breakdown", color="white")

    # 6. Memory Usage vs Size
    axs[1, 2].plot(sizes, m_mem, label='MD5 Memory',       color='#ef4444', marker='^', linestyle='--')
    axs[1, 2].plot(sizes, s_mem, label='HMAC-SHA256 Memory', color='#22c55e', marker='s', linestyle='-.')
    axs[1, 2].set_title("6. Memory Allocation (Bytes)", color="white")
    axs[1, 2].set_xlabel("Size (bytes)", color="white")
    axs[1, 2].legend(facecolor="#16213e", labelcolor="white")

    # Apply dark theme to all subplots
    for i in range(2):
        for j in range(3):
            ax = axs[i, j]
            ax.title.set_color("white")
            if i == 1 and j == 1:
                continue  # pie chart has no axes/ticks to style
            ax.set_facecolor("#16213e")
            ax.tick_params(colors="white")
            ax.yaxis.label.set_color("white")
            for spine in ax.spines.values():
                spine.set_edgecolor('gray')

    plt.tight_layout()
    plt.show()