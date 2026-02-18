import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from scanner import (
    scan_directory_usage,
    find_large_files,
    find_old_large_files,
    estimate_temp_data,
    human_size,
)


class PCOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PC Organizer")
        self.geometry("980x680")

        self.selected_path = tk.StringVar(value=str(Path.home()))
        self.size_threshold_mb = tk.IntVar(value=250)
        self.old_days = tk.IntVar(value=180)

        self._build_ui()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        controls = ttk.LabelFrame(root, text="Scan Controls", padding=10)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(controls, textvariable=self.selected_path, width=70).grid(row=0, column=1, padx=8, sticky="ew")
        ttk.Button(controls, text="Browse", command=self.pick_folder).grid(row=0, column=2)

        ttk.Label(controls, text="Large file threshold (MB):").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(controls, textvariable=self.size_threshold_mb, width=12).grid(row=1, column=1, sticky="w", pady=(8, 0))

        ttk.Label(controls, text="Old file age (days):").grid(row=1, column=1, sticky="e", pady=(8, 0))
        ttk.Entry(controls, textvariable=self.old_days, width=12).grid(row=1, column=2, sticky="w", pady=(8, 0))

        ttk.Button(controls, text="Analyze", command=self.run_scan_thread).grid(row=2, column=0, pady=(12, 0), sticky="w")
        controls.columnconfigure(1, weight=1)

        self.status = tk.StringVar(value="Select a folder and click Analyze.")
        ttk.Label(root, textvariable=self.status).pack(fill=tk.X, pady=(8, 4))

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.summary_text = tk.Text(notebook, wrap="word", height=8)
        self.large_tree = self._make_tree(notebook, ("size", "path"))
        self.old_tree = self._make_tree(notebook, ("size", "age", "path"))

        notebook.add(self.summary_text, text="Summary")
        notebook.add(self.large_tree, text="Large Files")
        notebook.add(self.old_tree, text="Old + Large")

    def _make_tree(self, parent, columns):
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col.title())
            width = 120 if col != "path" else 700
            tree.column(col, width=width, anchor="w")

        ys = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ys.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ys.pack(side=tk.RIGHT, fill=tk.Y)
        frame.tree = tree
        return frame

    def pick_folder(self):
        directory = filedialog.askdirectory(initialdir=self.selected_path.get())
        if directory:
            self.selected_path.set(directory)

    def run_scan_thread(self):
        path = self.selected_path.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showerror("Invalid folder", "Please select a valid folder to scan.")
            return

        self.status.set("Scanning... this can take a while for large drives.")
        thread = threading.Thread(target=self.perform_scan, daemon=True)
        thread.start()

    def perform_scan(self):
        try:
            threshold_bytes = self.size_threshold_mb.get() * 1024 * 1024
            old_days = self.old_days.get()
            target = Path(self.selected_path.get())

            stats = scan_directory_usage(target)
            large_files = find_large_files(target, threshold_bytes)
            old_large_files = find_old_large_files(target, threshold_bytes, old_days)
            temp_bytes = estimate_temp_data()

            self.after(0, lambda: self.update_results(stats, large_files, old_large_files, temp_bytes, target))
        except Exception as exc:  # Surface unexpected issues in GUI
            self.after(0, lambda: messagebox.showerror("Scan failed", str(exc)))
            self.after(0, lambda: self.status.set("Scan failed."))

    def update_results(self, stats, large_files, old_large_files, temp_bytes, target):
        self.summary_text.delete("1.0", tk.END)

        summary_lines = [
            f"Scanned: {target}",
            f"Files counted: {stats['file_count']:,}",
            f"Total size: {human_size(stats['total_size'])}",
            f"Top extension by size: {stats['top_extension']}",
            f"Potential temp/cache size on this system: {human_size(temp_bytes)}",
            "",
            "Slowdown indicators:",
            "- Very large files can reduce free disk space and impact performance.",
            "- Old large files are good cleanup candidates.",
            "- Large temp/cache folders can be cleaned safely in many cases.",
        ]
        self.summary_text.insert(tk.END, "\n".join(summary_lines))

        self._fill_tree(self.large_tree.tree, [(human_size(size), str(path)) for path, size in large_files[:200]])

        old_rows = []
        for path, size, age_days in old_large_files[:200]:
            old_rows.append((human_size(size), f"{age_days} days", str(path)))
        self._fill_tree(self.old_tree.tree, old_rows)

        self.status.set(
            f"Scan complete. Found {len(large_files)} large files and {len(old_large_files)} old-large files."
        )

    def _fill_tree(self, tree, rows):
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", tk.END, values=row)


def main():
    app = PCOrganizerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
