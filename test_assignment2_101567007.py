"""
Unit Tests for Assignment 2 — Port Scanner
"""

import unittest

from assignment2_101567007 import PortScanner, common_ports

# TODO: Import your classes and common_ports from assignment2_studentID
# from assignment2_studentID import PortScanner, common_ports


class TestPortScanner(unittest.TestCase):

    def test_scanner_initialization(self):
        """Test that PortScanner initializes with correct target and empty results list."""
        portscanner = PortScanner("127.0.0.1")
        self.assertEqual(portscanner.target, "127.0.0.1")
        self.assertEqual(portscanner.scan_results, [])

    def test_get_open_ports_filters_correctly(self):
        """Test that get_open_ports returns only Open ports."""
        portscanner = PortScanner("127.0.0.1")
        portscanner.scan_results = [
            (22, "Open", "SSH"),
            (23, "Closed", "Telnet"),
            (80, "Open", "HTTP"),
        ]
        open_ports = portscanner.get_open_ports()
        self.assertEqual(len(open_ports), 2)

    def test_common_ports_dict(self):
        """Test that common_ports dictionary has correct entries."""
        self.assertEqual(common_ports[80], "HTTP")
        self.assertEqual(common_ports[22], "SSH")

    def test_invalid_target(self):
        """Test that setter rejects empty string target."""
        portscanner = PortScanner("127.0.0.1")
        with self.assertRaises(ValueError):
            portscanner.target = ""
        self.assertEqual(portscanner.target, "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
