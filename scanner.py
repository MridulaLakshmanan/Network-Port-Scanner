"""
Network Port Scanner Module
Handles port scanning logic with multithreading support.
"""

import socket
import threading
from typing import Callable, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class PortScanner:
    """
    Performs port scanning on target hosts.
    Supports multithreaded scanning with callbacks for real-time updates.
    """

    def __init__(self, timeout: float = 1.5):
        """
        Initialize the port scanner.

        Args:
            timeout: Socket timeout in seconds (default: 1.5)
        """
        self.timeout = timeout
        self.is_scanning = False
        self.results = []

    def resolve_host(self, host: str) -> Optional[str]:
        """
        Resolve a domain name to an IP address.

        Args:
            host: Domain name or IP address

        Returns:
            IP address string or None if resolution fails
        """
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            return None

    def is_port_open(self, host: str, port: int) -> bool:
        """
        Check if a single port is open on the target host.

        Args:
            host: Target IP address
            port: Port number to check

        Returns:
            True if port is open, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def get_service_name(self, port: int) -> str:
        """
        Get the service name for a given port.

        Args:
            port: Port number

        Returns:
            Service name or 'UNKNOWN'
        """
        common_services = {
            21: "FTP",
            22: "SSH",
            23: "TELNET",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            465: "SMTP-SSL",
            587: "SMTP",
            993: "IMAP-SSL",
            995: "POP3-SSL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-ALT",
            8443: "HTTPS-ALT",
            27017: "MongoDB",
            6379: "Redis",
        }
        return common_services.get(port, "UNKNOWN")

    def scan_port(
        self, host: str, port: int, callback: Optional[Callable] = None
    ) -> Tuple[int, bool]:
        """
        Scan a single port and invoke callback with result.

        Args:
            host: Target IP address
            port: Port number to scan
            callback: Function to call with (port, is_open) when scan completes

        Returns:
            Tuple of (port, is_open)
        """
        if not self.is_scanning:
            return (port, False)

        is_open = self.is_port_open(host, port)

        if callback:
            service = self.get_service_name(port)
            status = "OPEN" if is_open else "CLOSED"
            callback(port, is_open, service, status)

        return (port, is_open)

    def scan_ports(
        self,
        host: str,
        start_port: int,
        end_port: int,
        callback: Optional[Callable] = None,
        max_workers: int = 50,
    ) -> List[Tuple[int, bool]]:
        """
        Scan a range of ports on the target host using multithreading.

        Args:
            host: Target IP address or hostname
            start_port: Starting port number
            end_port: Ending port number (inclusive)
            callback: Function to call for each scan result
            max_workers: Maximum number of threads to use

        Returns:
            List of tuples (port, is_open)
        """
        self.is_scanning = True
        self.results = []

        # Resolve hostname if necessary
        ip_address = host
        if not self._is_ip_address(host):
            ip_address = self.resolve_host(host)
            if ip_address is None:
                if callback:
                    callback(-1, False, "ERROR", f"Could not resolve {host}")
                self.is_scanning = False
                return []

        if callback:
            callback(-1, False, "INFO", f"Scanning {ip_address}...")

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.scan_port, ip_address, port, callback): port
                    for port in range(start_port, end_port + 1)
                }

                for future in as_completed(futures):
                    if not self.is_scanning:
                        break
                    try:
                        result = future.result()
                        self.results.append(result)
                    except Exception as e:
                        if callback:
                            callback(-1, False, "ERROR", f"Scan error: {str(e)}")

        except Exception as e:
            if callback:
                callback(-1, False, "ERROR", f"Scan failed: {str(e)}")

        self.is_scanning = False
        return self.results

    def stop_scan(self):
        """Stop the current scanning operation."""
        self.is_scanning = False

    @staticmethod
    def _is_ip_address(host: str) -> bool:
        """
        Check if the given string is a valid IP address.

        Args:
            host: String to check

        Returns:
            True if valid IP address, False otherwise
        """
        try:
            socket.inet_aton(host)
            return True
        except socket.error:
            return False

    @staticmethod
    def validate_port_range(start_port: int, end_port: int) -> Tuple[bool, str]:
        """
        Validate port range.

        Args:
            start_port: Starting port number
            end_port: Ending port number

        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_port < 1 or start_port > 65535:
            return False, "Start port must be between 1 and 65535"
        if end_port < 1 or end_port > 65535:
            return False, "End port must be between 1 and 65535"
        if start_port > end_port:
            return False, "Start port must be less than or equal to end port"
        return True, ""

    @staticmethod
    def validate_target(target: str) -> Tuple[bool, str]:
        """
        Validate target IP or hostname.

        Args:
            target: IP address or hostname

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not target or len(target.strip()) == 0:
            return False, "Target cannot be empty"
        if len(target) > 255:
            return False, "Target is too long"
        return True, ""
