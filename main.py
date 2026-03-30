import tkinter as tk
from gui import MD5AuditApp
from graphs import show_forensic_graphs

if __name__ == "__main__":
    root = tk.Tk()
    root.title("MD5 Collision Attack & Prevention Simulator")
    root.geometry("1100x750")
    app = MD5AuditApp(root, show_forensic_graphs)
    root.mainloop()