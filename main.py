#                      __               __                                     __  __        __           ____
#    ____  ____ ______/ /_  ____ ______/ /_  ____  ____       ____  ________  / /_/ /___  __/ /__  ____ _/ __/
#   / __ \/ __ `/ ___/ __ \/ __ `/ ___/ __ \/ __ \/ __ \     / __ \/ ___/ _ \/ __/ __/ / / / / _ \/ __ `/ /_  
#  / /_/ / /_/ (__  ) / / / /_/ / /__/ / / / /_/ / /_/ /    / /_/ / /  /  __/ /_/ /_/ /_/ / /  __/ /_/ / __/  
# / .___/\__,_/____/_/ /_/\__,_/\___/_/ /_/\____/\____/    / .___/_/   \___/\__/\__/\__, /_/\___/\__,_/_/     
#/_/                       https://boosty.to/pashachoo    /_/       ttv/pr3ttyleaf /____/                    
#                          version 1.0 PYTHON RECODE     
#
import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# forcing program to only launch .py and .bat files, so we get better logs aight
def launch_file(file_path):
    try:
        if file_path.endswith('.py'):
            subprocess.run(['python', file_path], check=True)
        elif file_path.endswith('.bat'):
            subprocess.run([file_path], shell=True, check=True)
        else:
            messagebox.showerror("Error", "Files include unsupported script format!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to execute {file_path}: {e}")

# visual tweaks
root = tk.Tk()
root.title("High-ping servers blocker")
root.iconbitmap('icon.ico')
root.geometry('400x400')
root.resizable(False, False)
root.configure(bg='gray')
frame = tk.Frame(root, bg='gray')
frame.pack(expand=True)


# bOOOOOOOOOOOOttons
btn_0 = tk.Button(root, text="Scan w/o subnet", command=lambda: launch_file('nosubnet.py'))
btn_18 = tk.Button(root, text="Scan w/ 18 subnet", command=lambda: launch_file('18subnet.py'))
btn_20 = tk.Button(root, text="Scan w/ 20 subnet", command=lambda: launch_file('20subnet.py'))
btn_24 = tk.Button(root, text="Scan w/ 24 subnet", command=lambda: launch_file('24subnet.py'))

# Pack buttons to the frame with some padding
btn_0.pack(pady=10)
btn_18.pack(pady=10)
btn_20.pack(pady=10)
btn_24.pack(pady=10)

# links & version
def open_github():
    subprocess.run(['start', 'https://github.com/Rockstar234/apex-high-ping'], shell=True)

btn_github = tk.Button(root, text="GitHub repo", command=open_github)
btn_github.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

version_label = tk.Label(root, text="v1.0", bg='gray')
version_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-40)

# someone pay me if it works plspsssspslsls
root.mainloop()
