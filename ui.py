"""
GUI Module
Provides the modern user interface for the network port scanner.
Uses customtkinter for a contemporary look and feel.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import time
from scanner import PortScanner
from utils import ResultFormatter, InputValidator, TimeFormatter, PortInfo


class PortScannerApp(ctk.CTk):
    """
    Main application window for the Network Port Scanner.
    Features modern dark theme with real-time scanning updates.
    """

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Configure window
        self.title("Network Port Scanner")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize scanner
        self.scanner = PortScanner()
        self.scanning = False
        self.scan_start_time = None
        self.service_map = {}

        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Build UI
        self._create_header()
        self._create_input_frame()
        self._create_results_frame()
        self._create_status_bar()

        # Update timer
        self._update_timer()

    def _create_header(self):
        """Create the header section with title and disclaimer."""
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Network Port Scanner",
            font=("Helvetica", 32, "bold"),
            text_color="#00ff88",
        )
        title.pack(pady=15, padx=20)

        # Disclaimer
        disclaimer = ctk.CTkLabel(
            header_frame,
            text="⚠️ Educational & authorized use only. Unauthorized scanning is illegal.",
            font=("Helvetica", 11),
            text_color="#ffaa00",
        )
        disclaimer.pack(pady=(0, 15), padx=20)

    def _create_input_frame(self):
        """Create the input controls frame."""
        input_frame = ctk.CTkFrame(self, fg_color="#0d0d0d")
        input_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
        input_frame.grid_columnconfigure(1, weight=1)

        # Target Label & Input
        target_label = ctk.CTkLabel(
            input_frame,
            text="Target Host:",
            font=("Helvetica", 12, "bold"),
            text_color="#ffffff",
        )
        target_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.target_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter IP address or domain name",
            font=("Helvetica", 11),
            height=40,
        )
        self.target_input.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # Port Range Frame
        port_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        port_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Start Port
        start_label = ctk.CTkLabel(
            port_frame,
            text="Start Port:",
            font=("Helvetica", 12, "bold"),
            text_color="#ffffff",
        )
        start_label.pack(side="left", padx=(0, 10))

        self.start_port_input = ctk.CTkEntry(
            port_frame,
            placeholder_text="1",
            width=100,
            font=("Helvetica", 11),
        )
        self.start_port_input.pack(side="left", padx=(0, 30))
        self.start_port_input.insert(0, "1")

        # End Port
        end_label = ctk.CTkLabel(
            port_frame,
            text="End Port:",
            font=("Helvetica", 12, "bold"),
            text_color="#ffffff",
        )
        end_label.pack(side="left", padx=(0, 10))

        self.end_port_input = ctk.CTkEntry(
            port_frame,
            placeholder_text="65535",
            width=100,
            font=("Helvetica", 11),
        )
        self.end_port_input.pack(side="left", padx=(0, 30))
        self.end_port_input.insert(0, "1000")

        # Thread Count
        thread_label = ctk.CTkLabel(
            port_frame,
            text="Threads:",
            font=("Helvetica", 12, "bold"),
            text_color="#ffffff",
        )
        thread_label.pack(side="left", padx=(0, 10))

        self.thread_input = ctk.CTkEntry(
            port_frame,
            placeholder_text="50",
            width=80,
            font=("Helvetica", 11),
        )
        self.thread_input.pack(side="left")
        self.thread_input.insert(0, "50")

        # Button Frame
        button_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=15)

        # Scan Button
        self.scan_button = ctk.CTkButton(
            button_frame,
            text="▶ Start Scan",
            command=self._start_scan,
            font=("Helvetica", 12, "bold"),
            fg_color="#00aa00",
            text_color="#ffffff",
            hover_color="#008800",
            height=40,
            corner_radius=8,
        )
        self.scan_button.pack(side="left", padx=5)

        # Stop Button
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Stop Scan",
            command=self._stop_scan,
            font=("Helvetica", 12, "bold"),
            fg_color="#aa0000",
            text_color="#ffffff",
            hover_color="#880000",
            height=40,
            corner_radius=8,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        # Clear Button
        clear_button = ctk.CTkButton(
            button_frame,
            text="🗑 Clear Results",
            command=self._clear_results,
            font=("Helvetica", 12, "bold"),
            fg_color="#444444",
            text_color="#ffffff",
            hover_color="#666666",
            height=40,
            corner_radius=8,
        )
        clear_button.pack(side="left", padx=5)

        # Export Button
        export_button = ctk.CTkButton(
            button_frame,
            text="💾 Export",
            command=self._export_results,
            font=("Helvetica", 12, "bold"),
            fg_color="#0066aa",
            text_color="#ffffff",
            hover_color="#004488",
            height=40,
            corner_radius=8,
        )
        export_button.pack(side="left", padx=5)

    def _create_results_frame(self):
        """Create the results display frame."""
        results_label = ctk.CTkLabel(
            self,
            text="Scan Results",
            font=("Helvetica", 14, "bold"),
            text_color="#00ff88",
        )
        results_label.grid(row=2, column=0, sticky="w", padx=20, pady=(10, 5))

        # Results text box with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            self,
            font=("Courier", 10),
            bg="#0d0d0d",
            fg="#00ff00",
            insertbackground="#00ff00",
            height=15,
            wrap="word",
            borderwidth=1,
            relief="flat",
        )
        self.results_text.grid(row=3, column=0, sticky="nsew", padx=15, pady=(0, 10))

        # Configure text tags for color coding
        self.results_text.tag_config("open", foreground="#00ff00")  # Green for open
        self.results_text.tag_config("closed", foreground="#888888")  # Gray for closed
        self.results_text.tag_config("error", foreground="#ff0000")  # Red for errors
        self.results_text.tag_config("info", foreground="#00aaff")  # Blue for info
        self.results_text.tag_config("warning", foreground="#ffaa00")  # Orange for warnings

        self.grid_rowconfigure(3, weight=1)

    def _create_status_bar(self):
        """Create the bottom status bar."""
        status_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", height=60)
        status_frame.grid(row=4, column=0, sticky="ew", padx=0, pady=0)
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_propagate(False)

        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=("Helvetica", 16),
            text_color="#666666",
        )
        self.status_indicator.grid(row=0, column=0, padx=15, pady=15)

        # Status text
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Idle",
            font=("Helvetica", 11),
            text_color="#ffffff",
        )
        self.status_label.grid(row=0, column=1, sticky="w", pady=15)

        # Timer
        self.timer_label = ctk.CTkLabel(
            status_frame,
            text="0:00",
            font=("Helvetica", 11),
            text_color="#00ff88",
        )
        self.timer_label.grid(row=0, column=2, sticky="e", padx=15, pady=15)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            status_frame, progress_color="#00aa00", height=4
        )
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=0)
        self.progress_bar.set(0)

    def _start_scan(self):
        """Start port scanning."""
        # Validate inputs
        target = self.target_input.get().strip()
        if not InputValidator.validate_ip(target):
            messagebox.showerror("Invalid Input", "Please enter a valid IP or hostname")
            return

        is_valid_start, start_port = InputValidator.validate_port(
            self.start_port_input.get()
        )
        is_valid_end, end_port = InputValidator.validate_port(self.end_port_input.get())

        if not is_valid_start or not is_valid_end:
            messagebox.showerror("Invalid Input", "Port numbers must be between 1 and 65535")
            return

        if start_port > end_port:
            messagebox.showerror("Invalid Input", "Start port cannot be greater than end port")
            return

        is_valid_threads, max_workers = InputValidator.validate_port(
            self.thread_input.get()
        )
        if not is_valid_threads or max_workers < 1 or max_workers > 500:
            max_workers = 50
            self.thread_input.delete(0, "end")
            self.thread_input.insert(0, "50")

        # Clear previous results
        self._clear_results()

        # Update UI state
        self.scanning = True
        self.scan_start_time = time.time()
        self.service_map = {}

        self.scan_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.target_input.configure(state="disabled")
        self.start_port_input.configure(state="disabled")
        self.end_port_input.configure(state="disabled")
        self.thread_input.configure(state="disabled")

        self._update_status("Scanning...", "#ffaa00", "●")

        # Run scan in separate thread
        scan_thread = threading.Thread(
            target=self._scan_worker,
            args=(target, start_port, end_port, max_workers),
            daemon=True,
        )
        scan_thread.start()

    def _scan_worker(self, target: str, start_port: int, end_port: int, max_workers: int):
        """Worker thread for scanning."""
        port_count = end_port - start_port + 1

        def scan_callback(port: int, is_open: bool, service: str, status: str):
            """Callback for scan progress."""
            if port == -1:  # Special messages
                if status == "INFO":
                    self._append_result(service, "info")
                elif status == "ERROR":
                    self._append_result(f"ERROR: {service}", "error")
            else:
                # Regular port result
                self.service_map[port] = service
                formatted = ResultFormatter.format_result(port, is_open, service, status)
                tag = "open" if is_open else "closed"
                self._append_result(formatted, tag)

                # Update progress
                scanned = len(self.scanner.results) + 1
                progress = min(scanned / port_count, 1.0)
                self.progress_bar.set(progress)

        # Perform scan
        self.scanner.scan_ports(
            target, start_port, end_port, scan_callback, max_workers
        )

        # Scan complete
        open_count = len([p for p, o in self.scanner.results if o])
        duration = time.time() - self.scan_start_time
        summary = f"\n✓ Scan Complete: {open_count} open ports found (Time: {TimeFormatter.format_duration(duration)})"
        self._append_result(summary, "info")

        self._scan_complete()

    def _stop_scan(self):
        """Stop the scanning operation."""
        self.scanner.stop_scan()
        self.scanning = False
        self._append_result("\n⚠ Scan stopped by user", "warning")
        self._scan_complete()

    def _scan_complete(self):
        """Handle scan completion."""
        self.scanning = False
        self.scan_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.target_input.configure(state="normal")
        self.start_port_input.configure(state="normal")
        self.end_port_input.configure(state="normal")
        self.thread_input.configure(state="normal")

        self._update_status("Idle", "#666666", "●")
        self.progress_bar.set(0)

    def _append_result(self, text: str, tag: str = "info"):
        """Append text to results display."""
        self.results_text.insert("end", text + "\n", tag)
        self.results_text.see("end")
        self.update()

    def _clear_results(self):
        """Clear the results display."""
        self.results_text.delete(1.0, "end")
        self.scanner.results = []
        self.service_map = {}
        self.progress_bar.set(0)

    def _export_results(self):
        """Export results to file."""
        if not self.scanner.results:
            messagebox.showwarning("No Results", "No scan results to export")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

        if filepath:
            target = self.target_input.get()
            if ResultFormatter.export_results(
                self.scanner.results, target, self.service_map, filepath
            ):
                messagebox.showinfo("Success", f"Results exported to {filepath}")
            else:
                messagebox.showerror("Export Failed", "Could not export results")

    def _update_status(self, status: str, color: str, indicator: str):
        """Update status bar."""
        self.status_label.configure(text=status, text_color="#ffffff")
        self.status_indicator.configure(text=indicator, text_color=color)

    def _update_timer(self):
        """Update the timer display."""
        if self.scanning and self.scan_start_time:
            elapsed = time.time() - self.scan_start_time
            self.timer_label.configure(text=TimeFormatter.format_duration(elapsed))

        self.after(100, self._update_timer)


def main():
    """Run the application."""
    app = PortScannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
