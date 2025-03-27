import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import os

# Nyelvi támogatás
LANGUAGES = {
    "hu": {
        "title": "Fájl entrópia elemző",
        "select_dir": "Könyvtár kiválasztása",
        "load_files": "Fájlok betöltése",
        "save_png": "Mentés PNG",
        "save_svg": "Mentés SVG",
        "help": "Súgó",
        "window_size": "Ablakméret (byte):",
        "error_title": "Hiba",
        "error_msg": "Érvénytelen ablakméret. Pozitív egész szám szükséges.",
        "plot_title": "Entrópia profil (ablakméret = {size} bájt)",
        "x_label": "Ablak indexe",
        "y_label": "Entrópia (bit/byte)",
        "popup_title": "Offset információ",
        "copy_button": "Másolás vágólapra",
        "help_text": (
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
        ),
        "structured": "Strukturált",
        "text": "Szöveg",
        "compressed": "Tömörített",
        "encrypted": "Titkosított",
        "language": "Nyelv kiválasztása",
        "toggle_menu": "Menü elrejtése"
    },
    "en": {
        "title": "File Entropy Analyzer",
        "select_dir": "Select Directory",
        "load_files": "Load Files",
        "save_png": "Save PNG",
        "save_svg": "Save SVG",
        "help": "Help",
        "window_size": "Window Size (bytes):",
        "error_title": "Error",
        "error_msg": "Invalid window size. Please enter a positive integer.",
        "plot_title": "Entropy Profile (window size = {size} bytes)",
        "x_label": "Window Index",
        "y_label": "Entropy (bits/byte)",
        "popup_title": "Offset Info",
        "copy_button": "Copy to Clipboard",
        "help_text": (
            "📊 Entropy Analysis Help:\n\n"
            "🔹 Entropy measures data randomness (0–8 bits/byte).\n"
            "🔹 General interpretation:\n"
            "    - 0–2: highly structured (e.g., tables, zeros)\n"
            "    - 2–5: text, encoded strings (e.g., UTF-8/UTF-16)\n"
            "    - 5–7: compressed data (e.g., zlib, LZ4, ZSTD)\n"
            "    - 7–8: encrypted or random data (e.g., AES, RNG)\n\n"
            "🔹 Window Size:\n"
            "    Small → more detail, more noise\n"
            "    Large → smoother, less resolution\n\n"
            "Recommended Sizes:\n"
            "  64–256: Fine patterns (structured files)\n"
            "  512–1024: General use\n"
            "  4096+: Large compressed blocks\n\n"
            "📌 Usage:\n"
            "1. Select a folder.\n"
            "2. Select files.\n"
            "3. Enter window size.\n"
            "4. Click 'Load Files'.\n"
            "5. Navigate: zoom, drag, export.\n\n"
            "🧠 Interactive:\n"
            " - Click to see exact offset and entropy.\n"
            " - Colored bands reflect entropy ranges."
        ),
        "structured": "Structured",
        "text": "Text",
        "compressed": "Compressed",
        "encrypted": "Encrypted",
        "language": "Select Language",
        "toggle_menu": "Hide Menu"
    }
}

# A nyelv beállítása
lang = "hu"
def tr(key):
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, LANGUAGES["en"].get(key, key))

# A további módosításokat mostantól e fordítási függvény használatával végezzük
# A teljes GUI-t és funkciókat ezzel fogjuk lokalizálni

# A nyelvválasztó integrálása következik – ezt a GUI főablakához kell hozzáadni

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

class LanguageSelector:
    def __init__(self, master, callback):
        self.var = tk.StringVar(value=lang)
        self.dropdown = ttk.OptionMenu(master, self.var, lang, *LANGUAGES.keys(), command=self.change_language)
        self.dropdown.pack(anchor="ne", padx=5, pady=2)
        self.callback = callback
        

    def change_language(self, selected):
        global lang
        lang = selected
        self.callback()

class EntropyApp:
    def __init__(self, root):
        self.root = root
        self.root.title(tr("title"))
        self.files = []
        self.entropy_data = {}

        # Először létrehozzuk a frame-t
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # A LanguageSelector inicializálása most már megfelelő, mivel a frame már létezik
        self.language_selector = LanguageSelector(self.frame, self.update_texts)

        # További GUI komponensek inicializálása
        self.left_frame = tk.Frame(self.frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.toggle_button = tk.Button(self.right_frame, text="Hide Menu", command=self.toggle_menu)
        self.toggle_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.dir_button = tk.Button(self.left_frame, text="Select Directory", command=self.select_directory)
        self.dir_button.pack(pady=5)

        self.file_listbox = tk.Listbox(self.left_frame, selectmode=tk.MULTIPLE, width=40)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.window_label = tk.Label(self.left_frame, text=tr("window_size"))
        self.window_label.pack(pady=(10, 0))
        self.window_size_var = tk.IntVar(value=256)
        self.window_entry = tk.Entry(self.left_frame, textvariable=self.window_size_var, width=20)
        self.window_entry.pack(pady=2)

        self.load_button = tk.Button(self.left_frame, text=tr("load_files"), command=self.load_selected_files)
        self.load_button.pack(pady=5)

        self.save_png_button = tk.Button(self.left_frame, text=tr("save_png"), command=lambda: self.save_plot("png"))
        self.save_png_button.pack(pady=2)

        self.save_svg_button = tk.Button(self.left_frame, text=tr("save_svg"), command=lambda: self.save_plot("svg"))
        self.save_svg_button.pack(pady=2)

        self.help_button = tk.Button(self.left_frame, text=tr("help"), command=self.show_help)
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

    def toggle_menu(self):
        # Ha el van rejtve a bal oldali menü, akkor visszaállítjuk, ha látható, akkor elrejtjük
        if self.left_frame.winfo_ismapped():
            self.left_frame.pack_forget()
            self.toggle_menu_button.config(text=tr("toggle_menu"))
        else:
            self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
    def update_texts(self):
        self.root.title(tr("title"))
        self.window_label.config(text=tr("window_size"))
        self.load_button.config(text=tr("load_files"))
        self.help_button.config(text=tr("help"))
    
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
            messagebox.showerror(tr("error_title"), tr("error_msg"))
            return

        selected_indices = self.file_listbox.curselection()
        self.ax.clear()
        self.entropy_data.clear()

        self.ax.set_ylim(0, 8)
        self.ax.axhspan(0, 2, color='green', alpha=0.1, label=tr("structured"))
        self.ax.axhspan(2, 5, color='blue', alpha=0.1, label=tr("text"))
        self.ax.axhspan(5, 7, color='orange', alpha=0.1, label=tr("compressed"))
        self.ax.axhspan(7, 8, color='red', alpha=0.1, label=tr("encrypted"))

        for i in selected_indices:
            filename = self.file_listbox.get(i)
            path = os.path.join(self.dir_path, filename)
            with open(path, "rb") as f:
                data = f.read()
                entropy = calculate_entropy(data, window_size=window_size)
                label = filename
                self.entropy_data[label] = entropy
                self.ax.plot(entropy, label=label, picker=True)

        self.ax.set_title(tr("plot_title").format(size=window_size))
        self.ax.set_xlabel(tr("x_label"))
        self.ax.set_ylabel(tr("y_label"))
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

        copy_button = tk.Button(top, text=tr("copy_button"), command=copy_to_clipboard)
        copy_button.pack(pady=5)

    def show_help(self):
        help_text = tr(
            "help_text"
        )
        messagebox.showinfo(tr("help"), help_text)

# Indítás
if __name__ == "__main__":
    root = tk.Tk()
    app = EntropyApp(root)
    root.mainloop()
