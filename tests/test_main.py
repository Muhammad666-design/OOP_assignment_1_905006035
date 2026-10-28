import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from main import RepairCentre, RepairRequest, main


class RepairCentreTests(unittest.TestCase):
    def setUp(self):
        self.centre = RepairCentre()

    def test_registers_and_finds_multiple_requests(self):
        first = self.centre.register_request(" Laptop ", "Will not start")
        second = self.centre.register_request("Fan", "Makes a loud noise")

        self.assertNotEqual(first.request_id, second.request_id)
        self.assertIs(self.centre.find_request(first.request_id), first)
        self.assertEqual(len(self.centre.list_requests()), 2)
        self.assertEqual(first.item_type, "Laptop")

    def test_rejects_blank_request_information(self):
        with self.assertRaisesRegex(ValueError, "Item type cannot be blank"):
            self.centre.register_request(" ", "Fault")
        with self.assertRaisesRegex(ValueError, "Fault description cannot be blank"):
            self.centre.register_request("Laptop", " ")

    def test_registers_and_assigns_technician(self):
        request = self.centre.register_request("Radio", "No sound")
        technician = self.centre.register_technician(" t01 ", " Alex ")

        self.centre.assign_technician(request.request_id.lower(), "t01")

        self.assertEqual(technician.technician_id, "T01")
        self.assertIs(request.assigned_technician, technician)
        self.assertIs(self.centre.find_technician("T01"), technician)

    def test_rejects_duplicate_technician_id(self):
        self.centre.register_technician("T01", "Alex")

        with self.assertRaisesRegex(ValueError, "already registered"):
            self.centre.register_technician("t01", "Sam")

    def test_reports_unknown_requests_and_technicians(self):
        with self.assertRaisesRegex(ValueError, "Request not found"):
            self.centre.update_status("R9999", "Completed")
        request = self.centre.register_request("Radio", "No sound")
        with self.assertRaisesRegex(ValueError, "Technician not found"):
            self.centre.assign_technician(request.request_id, "T99")

    def test_status_is_canonicalized_and_invalid_status_is_rejected(self):
        request = self.centre.register_request("Phone", "Cracked screen")

        self.centre.update_status(request.request_id, " in progress ")
        self.assertEqual(request.status, "In Progress")

        with self.assertRaisesRegex(ValueError, "Invalid status"):
            self.centre.update_status(request.request_id, "Unknown")
        self.assertEqual(request.status, "In Progress")

    def test_records_nonblank_outcome(self):
        request = self.centre.register_request("Radio", "No sound")

        self.centre.record_outcome(request.request_id, " Repaired and tested ")

        self.assertEqual(request.outcome, "Repaired and tested")
        with self.assertRaisesRegex(ValueError, "Outcome cannot be blank"):
            self.centre.record_outcome(request.request_id, " ")


class MenuWorkflowTests(unittest.TestCase):
    def test_menu_runs_operations_and_exits_cleanly(self):
        user_input = [
            "1",
            "Laptop",
            "No power",
            "4",
            "T01",
            "Alex",
            "6",
            "R0001",
            "T01",
            "7",
            "R0001",
            "in progress",
            "8",
            "R0001",
            "Repaired",
            "2",
            "0",
        ]
        output = StringIO()

        with patch("builtins.input", side_effect=user_input):
            with patch.object(RepairRequest, "_next_request_number", 1):
                with redirect_stdout(output):
                    main()

        result = output.getvalue()
        self.assertIn("Request registered with ID R0001.", result)
        self.assertIn("Technician assigned to request R0001.", result)
        self.assertIn("Status: In Progress", result)
        self.assertIn("Outcome: Repaired", result)
        self.assertIn("Goodbye.", result)

    def test_menu_recovers_from_invalid_and_missing_input(self):
        user_input = [
            "not-a-menu-option",
            "1",
            " ",
            "Laptop",
            " ",
            "No power",
            "7",
            "R9999",
            "Completed",
            "7",
            "R0001",
            "not-a-status",
            "7",
            "R0001",
            "Completed",
            "3",
            "R9999",
            "0",
        ]
        output = StringIO()

        with patch("builtins.input", side_effect=user_input):
            with patch.object(RepairRequest, "_next_request_number", 1):
                with redirect_stdout(output):
                    main()

        result = output.getvalue()
        self.assertIn("Invalid menu option", result)
        self.assertEqual(result.count("Input cannot be blank"), 2)
        self.assertIn("Error: Request not found.", result)
        self.assertIn("Error: Invalid status.", result)
        self.assertIn("Request not found.", result)
        self.assertIn("Status updated.", result)
        self.assertIn("Goodbye.", result)


if __name__ == "__main__":
    unittest.main()
