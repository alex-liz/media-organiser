import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from file_orginiser import MediaOrganizer
import threading
import queue
import sys
import time
import os


class StdoutRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        if text.strip():
            self.queue.put(text)

    def flush(self):
        pass


class MediaOrganizerGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Media File Organizer")
        self.geometry("700x550")
        self.resizable(False, False)

        self.log_queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker_thread = None

        self.create_widgets()
        self.after(100, self.process_log_queue)

    def create_widgets(self):
        # Folder chooser
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

        for label, value in modes:
            tk.Radiobutton(self, text=label, variable=self.organize_var, value=value)\
                .pack(anchor="w", padx=40)

        # Options
        self.remove_duplicates_var = tk.BooleanVar()
        self.dry_run_var = tk.BooleanVar()

        tk.Checkbutton(self, text="Remove duplicates", variable=self.remove_duplicates_var)\
            .pack(anchor="w", padx=20, pady=(5, 0))
        tk.Checkbutton(self, text="Dry run", variable=self.dry_run_var)\
            .pack(anchor="w", padx=20)

        # Progress bar
        tk.Label(self, text="Progress:").pack(anchor="w", padx=20, pady=(10, 5))
        self.progress = ttk.Progressbar(self, length=640, mode="indeterminate")
        self.progress.pack(padx=20)

        # Log output
        tk.Label(self, text="Log output:").pack(anchor="w", padx=20, pady=(10, 5))

        self.log_text = tk.Text(self, height=10, state="disabled")
        self.log_text.pack(fill="both", padx=20)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=15)

        self.run_btn = tk.Button(btn_frame, text="Run", bg="#4CAF50", fg="white",
                                 height=2, command=self.start)
        self.run_btn.pack(side="left", fill="x", expand=True)

        self.cancel_btn = tk.Button(btn_frame, text="Cancel", bg="#f44336", fg="white",
                                    height=2, state="disabled", command=self.cancel)
        self.cancel_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def start(self):
        if not self.path_var.get():
            messagebox.show_error("Error", "Please select a folder")
            return

        self.cancel_event.clear()
        self.progress.start(10)
        self.run_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")

        self.worker_thread = threading.Thread(target=self.run_organizer, daemon=True)
        self.worker_thread.start()

    def cancel(self):
        self.cancel_event.set()
        self.log_queue.put("⚠ Cancel requested...\n")

    def run_organizer(self):
        sys.stdout = StdoutRedirector(self.log_queue)

        try:
            organizer = MediaOrganizer(
                path=self.path_var.get(),
                organize_mode=self.organize_var.get(),
                remove_duplicates=self.remove_duplicates_var.get(),
                dry_run=self.dry_run_var.get()
            )

            organizer.cancel_requested = False

            while not self.cancel_event.is_set():
                organizer.run()
                break

            if self.cancel_event.is_set():
                self.log_queue.put("❌ Operation cancelled by user.\n")
            else:
                self.log_queue.put("✅ Operation completed successfully.\n")

        except Exception as e:
            self.log_queue.put(f"❌ Error: {e}\n")

        finally:
            sys.stdout = sys.__stdout__
            self.progress.stop()
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
    app = MediaOrganizerGUI()
    app.mainloop()
