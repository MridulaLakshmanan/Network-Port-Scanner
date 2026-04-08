"""Simple Tkinter GUI fallback for the Network Port Scanner.

This provides a lightweight GUI that works without CustomTkinter and is safe
on older macOS versions. It intentionally keeps styling minimal and focuses on
functionality: enter a target, ports and thread count, start/stop scan, and
view results in a scrolled text widget.
"""
import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from scanner import PortScanner
from utils import ResultFormatter, InputValidator, TimeFormatter, PortInfo


class PortScannerAppTk(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Network Port Scanner (Tk fallback)")
        self.geometry("900x600")

        self.scanner = PortScanner()
        self.scanning = False
        self.scan_start_time = None
        self.service_map = {}

        self._create_widgets()
        self._update_timer()

    def _create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Top controls
        controls = ttk.Frame(frame)
        controls.pack(fill="x")

        ttk.Label(controls, text="Target:").grid(row=0, column=0, sticky="w")
        self.target_var = tk.StringVar(value="127.0.0.1")
        self.target_entry = ttk.Entry(controls, textvariable=self.target_var, width=30)
        self.target_entry.grid(row=0, column=1, padx=6)

        ttk.Label(controls, text="Start:").grid(row=0, column=2, sticky="w")
        self.start_var = tk.StringVar(value="1")
        ttk.Entry(controls, textvariable=self.start_var, width=6).grid(row=0, column=3, padx=6)

        ttk.Label(controls, text="End:").grid(row=0, column=4, sticky="w")
        self.end_var = tk.StringVar(value="1000")
        ttk.Entry(controls, textvariable=self.end_var, width=6).grid(row=0, column=5, padx=6)

        ttk.Label(controls, text="Threads:").grid(row=0, column=6, sticky="w")
        self.threads_var = tk.StringVar(value="50")
        ttk.Entry(controls, textvariable=self.threads_var, width=6).grid(row=0, column=7, padx=6)

        self.start_btn = ttk.Button(controls, text="Start Scan", command=self._start_scan)
        self.start_btn.grid(row=0, column=8, padx=6)
        self.stop_btn = ttk.Button(controls, text="Stop Scan", command=self._stop_scan, state="disabled")
        self.stop_btn.grid(row=0, column=9, padx=6)

        # Results box
        self.results_text = scrolledtext.ScrolledText(frame, height=25, wrap="word")
        self.results_text.pack(fill="both", expand=True, pady=(10, 0))
        self.results_text.configure(font=("Courier", 10))

        # Bottom status
        status = ttk.Frame(frame)
        status.pack(fill="x", pady=(8, 0))
        self.status_label = ttk.Label(status, text="Idle")
        self.status_label.pack(side="left")
        self.timer_label = ttk.Label(status, text="0:00")
        self.timer_label.pack(side="right")

    def _append_result(self, text: str):
        self.results_text.insert("end", text + "\n")
        self.results_text.see("end")
        self.update()

    def _clear_results(self):
        self.results_text.delete(1.0, "end")
        self.scanner.results = []
        self.service_map = {}

    def _update_status(self, status: str):
        self.status_label.configure(text=status)

    def _start_scan(self):
        target = self.target_var.get().strip()
        if not InputValidator.validate_ip(target):
            messagebox.showerror("Invalid Input", "Please enter a valid IP or hostname")
            return

        ok_s, start_p = InputValidator.validate_port(self.start_var.get())
        ok_e, end_p = InputValidator.validate_port(self.end_var.get())
        ok_t, threads = InputValidator.validate_port(self.threads_var.get())

        if not ok_s or not ok_e:
            messagebox.showerror("Invalid Input", "Port numbers must be between 1 and 65535")
            return
        if start_p > end_p:
            messagebox.showerror("Invalid Input", "Start port cannot be greater than end port")
            return
        if not ok_t or threads < 1:
            threads = 50
            self.threads_var.set("50")

        self._clear_results()
        self.scanning = True
        self.scan_start_time = time.time()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._update_status("Scanning...")

        t = threading.Thread(target=self._scan_worker, args=(target, start_p, end_p, threads), daemon=True)
        t.start()

    def _scan_worker(self, target, start_p, end_p, threads):
        port_count = end_p - start_p + 1

        def cb(port, is_open, service, status):
            if port == -1:
                if status == "INFO":
                    self._append_result(service)
                elif status == "ERROR":
                    self._append_result("ERROR: " + service)
            else:
                self.service_map[port] = service
                formatted = ResultFormatter.format_result(port, is_open, service, status)
                self._append_result(formatted)

        self.scanner.scan_ports(target, start_p, end_p, cb, max_workers=threads)

        duration = time.time() - self.scan_start_time
        open_count = len([p for p, o in self.scanner.results if o])
        self._append_result(f"\n\u2713 Scan Complete: {open_count} open ports found (Time: {TimeFormatter.format_duration(duration)})")
        self._scan_complete()

    def _stop_scan(self):
        self.scanner.stop_scan()
        self.scanning = False
        self._append_result("\nScan stopped by user")
        self._scan_complete()

    def _scan_complete(self):
        self.scanning = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._update_status("Idle")

    def _update_timer(self):
        if self.scanning and self.scan_start_time:
            elapsed = time.time() - self.scan_start_time
            self.timer_label.configure(text=TimeFormatter.format_duration(elapsed))
        self.after(200, self._update_timer)


def main():
    app = PortScannerAppTk()
    app.mainloop()


if __name__ == "__main__":
    main()
