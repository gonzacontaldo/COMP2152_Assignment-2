"""
Author: Gonzalo Contaldo
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

import socket
import threading
import sqlite3
import os
import platform
import datetime


print("Python version:", platform.python_version())
print("Operating System:", platform.system(), platform.release())

# Define common ports and their services
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt",
}


class NetworkTool:
    def __init__(self, target):
        self.__target = target

    # Q3: What is the benefit of using @property and @target.setter?
    """ 
    @property lets you access a method like an attribute, and @setter lets you control how that attribute is updated.
    Benefit: encapsulation + validation, you can add logic (like checks or calculations) without changing how the attribute is used.
    """

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if value == "":
            raise ValueError("Target cannot be an empty string.")
        self.__target = value

    def __del__(self):
        print("NetworkTool instance destroyed")


# Q1: How does PortScanner reuse code from NetworkTool?
"""
PortScanner inherits from NetworkTool, so it automatically gets its methods and attributes.
It reuses code by:
- Calling shared methods from NetworkTool (like connection setup, logging, etc.)
- Avoiding rewriting common network logic
"""


class PortScanner(NetworkTool):
    # - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    # - Destructor: print "PortScanner instance destroyed", call super().__del__()
    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()

    def scan_port(self, port):
        #     Q4: What would happen without try-except here?
        """
        Without try-except, any socket error would crash the program and stop the scan.
        With it, errors are handled and the scan continues.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"
            service_name = common_ports.get(port, "Unknown")

            with self.lock:
                self.scan_results.append((port, status, service_name))

        except socket.error as e:
            print(f"Error scanning port {port}: {e}")
        finally:
            sock.close()

    def get_open_ports(self):
        return [port for port, status, service in self.scan_results if status == "Open"]

    # Q2: Why do we use threading instead of scanning one port at a time?
    """ 
    Threading allows us to scan multiple ports simultaneously,
    which significantly reduces the total scan time compared to scanning one port at a time 
    (which would be sequential and much slower, especially if many ports are open or filtered).
    """

    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def save_results(target, results):
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                port INTEGER,
                status TEXT,
                service TEXT,
                scan_date TEXT
            )
        """
        )

        for port, status, service in results:
            cursor.execute(
                """
                INSERT INTO scans (target, port, status, service, scan_date)
                VALUES (?, ?, ?, ?, ?)
            """,
                (target, port, status, service, str(datetime.datetime.now())),
            )

        conn.commit()
        conn.close()

    def load_past_scans():
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
        rows = cursor.fetchall()

        if rows:
            for target, port, status, service, scan_date in rows:
                print(f"[{scan_date}] {target} : Port {port} ({service}) - {status}")
        else:
            print("No past scans found.")

        conn.close()


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    try:
        target = (
            input("Enter target IP address (default '127.0.0.1' if empty): ")
            or "127.0.0.1"
        )
        start = int(input("Enter start port (1-1024): "))
        end = int(input("Enter end port (1-1024, >= start port): "))

        if start < 1 or start > 1024 or end < 1 or end > 1024 or start > end:
            raise ValueError("Port must be between 1 and 1024.")

    except ValueError as e:
        print(f"Invalid input. Please enter a valid integer. {e}")
        exit(1)

    scanner = PortScanner(target)
    print(f"Scanning {target} from port {start} to {end}...")
    scanner.scan_range(start, end)
    open_ports = scanner.get_open_ports()
    print(f"Open ports on {target}: {open_ports}")
    print(f"Total open ports found: {len(open_ports)}")
    PortScanner.save_results(target, scanner.scan_results)

    # Ask user if they want to see past scan history
    view_history = (
        input("Would you like to see past scan history? (yes/no): ").strip().lower()
    )
    if view_history == "yes":
        PortScanner.load_past_scans()

# Q5: New Feature Proposal
"""
Add a feature that groups open ports by service (e.g., HTTP, SSH).
A list comprehension can extract services from open ports and count them.
This helps users quickly understand what services are running.
"""

# Diagram: See diagram_studentID.png in the repository root
