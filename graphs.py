import matplotlib.pyplot as plt
import numpy as np
from tkinter import messagebox

def show_forensic_graphs(results, attack_mode="IDENTICAL-PREFIX"):
    if not results or 's_time' not in results[0]:
        messagebox.showerror("Error", "Please Run Attack and Apply Prevention first!")
        return
        
    fig, axs = plt.subplots(2, 3, figsize=(16, 9))
    fig.patch.set_facecolor("#0f0f1a") # Matches theme
    fig.suptitle(f"Forensic Analysis: {attack_mode}", color="#00ffcc", fontsize=18, fontweight='bold')
    
    # Extract data
    attack_success = sum(1 for r in results if r.get('collides', False)) / len(results) * 100
    prevention_success = sum(1 for r in results if not r.get('s_collides', True)) / len(results) * 100
    
    sizes = [r['size'] for r in results]
    m_times = [r['m_time'] for r in results]
    s_times = [r['s_time'] for r in results]
    m_mem = [r['m_mem'] for r in results]
    s_mem = [r['s_mem'] for r in results]
    
    # 1. Attack Success Rate
    axs[0, 0].bar(['MD5 Config', 'HMAC-SHA256'], [attack_success, 100 - prevention_success], color=['#ef4444', '#22c55e'])
    axs[0, 0].set_title(f"1. Attack Success Rate (%)", color="white")
    axs[0, 0].set_ylim(0, 110)

    # 2. Time vs Key / Parameter Size
    axs[0, 1].plot(sizes, m_times, label='MD5 Execution', color='#ef4444', marker='o')
    axs[0, 1].plot(sizes, s_times, label='Prevention (HMAC)', color='#22c55e', marker='x')
    axs[0, 1].set_title("2. Time vs Parameter Size (ms)", color="white")
    axs[0, 1].set_xlabel("Size (bytes)", color="white")
    axs[0, 1].legend()

    # 3. Confidentiality / Integrity Rate
    axs[0, 2].bar(['MD5 Integrity', 'HMAC-SHA256 Integrity'], [100 - attack_success, prevention_success], color=['#ef4444', '#22c55e'])
    axs[0, 2].set_title("3. Integrity Validation Rate (%)", color="white")
    axs[0, 2].set_ylim(0, 110)

    # 4. Attack vs Prevention Latency Overhead
    axs[1, 0].boxplot([m_times, s_times], labels=['MD5 Exec', 'Prevention Exec'])
    axs[1, 0].set_title("4. Latency Overhead Distribution", color="white")

    # 5. Security Improvement Percentage (Recommended)
    improvement = prevention_success - (100 - attack_success)
    
    # Ensure pie chart does not crash if improvement is negative or 0
    if improvement <= 0:
        axs[1, 1].pie([100], labels=['No Improvement'], colors=['#ef4444'], autopct='%1.1f%%', textprops={'color':"white"})
    else:
        axs[1, 1].pie([100 - improvement, improvement], labels=['Vulnerable Component', 'Security Improvement'], colors=['#ef4444', '#22c55e'], autopct='%1.1f%%', textprops={'color':"white"})
    
    axs[1, 1].set_title("5. Security Improvement Breakdown", color="white")

    # 6. Resource Usage (Memory vs Size) (Recommended)
    axs[1, 2].plot(sizes, m_mem, label='MD5 Memory', color='#ef4444', marker='^', linestyle='--')
    axs[1, 2].plot(sizes, s_mem, label='HMAC Memory', color='#22c55e', marker='s', linestyle='-.')
    axs[1, 2].set_title("6. Memory Allocation (Bytes)", color="white")
    axs[1, 2].set_xlabel("Size (bytes)", color="white")
    axs[1, 2].legend()

    for i in range(2):
        for j in range(3):
            ax = axs[i, j]
            if not isinstance(ax, plt.Axes): continue
            
            # Exclude background setting for pie chart
            if not (i == 1 and j == 1):
                ax.set_facecolor("#16213e")
                ax.tick_params(colors="white")
                for spine in ax.spines.values():
                    spine.set_edgecolor('gray')
                    
            ax.title.set_color("white")
    
    plt.tight_layout()
    plt.show()