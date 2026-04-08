"""
Utility Module
Provides helper functions for validation, formatting, and file operations.
"""

import re
from typing import List, Tuple
from datetime import datetime


class ResultFormatter:
    """Formats and exports scan results."""

    @staticmethod
    def format_result(
        port: int, is_open: bool, service: str = "UNKNOWN", status: str = "CLOSED"
    ) -> str:
        """
        Format a single scan result.

        Args:
            port: Port number
            is_open: Whether port is open
            service: Service name running on port
            status: Port status (OPEN/CLOSED)

        Returns:
            Formatted result string
        """
        symbol = "[+]" if is_open else "[-]"
        return f"{symbol} Port {port:5d} {status:6s} ({service})"

    @staticmethod
    def export_results(
        results: List[Tuple[int, bool]],
        target: str,
        service_map: dict,
        filepath: str,
    ) -> bool:
        """
        Export scan results to a text file.

        Args:
            results: List of (port, is_open) tuples
            target: Target host that was scanned
            service_map: Dictionary mapping ports to service names
            filepath: Path to save results

        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(filepath, "w") as f:
                f.write("=" * 60 + "\n")
                f.write("NETWORK PORT SCANNER RESULTS\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Target: {target}\n")
                f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Ports Scanned: {len(results)}\n\n")

                # Separate open and closed ports
                open_ports = [port for port, is_open in results if is_open]
                closed_ports = [port for port, is_open in results if not is_open]

                f.write(f"Open Ports: {len(open_ports)}\n")
                if open_ports:
                    for port in sorted(open_ports):
                        service = service_map.get(port, "UNKNOWN")
                        f.write(f"  [+] Port {port:5d} OPEN ({service})\n")
                else:
                    f.write("  None\n")

                f.write(f"\nClosed Ports: {len(closed_ports)}\n")
                if closed_ports:
                    for port in sorted(closed_ports)[:20]:  # Show first 20
                        f.write(f"  [-] Port {port:5d} CLOSED\n")
                    if len(closed_ports) > 20:
                        f.write(f"  ... and {len(closed_ports) - 20} more\n")
                else:
                    f.write("  None\n")

                f.write("\n" + "=" * 60 + "\n")
                f.write("Educational use only. Authorized scanning only.\n")
                f.write("=" * 60 + "\n")

            return True
        except Exception as e:
            print(f"Error exporting results: {e}")
            return False


class InputValidator:
    """Validates user inputs."""

    @staticmethod
    def validate_port(port_str: str) -> Tuple[bool, int]:
        """
        Validate and parse a port number.

        Args:
            port_str: Port as string

        Returns:
            Tuple of (is_valid, port_number)
        """
        try:
            port = int(port_str.strip())
            if 1 <= port <= 65535:
                return True, port
            return False, 0
        except ValueError:
            return False, 0

    @staticmethod
    def validate_ip(ip: str) -> bool:
        """
        Validate IP address format (basic check).

        Args:
            ip: IP address or hostname

        Returns:
            True if valid format, False otherwise
        """
        ip = ip.strip()
        if not ip:
            return False

        # Check if it's a hostname (domain)
        if not all(c.isdigit() or c == "." for c in ip):
            # It's a hostname, check format
            hostname_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
            return bool(re.match(hostname_pattern, ip))

        # It's an IP address, validate
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False


class TimeFormatter:
    """Formats time durations."""

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string
        """
        if seconds < 1:
            return f"{seconds:.2f}s"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"


class PortInfo:
    """Provides information about common ports."""

    COMMON_PORTS = {
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

    @classmethod
    def get_service(cls, port: int) -> str:
        """
        Get service name for a port.

        Args:
            port: Port number

        Returns:
            Service name or 'UNKNOWN'
        """
        return cls.COMMON_PORTS.get(port, "UNKNOWN")

    @classmethod
    def is_common_port(cls, port: int) -> bool:
        """
        Check if port is a commonly used port.

        Args:
            port: Port number

        Returns:
            True if port is in common ports list
        """
        return port in cls.COMMON_PORTS
