import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from file_organiser import MediaOrganiser
import threading
import queue
import sys
import time

from datetime import datetime

from datetime import datetime


class StdoutRedirector:
    def __init__(self, queue):
        self.queue = queue
        self._buffer = ""

    def write(self, text):
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.queue.put(f"[{timestamp}] {line}\n")

    def flush(self):
        if self._buffer.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.queue.put(f"[{timestamp}] {self._buffer.strip()}\n")
            self._buffer = ""


class MediaOrganiserGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Media File Organizer")
        self.geometry("800x650")
        self.resizable(False, False)

        self.log_queue = queue.Queue()
        self.cancel_event = threading.Event()

        self.create_widgets()
        self.after(100, self.process_log_queue)

    def create_widgets(self):
        # Folder selection
        tk.Label(self, text="Media Folder:").pack(anchor="w", padx=20, pady=(15, 5))

        folder_frame = tk.Frame(self)
        folder_frame.pack(fill="x", padx=20)

        self.path_var = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.path_var).pack(side="left", fill="x", expand=True)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side="left", padx=5)

        # Organize mode
        tk.Label(self, text="Organize by:").pack(anchor="w", padx=20, pady=(10, 5))

        self.organize_var = tk.StringVar(value="none")
        modes = [
            ("None", "none"),
            ("Year", "year"),
            ("Year / Month", "year_month"),
            ("Year / Month / Day", "year_month_day"),
        ]
        for text, value in modes:
            tk.Radiobutton(self, text=text, variable=self.organize_var, value=value) \
                .pack(anchor="w", padx=40)

        # Options
        self.remove_duplicates_var = tk.BooleanVar()
        self.dry_run_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Remove duplicates", variable=self.remove_duplicates_var) \
            .pack(anchor="w", padx=20)
        tk.Checkbutton(self, text="Dry run", variable=self.dry_run_var) \
            .pack(anchor="w", padx=20)

        # Progress bar
        tk.Label(self, text="Progress:").pack(anchor="w", padx=20, pady=(10, 5))
        self.progress = ttk.Progressbar(self, length=760, mode="determinate", maximum=100)
        self.progress.pack(padx=20)
        self.progress_label = tk.Label(self, text="0 %")
        self.progress_label.pack(anchor="e", padx=25)
        self.eta_label = tk.Label(self, text="ETA: --:--:--")
        self.eta_label.pack(anchor="e", padx=25, pady=(0, 10))

        # Run and Cancel buttons (centered above log)
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.run_btn = tk.Button(
            btn_frame,
            text="▶ Run Organizer",
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 12, "bold"),
            height=2,
            command=self.start
        )
        self.run_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.cancel_btn = tk.Button(
            btn_frame,
            text="✖ Cancel",
            bg="#f44336",
            fg="white",
            font=("Helvetica", 12, "bold"),
            height=2,
            state="disabled",
            command=self.cancel
        )
        self.cancel_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Log output
        tk.Label(self, text="Log output:").pack(anchor="w", padx=20, pady=(10, 5))
        # Log output
        tk.Label(self, text="Log output:").pack(anchor="w", padx=20, pady=(10, 5))
        self.log_text = tk.Text(
            self,
            height=15,
            state="disabled",
            bg="#1e1e1e",
            fg="#dcdcdc",
            insertbackground="#dcdcdc",  # cursor color
            font=("Consolas", 10),
            wrap="none"
        )
        self.log_text.pack(fill="both", padx=20, pady=(0, 20))

        # Add scrollbars
        self.log_scroll_y = tk.Scrollbar(self.log_text.master, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scroll_y.set)
        self.log_scroll_y.pack(side="right", fill="y")

        self.log_scroll_x = tk.Scrollbar(self.log_text.master, orient="horizontal", command=self.log_text.xview)
        self.log_text.configure(xscrollcommand=self.log_scroll_x.set)
        self.log_scroll_x.pack(side="bottom", fill="x")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def start(self):
        if not self.path_var.get():
            messagebox.showerror("Error", "Please select a folder")
            return

        self.progress["value"] = 0
        self.progress_label.config(text="0 %")
        self.eta_label.config(text="ETA: --:--:--")
        self.cancel_event.clear()

        self.run_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

        threading.Thread(target=self.run_organizer, daemon=True).start()

    def cancel(self):
        self.cancel_event.set()
        self.log_queue.put("⚠ Cancel requested...\n")

    def update_progress(self, processed, total, eta):
        percent = int((processed / total) * 100)
        self.progress["value"] = percent
        self.progress_label.config(text=f"{percent} %")

        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta))
        self.eta_label.config(text=f"ETA: {eta_str}")

    def run_organizer(self):
        sys.stdout = StdoutRedirector(self.log_queue)

        try:
            organizer = MediaOrganiser(
                path=self.path_var.get(),
                organize_mode=self.organize_var.get(),
                remove_duplicates=self.remove_duplicates_var.get(),
                dry_run=self.dry_run_var.get(),
                progress_callback=self.update_progress,
                cancel_callback=lambda: self.cancel_event.is_set()
            )
            organizer.run()

            if self.cancel_event.is_set():
                self.log_queue.put("❌ Operation cancelled by user.\n")
            else:
                self.log_queue.put("✅ Operation completed successfully.\n")

        except Exception as e:
            self.log_queue.put(f"❌ Error: {e}\n")

        finally:
            sys.stdout = sys.__stdout__
            self.run_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")

    def process_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state="normal")
                self.log_text.insert("end", msg)
                self.log_text.see("end")
                self.log_text.config(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)


if __name__ == "__main__":
    app = MediaOrganiserGUI()
    app.mainloop()
