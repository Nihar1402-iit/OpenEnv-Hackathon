"""
Deterministic synthetic dataset for CRM environment.
"""

from typing import List, Dict, Any
from .models import Customer, Order, SupportTicket


def get_customers() -> List[Customer]:
    """Return hardcoded customer dataset."""
    return [
        Customer(customer_id="C001", name="Alice Johnson", email="alice@example.com", tier="Gold", phone="555-0001", created_at="2024-01-15"),
        Customer(customer_id="C002", name="Bob Smith", email="bob@example.com", tier="Silver", phone="555-0002", created_at="2024-01-20"),
        Customer(customer_id="C003", name="Carol White", email="carol@example.com", tier="Bronze", phone="555-0003", created_at="2024-02-01"),
        Customer(customer_id="C004", name="David Brown", email="david@example.com", tier="Gold", phone="555-0004", created_at="2024-02-05"),
        Customer(customer_id="C005", name="Eve Davis", email="eve@example.com", tier="Silver", phone="555-0005", created_at="2024-02-10"),
        Customer(customer_id="C006", name="Frank Miller", email="frank@example.com", tier="Gold", phone="555-0006", created_at="2024-02-15"),
        Customer(customer_id="C007", name="Grace Lee", email="grace@example.com", tier="Bronze", phone="555-0007", created_at="2024-02-20"),
        Customer(customer_id="C008", name="Henry Wilson", email="henry@example.com", tier="Silver", phone="555-0008", created_at="2024-03-01"),
        Customer(customer_id="C009", name="Ivy Martinez", email="ivy@example.com", tier="Gold", phone="555-0009", created_at="2024-03-05"),
        Customer(customer_id="C010", name="Jack Taylor", email="jack@example.com", tier="Bronze", phone="555-0010", created_at="2024-03-10"),
        Customer(customer_id="C011", name="Karen Anderson", email="karen@example.com", tier="Gold", phone="555-0011", created_at="2024-03-15"),
        Customer(customer_id="C012", name="Leo Thomas", email="leo@example.com", tier="Silver", phone="555-0012", created_at="2024-03-20"),
        Customer(customer_id="C013", name="Mona Jackson", email="mona@example.com", tier="Bronze", phone="555-0013", created_at="2024-03-25"),
        Customer(customer_id="C014", name="Nathan Harris", email="nathan@example.com", tier="Gold", phone="555-0014", created_at="2024-04-01"),
        Customer(customer_id="C015", name="Olivia Martin", email="olivia@example.com", tier="Silver", phone="555-0015", created_at="2024-04-05"),
        Customer(customer_id="C016", name="Paul Garcia", email="paul@example.com", tier="Gold", phone="555-0016", created_at="2024-04-10"),
        Customer(customer_id="C017", name="Quinn Rodriguez", email="quinn@example.com", tier="Bronze", phone="555-0017", created_at="2024-04-15"),
        Customer(customer_id="C018", name="Rachel Lewis", email="rachel@example.com", tier="Silver", phone="555-0018", created_at="2024-04-20"),
        Customer(customer_id="C019", name="Sam Walker", email="sam@example.com", tier="Gold", phone="555-0019", created_at="2024-04-25"),
        Customer(customer_id="C020", name="Tina Hall", email="tina@example.com", tier="Bronze", phone="555-0020", created_at="2024-05-01"),
    ]


def get_orders() -> List[Order]:
    """Return hardcoded order dataset."""
    return [
        Order(order_id="O001", customer_id="C001", product="Laptop", amount=1200.0, status="Completed", created_at="2024-01-16"),
        Order(order_id="O002", customer_id="C002", product="Mouse", amount=25.0, status="Completed", created_at="2024-01-21"),
        Order(order_id="O003", customer_id="C003", product="Keyboard", amount=80.0, status="Pending", created_at="2024-02-02"),
        Order(order_id="O004", customer_id="C001", product="Monitor", amount=350.0, status="Completed", created_at="2024-02-06"),
        Order(order_id="O005", customer_id="C004", product="Laptop", amount=1300.0, status="Completed", created_at="2024-02-07"),
        Order(order_id="O006", customer_id="C005", product="Keyboard", amount=85.0, status="Completed", created_at="2024-02-11"),
        Order(order_id="O007", customer_id="C006", product="Laptop", amount=1250.0, status="Completed", created_at="2024-02-16"),
        Order(order_id="O008", customer_id="C007", product="Mouse", amount=30.0, status="Cancelled", created_at="2024-02-21"),
        Order(order_id="O009", customer_id="C001", product="Keyboard", amount=90.0, status="Completed", created_at="2024-03-02"),
        Order(order_id="O010", customer_id="C008", product="Monitor", amount=300.0, status="Completed", created_at="2024-03-02"),
        Order(order_id="O011", customer_id="C009", product="Laptop", amount=1400.0, status="Completed", created_at="2024-03-06"),
        Order(order_id="O012", customer_id="C010", product="Mouse", amount=20.0, status="Pending", created_at="2024-03-11"),
        Order(order_id="O013", customer_id="C004", product="Monitor", amount=400.0, status="Completed", created_at="2024-03-16"),
        Order(order_id="O014", customer_id="C011", product="Keyboard", amount=95.0, status="Completed", created_at="2024-03-21"),
        Order(order_id="O015", customer_id="C012", product="Laptop", amount=1100.0, status="Completed", created_at="2024-03-26"),
        Order(order_id="O016", customer_id="C006", product="Monitor", amount=350.0, status="Completed", created_at="2024-04-02"),
        Order(order_id="O017", customer_id="C013", product="Mouse", amount=25.0, status="Completed", created_at="2024-04-06"),
        Order(order_id="O018", customer_id="C014", product="Laptop", amount=1150.0, status="Pending", created_at="2024-04-11"),
        Order(order_id="O019", customer_id="C009", product="Keyboard", amount=100.0, status="Completed", created_at="2024-04-16"),
        Order(order_id="O020", customer_id="C015", product="Monitor", amount=320.0, status="Completed", created_at="2024-04-21"),
        Order(order_id="O021", customer_id="C016", product="Laptop", amount=1200.0, status="Completed", created_at="2024-04-26"),
        Order(order_id="O022", customer_id="C017", product="Mouse", amount=22.0, status="Completed", created_at="2024-05-02"),
        Order(order_id="O023", customer_id="C001", product="Monitor", amount=280.0, status="Completed", created_at="2024-05-03"),
        Order(order_id="O024", customer_id="C018", product="Keyboard", amount=88.0, status="Pending", created_at="2024-05-07"),
        Order(order_id="O025", customer_id="C019", product="Laptop", amount=1350.0, status="Completed", created_at="2024-05-12"),
        Order(order_id="O026", customer_id="C011", product="Monitor", amount=400.0, status="Completed", created_at="2024-05-13"),
        Order(order_id="O027", customer_id="C004", product="Keyboard", amount=92.0, status="Completed", created_at="2024-05-18"),
        Order(order_id="O028", customer_id="C020", product="Mouse", amount=28.0, status="Completed", created_at="2024-05-22"),
        Order(order_id="O029", customer_id="C006", product="Laptop", amount=1200.0, status="Completed", created_at="2024-05-27"),
        Order(order_id="O030", customer_id="C009", product="Monitor", amount=350.0, status="Completed", created_at="2024-06-01"),
    ]


def get_support_tickets() -> List[SupportTicket]:
    """Return hardcoded support ticket dataset."""
    return [
        SupportTicket(ticket_id="T001", customer_id="C001", subject="Laptop overheating", priority="High", status="Open", created_at="2024-03-01"),
        SupportTicket(ticket_id="T002", customer_id="C002", subject="Mouse not working", priority="Low", status="Closed", created_at="2024-02-15"),
        SupportTicket(ticket_id="T003", customer_id="C003", subject="Keyboard keys stuck", priority="Medium", status="Open", created_at="2024-03-10"),
        SupportTicket(ticket_id="T004", customer_id="C004", subject="Monitor flickering", priority="High", status="Open", created_at="2024-03-15"),
        SupportTicket(ticket_id="T005", customer_id="C005", subject="Delivery delay", priority="Medium", status="Closed", created_at="2024-02-20"),
        SupportTicket(ticket_id="T006", customer_id="C006", subject="Laptop noise issue", priority="High", status="Open", created_at="2024-03-20"),
        SupportTicket(ticket_id="T007", customer_id="C007", subject="Refund request", priority="Medium", status="Closed", created_at="2024-03-01"),
        SupportTicket(ticket_id="T008", customer_id="C008", subject="Mouse sensitivity", priority="Low", status="Closed", created_at="2024-03-05"),
        SupportTicket(ticket_id="T009", customer_id="C009", subject="Keyboard lag", priority="High", status="Open", created_at="2024-03-22"),
        SupportTicket(ticket_id="T010", customer_id="C010", subject="Monitor dead pixels", priority="Medium", status="Open", created_at="2024-03-25"),
        SupportTicket(ticket_id="T011", customer_id="C011", subject="Account issue", priority="High", status="Open", created_at="2024-03-28"),
        SupportTicket(ticket_id="T012", customer_id="C012", subject="Product compatibility", priority="Low", status="Closed", created_at="2024-03-10"),
        SupportTicket(ticket_id="T013", customer_id="C013", subject="Shipping problem", priority="Medium", status="Closed", created_at="2024-03-18"),
        SupportTicket(ticket_id="T014", customer_id="C014", subject="Laptop screen crack", priority="High", status="Open", created_at="2024-04-01"),
        SupportTicket(ticket_id="T015", customer_id="C015", subject="Battery drain", priority="Low", status="Closed", created_at="2024-03-20"),
        SupportTicket(ticket_id="T016", customer_id="C016", subject="Monitor color issue", priority="High", status="Open", created_at="2024-04-05"),
        SupportTicket(ticket_id="T017", customer_id="C017", subject="Peripheral not detected", priority="Medium", status="Open", created_at="2024-04-08"),
        SupportTicket(ticket_id="T018", customer_id="C018", subject="Warranty claim", priority="Low", status="Closed", created_at="2024-03-28"),
        SupportTicket(ticket_id="T019", customer_id="C019", subject="Performance issue", priority="High", status="Open", created_at="2024-04-10"),
        SupportTicket(ticket_id="T020", customer_id="C020", subject="Setup assistance", priority="Medium", status="Closed", created_at="2024-04-02"),
        SupportTicket(ticket_id="T021", customer_id="C001", subject="Software issue", priority="Medium", status="Closed", created_at="2024-04-12"),
        SupportTicket(ticket_id="T022", customer_id="C004", subject="Connectivity problem", priority="High", status="Open", created_at="2024-04-15"),
        SupportTicket(ticket_id="T023", customer_id="C006", subject="Port issue", priority="High", status="Open", created_at="2024-04-18"),
        SupportTicket(ticket_id="T024", customer_id="C009", subject="Update problem", priority="Medium", status="Closed", created_at="2024-04-20"),
        SupportTicket(ticket_id="T025", customer_id="C011", subject="Security concern", priority="High", status="Open", created_at="2024-04-22"),
        SupportTicket(ticket_id="T026", customer_id="C014", subject="Data loss", priority="High", status="Open", created_at="2024-04-25"),
        SupportTicket(ticket_id="T027", customer_id="C016", subject="Display issue", priority="Medium", status="Closed", created_at="2024-04-28"),
        SupportTicket(ticket_id="T028", customer_id="C019", subject="Power issue", priority="High", status="Open", created_at="2024-05-01"),
        SupportTicket(ticket_id="T029", customer_id="C004", subject="Interface problem", priority="Medium", status="Open", created_at="2024-05-03"),
        SupportTicket(ticket_id="T030", customer_id="C001", subject="Speed issue", priority="Low", status="Closed", created_at="2024-05-05"),
    ]


def create_database() -> Dict[str, Any]:
    """Create in-memory database with all data."""
    return {
        "customers": get_customers(),
        "orders": get_orders(),
        "support_tickets": get_support_tickets(),
    }
