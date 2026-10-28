"""Menu-driven community repair and reuse management prototype."""

from typing import Dict, Optional, Tuple


class Technician:
    def __init__(self, technician_id: str, name: str) -> None:
        self.technician_id = technician_id.strip().upper()
        self.name = name.strip()
        if not self.technician_id:
            raise ValueError("Technician ID cannot be blank.")
        if not self.name:
            raise ValueError("Technician name cannot be blank.")

    def display_details(self) -> str:
        return "Technician ID: {} | Name: {}".format(self.technician_id, self.name)


class RepairRequest:
    STATUSES: Tuple[str, ...] = (
        "New",
        "In Progress",
        "Awaiting Parts",
        "Completed",
        "Reuse Assessment",
    )
    _next_request_number = 1

    @classmethod
    def generate_request_id(cls) -> str:
        request_id = "R{:04d}".format(cls._next_request_number)
        cls._next_request_number += 1
        return request_id

    def __init__(self, item_type: str, fault_description: str) -> None:
        item_type = item_type.strip()
        fault_description = fault_description.strip()
        if not item_type:
            raise ValueError("Item type cannot be blank.")
        if not fault_description:
            raise ValueError("Fault description cannot be blank.")
        self.request_id = self.generate_request_id()
        self.item_type = item_type
        self.fault_description = fault_description
        self.status = "New"
        self.assigned_technician: Optional[Technician] = None
        self.outcome: Optional[str] = None

    def update_status(self, status: str) -> None:
        normalized_status = status.strip().casefold()
        for valid_status in self.STATUSES:
            if normalized_status == valid_status.casefold():
                self.status = valid_status
                return
        raise ValueError(
            "Invalid status. Choose one of: {}.".format(", ".join(self.STATUSES))
        )

    def assign_technician(self, technician: Technician) -> None:
        self.assigned_technician = technician

    def record_outcome(self, outcome: str) -> None:
        outcome = outcome.strip()
        if not outcome:
            raise ValueError("Outcome cannot be blank.")
        self.outcome = outcome

    def display_details(self) -> str:
        technician = (
            self.assigned_technician.display_details()
            if self.assigned_technician
            else "Not assigned"
        )
        outcome = self.outcome if self.outcome else "Not recorded"
        return (
            "Request ID: {}\n"
            "Item type: {}\n"
            "Reported fault: {}\n"
            "Status: {}\n"
            "Technician: {}\n"
            "Outcome: {}"
        ).format(
            self.request_id,
            self.item_type,
            self.fault_description,
            self.status,
            technician,
            outcome,
        )


class RepairCentre:
    def __init__(self) -> None:
        self.requests: Dict[str, RepairRequest] = {}
        self.technicians: Dict[str, Technician] = {}

    def register_request(
        self, item_type: str, fault_description: str
    ) -> RepairRequest:
        request = RepairRequest(item_type, fault_description)
        self.requests[request.request_id] = request
        return request

    def register_technician(self, technician_id: str, name: str) -> Technician:
        normalized_id = technician_id.strip().upper()
        if normalized_id in self.technicians:
            raise ValueError("That technician ID is already registered.")
        technician = Technician(normalized_id, name.strip())
        self.technicians[normalized_id] = technician
        return technician

    def find_request(self, request_id: str) -> Optional[RepairRequest]:
        return self.requests.get(request_id.strip().upper())

    def find_technician(self, technician_id: str) -> Optional[Technician]:
        return self.technicians.get(technician_id.strip().upper())

    def list_requests(self) -> Tuple[RepairRequest, ...]:
        return tuple(self.requests.values())

    def list_technicians(self) -> Tuple[Technician, ...]:
        return tuple(self.technicians.values())

    def assign_technician(self, request_id: str, technician_id: str) -> None:
        request = self.find_request(request_id)
        if request is None:
            raise ValueError("Request not found.")
        technician = self.find_technician(technician_id)
        if technician is None:
            raise ValueError("Technician not found. Register the technician first.")
        request.assign_technician(technician)

    def update_status(self, request_id: str, status: str) -> None:
        request = self.find_request(request_id)
        if request is None:
            raise ValueError("Request not found.")
        request.update_status(status)

    def record_outcome(self, request_id: str, outcome: str) -> None:
        request = self.find_request(request_id)
        if request is None:
            raise ValueError("Request not found.")
        request.record_outcome(outcome)


def prompt_required(label: str) -> str:
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Input cannot be blank. Please try again.")


def prompt_request(centre: RepairCentre) -> Optional[RepairRequest]:
    request_id = prompt_required("Enter request ID: ")
    request = centre.find_request(request_id)
    if request is None:
        print("Request not found.")
    return request


def register_request(centre: RepairCentre) -> None:
    item_type = prompt_required("Item type: ")
    fault_description = prompt_required("Reported fault: ")
    request = centre.register_request(item_type, fault_description)
    print("Request registered with ID {}.".format(request.request_id))


def register_technician(centre: RepairCentre) -> None:
    technician_id = prompt_required("Technician ID: ")
    name = prompt_required("Technician name: ")
    technician = centre.register_technician(technician_id, name)
    print("Registered {}.".format(technician.display_details()))


def view_requests(centre: RepairCentre) -> None:
    requests = centre.list_requests()
    if not requests:
        print("There are no repair requests.")
        return
    for request in requests:
        print("\n" + request.display_details())


def search_request(centre: RepairCentre) -> None:
    request = prompt_request(centre)
    if request is not None:
        print(request.display_details())


def assign_technician(centre: RepairCentre) -> None:
    request_id = prompt_required("Request ID: ")
    technician_id = prompt_required("Technician ID: ")
    centre.assign_technician(request_id, technician_id)
    print("Technician assigned to request {}.".format(request_id.upper()))


def update_status(centre: RepairCentre) -> None:
    print("Available statuses: {}".format(", ".join(RepairRequest.STATUSES)))
    request_id = prompt_required("Request ID: ")
    status = prompt_required("New status: ")
    centre.update_status(request_id, status)
    print("Status updated.")


def record_outcome(centre: RepairCentre) -> None:
    request_id = prompt_required("Request ID: ")
    outcome = prompt_required("Repair outcome or further action: ")
    centre.record_outcome(request_id, outcome)
    print("Outcome recorded.")


def view_technicians(centre: RepairCentre) -> None:
    technicians = centre.list_technicians()
    if not technicians:
        print("There are no registered technicians.")
        return
    for technician in technicians:
        print(technician.display_details())


def display_menu() -> None:
    print(
        "\nCommunity Repair and Reuse Management System\n"
        "1. Register repair request\n"
        "2. View all requests\n"
        "3. Search request\n"
        "4. Register technician\n"
        "5. View technicians\n"
        "6. Assign technician\n"
        "7. Update request status\n"
        "8. Record repair outcome\n"
        "0. Exit"
    )


def main() -> None:
    centre = RepairCentre()
    actions = {
        "1": register_request,
        "2": view_requests,
        "3": search_request,
        "4": register_technician,
        "5": view_technicians,
        "6": assign_technician,
        "7": update_status,
        "8": record_outcome,
    }

    while True:
        display_menu()
        try:
            choice = input("Select an option: ").strip()
            if choice == "0":
                print("Goodbye.")
                break
            action = actions.get(choice)
            if action is None:
                print("Invalid menu option. Please choose a listed option.")
                continue
            action(centre)
        except ValueError as error:
            print("Error: {}".format(error))
        except EOFError:
            print("\nInput closed. Exiting.")
            break
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break


if __name__ == "__main__":
    main()