import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import os

# Entrópia számítás
def calculate_entropy(data, window_size=256):
    entropy_values = []
    for i in range(0, len(data) - window_size + 1, window_size):
        window = data[i:i + window_size]
        freq = np.bincount(np.frombuffer(window, dtype=np.uint8), minlength=256)
        prob = freq / window_size
        prob = prob[prob > 0]
        entropy = -np.sum(prob * np.log2(prob))
        entropy_values.append(entropy)
    return entropy_values

class EntropyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fájl entrópia elemző")
        self.files = []
        self.entropy_data = {}

        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.dir_button = tk.Button(self.left_frame, text="Könyvtár kiválasztása", command=self.select_directory)
        self.dir_button.pack(pady=5)

        self.file_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.window_label = tk.Label(self.left_frame, text="Ablakméret (byte):")
        self.window_label.pack(pady=(10, 0))
        self.window_size_var = tk.IntVar(value=256)
        self.window_entry = tk.Entry(self.left_frame, textvariable=self.window_size_var, width=10)
        self.window_entry.pack(pady=2)

        self.load_button = tk.Button(self.left_frame, text="Fájlok betöltése", command=self.load_selected_files)
        self.load_button.pack(pady=5)

        self.save_png_button = tk.Button(self.left_frame, text="Mentés PNG", command=lambda: self.save_plot("png"))
        self.save_png_button.pack(pady=2)

        self.save_svg_button = tk.Button(self.left_frame, text="Mentés SVG", command=lambda: self.save_plot("svg"))
        self.save_svg_button.pack(pady=2)

        self.help_button = tk.Button(self.left_frame, text="Súgó", command=self.show_help)
        self.help_button.pack(pady=10)

        self.figure, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.right_frame)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.right_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.status = tk.Label(self.root, text="", anchor=tk.W)
        self.status.pack(fill=tk.X)

        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_press_event", self.on_click)

        self.annot = self.ax.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                                      bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        self.last_clicked = None

    def select_directory(self):
        directory = filedialog.askdirectory()
        if not directory:
            return
        self.file_listbox.delete(0, tk.END)
        self.dir_path = directory
        for file in os.listdir(directory):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path):
                self.file_listbox.insert(tk.END, file)

    def load_selected_files(self):
        try:
            window_size = int(self.window_entry.get())
            if window_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hiba", "Érvénytelen ablakméret. Pozitív egész szám szükséges.")
            return

        selected_indices = self.file_listbox.curselection()
        self.ax.clear()
        self.entropy_data.clear()

        self.ax.set_ylim(0, 8)
        self.ax.axhspan(0, 2, color='green', alpha=0.1, label='Strukturált')
        self.ax.axhspan(2, 5, color='blue', alpha=0.1, label='Szöveg')
        self.ax.axhspan(5, 7, color='orange', alpha=0.1, label='Tömörített')
        self.ax.axhspan(7, 8, color='red', alpha=0.1, label='Titkosított')

        for i in selected_indices:
            filename = self.file_listbox.get(i)
            path = os.path.join(self.dir_path, filename)
            with open(path, "rb") as f:
                data = f.read()
                entropy = calculate_entropy(data, window_size=window_size)
                label = filename
                self.entropy_data[label] = entropy
                self.ax.plot(entropy, label=label, picker=True)

        self.ax.set_title(f"Entrópia profil (ablakméret = {window_size} bájt)")
        self.ax.set_xlabel("Ablak indexe")
        self.ax.set_ylabel("Entrópia (bit/byte)")
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

    def save_plot(self, format):
        file = filedialog.asksaveasfilename(defaultextension=f".{format}", filetypes=[(f"{format.upper()} fájl", f"*.{format}")])
        if file:
            self.figure.savefig(file, format=format)

    def on_mouse_move(self, event):
        if event.inaxes:
            self.status.config(text=f"X: {int(event.xdata)}, Y: {event.ydata:.2f}")
        else:
            self.status.config(text="")

    def on_click(self, event):
        if not event.inaxes:
            return
        x = int(round(event.xdata))
        messages = []
        for label, values in self.entropy_data.items():
            if x >= 0 and x < len(values):
                entropy_val = values[x]
                offset = x * int(self.window_size_var.get())
                messages.append(f"Fájl: {label}\nOffset: {offset} (0x{offset:X})\nEntrópia: {entropy_val:.2f}")
        if messages:
            msg = "\n\n".join(messages)
            self.show_offset_popup(msg)

    def show_offset_popup(self, msg):
        top = tk.Toplevel(self.root)
        top.title("Offset információ")
        top.geometry("400x200")
        text = tk.Text(top, wrap="word")
        text.insert("1.0", msg)
        text.config(state="normal")
        text.pack(expand=True, fill="both")

        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(msg)
            self.root.update()

        copy_button = tk.Button(top, text="Másolás vágólapra", command=copy_to_clipboard)
        copy_button.pack(pady=5)

    def show_help(self):
        help_text = (
            "📊 Entrópiaelemzés súgó:\n\n"
            "🔹 Az entrópia az adatok rendezetlenségét méri (0–8 bit/byte).\n"
            "🔹 Általános értelmezés:\n"
            "    - 0–2: nagyon strukturált (pl. táblázatok, nullák)\n"
            "    - 2–5: szöveg, kódolt stringek (pl. UTF-8/UTF-16)\n"
            "    - 5–7: tömörített adatok (pl. zlib, LZ4, ZSTD)\n"
            "    - 7–8: titkosított vagy véletlenszerű adatok (pl. AES, RNG)\n\n"
            "🔹 Ablakméret:\n"
            "    Kis érték → részletesebb, de zajosabb\n"
            "    Nagy érték → simább, de elmosódott változások\n\n"
            "Javasolt ablakméretek:\n"
            "  64–256: Finom minták (strukturált fájlok)\n"
            "  512–1024: Általános cél\n"
            "  4096+: Nagy tömörített blokkok\n\n"
            "📌 Használat:\n"
            "1. Válassz könyvtárat.\n"
            "2. Jelöld ki a fájlokat.\n"
            "3. Add meg az ablakméretet.\n"
            "4. Kattints a 'Fájlok betöltése' gombra.\n"
            "5. Navigálj a grafikonon: zoom, húzás, mentés.\n\n"
            "🧠 Interaktív funkciók:\n"
            " - Egérkattintással kiemelheted a pontos offsetet és entrópiaértéket.\n"
            " - Színes sávok fix 0–8 bit/byte skálán mutatják a tartományokat."
        )
        messagebox.showinfo("Súgó", help_text)

# Indítás
if __name__ == "__main__":
    root = tk.Tk()
    app = EntropyApp(root)
    root.mainloop()
