"""
Project:    Network Port Scanner
Difficulty: Intermediate
Skills:     Python, Sockets
Time:       Medium (a weekend)

What you will build:
    A command-line tool that scans a target host for open TCP ports.
    The scanner tries to connect to each port with a short timeout and
    reports which ports are open, closed, or filtered.

How to run:
    python port_scanner.py <host>
    python port_scanner.py scanme.example.com --ports 80,443 --timeout 1

Learning goals:
    - Working with sockets and connect attempts
    - Parsing command-line arguments
    - Handling network timeouts and exceptions
    - Running a scan with threads for speed

Roadmap:
    Step 1:  Run the project to see the current CLI skeleton
    Step 2:  Complete parse_ports() to convert user input into a list of ports
    Step 3:  Complete scan_port() to test a single TCP port
    Step 4:  Complete scan_host() to iterate over all requested ports
    Step 5:  Complete main() to tie parsing and scanning together
"""

import argparse
import socket

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Default list of well-known ports when the user does not specify any
DEFAULT_PORTS = [22, 80, 443, 3306, 5432, 8080]

# How long (in seconds) to wait for a connect attempt before giving up
DEFAULT_TIMEOUT = 1.0


# ---------------------------------------------------------------------------
# Helpers — complete each function below
# ---------------------------------------------------------------------------

def parse_ports(ports_arg):
    """
    Convert the user's --ports value into a list of integers.

    Accepts:
        "80"           -> [80]
        "80,443,8080"  -> [80, 443, 8080]
        "80-85"        -> [80, 81, 82, 83, 84, 85]

    Returns DEFAULT_PORTS if ports_arg is None.
    """
    pass


def scan_port(host, port, timeout=DEFAULT_TIMEOUT):
    """
    Attempt a TCP connection to (host, port).

    Returns "open" if the connection succeeds, "closed" if the host rejects
    it (ConnectionRefusedError), and "filtered" on any timeout or other
    error.
    """
    pass


def scan_host(host, ports, timeout=DEFAULT_TIMEOUT):
    """
    Scan every port in `ports` and print the result for each one.

    Expected output:
        Port 80: open
        Port 443: filtered
    """
    pass


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Scan a host for open TCP ports.")
    parser.add_argument("host", help="Hostname or IP address to scan")
    parser.add_argument("--ports", help="Comma-separated list or range of ports")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    ports = parse_ports(args.ports)
    print(f"Scanning {args.host} for {len(ports)} ports...")

    scan_host(args.host, ports, args.timeout)


if __name__ == "__main__":
    main()
