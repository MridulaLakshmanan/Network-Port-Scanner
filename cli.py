"""Command-line fallback runner for the Network Port Scanner.

This is used when the GUI cannot be started (for example on older macOS
where the GUI toolkit aborts). It performs a small scan and prints results
to stdout.
"""
import argparse
import time
from scanner import PortScanner


def main():
    parser = argparse.ArgumentParser(description="Simple CLI port scanner fallback")
    parser.add_argument("target", nargs="?", default="127.0.0.1", help="Target host (default: 127.0.0.1)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end", type=int, default=1024, help="End port (default: 1024)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of threads (default: 50)")
    args = parser.parse_args()

    scanner = PortScanner()

    print(f"Scanning {args.target} ports {args.start}-{args.end} with {args.threads} threads...")
    start_time = time.time()

    def cb(port, is_open, service, status):
        # simple realtime output
        if port == -1:
            print(status + ":", service)
        else:
            if is_open:
                print(f"{port}/tcp OPEN    ({service})")

    results = scanner.scan_ports(args.target, args.start, args.end, cb, max_workers=args.threads)

    elapsed = time.time() - start_time
    open_ports = [p for p, o in results if o]

    print("\nScan complete — open ports:")
    if open_ports:
        for p in open_ports:
            print(f" - {p} ({scanner.get_service_name(p)})")
    else:
        print(" (none found)")

    print(f"Time: {elapsed:.2f}s | Scanned: {len(results)} ports")


if __name__ == "__main__":
    main()
