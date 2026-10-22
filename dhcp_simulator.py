
import ipaddress
import time
from datetime import datetime

# DHCP pool configuration for two subnets
POOLS = {
    "Subnet A": {
        "network": ipaddress.ip_network("192.168.1.0/24"),
        "gateway": "192.168.1.1",
        "start": "192.168.1.10",
        "end": "192.168.1.12",
    },
    "Subnet B": {
        "network": ipaddress.ip_network("192.168.2.0/24"),
        "gateway": "192.168.2.1",
        "start": "192.168.2.10",
        "end": "192.168.2.12",
    },
}

leases = {}
history = []


def get_available_ips(subnet):
    pool = POOLS[subnet]
    start = ipaddress.ip_address(pool["start"])
    end = ipaddress.ip_address(pool["end"])

    return [
        str(ip)
        for ip in range(int(start), int(end) + 1)
        if str(ip) not in leases
    ]


def show_dora(client, subnet, ip):
    messages = [
        ("DISCOVER", "Client broadcasts a request for a DHCP server."),
        ("OFFER", f"Server offers IP address {ip}."),
        ("REQUEST", f"Client requests IP address {ip}."),
        ("ACKNOWLEDGE", "Server confirms the lease and network settings."),
    ]

    print("\n--- DHCP DORA PROCESS ---")
    for message, description in messages:
        print(f"{message:12} | {client}: {description}")
        time.sleep(0.25)


def request_ip():
    client = input("Enter client name (e.g., PC4): ").strip()
    if not client:
        print("Client name cannot be empty.")
        return

    if client in leases:
        print(f"{client} already has IP {leases[client]['ip']}.")
        return

    print("\nChoose subnet:")
    print("1. Subnet A (192.168.1.0/24)")
    print("2. Subnet B (192.168.2.0/24)")
    choice = input("Enter 1 or 2: ").strip()

    if choice not in ("1", "2"):
        print("Invalid subnet choice.")
        return

    subnet = "Subnet A" if choice == "1" else "Subnet B"
    available = get_available_ips(subnet)

    if not available:
        print(f"\nPOOL EXHAUSTED: No IP addresses remain in {subnet}.")
        history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "client": client,
            "subnet": subnet,
            "event": "FAILED - pool exhausted",
        })
        return

    offered_ip = available[0]
    show_dora(client, subnet, offered_ip)

    leases[client] = {
        "ip": offered_ip,
        "subnet": subnet,
        "gateway": POOLS[subnet]["gateway"],
        "mask": "255.255.255.0",
        "lease_time": "Simulated lease (no expiry timer)",
    }

    history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "client": client,
        "subnet": subnet,
        "event": f"LEASED {offered_ip}",
    })

    print("\nIP ASSIGNED SUCCESSFULLY")
    print(f"Client:       {client}")
    print(f"IP address:   {offered_ip}")
    print(f"Subnet mask:  255.255.255.0")
    print(f"Gateway:      {POOLS[subnet]['gateway']}")
    print("DNS server:   8.8.8.8")


def show_leases():
    print("\n--- ACTIVE DHCP LEASES ---")
    if not leases:
        print("No active leases.")
        return

    print(f"{'Client':<12}{'IP Address':<18}{'Subnet':<12}{'Gateway'}")
    print("-" * 62)
    for client, details in leases.items():
        print(
            f"{client:<12}{details['ip']:<18}"
            f"{details['subnet']:<12}{details['gateway']}"
        )


def release_ip():
    client = input("Enter client name to release (e.g., PC4): ").strip()

    if client not in leases:
        print("No active lease found for that client.")
        return

    released = leases.pop(client)
    history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "client": client,
        "subnet": released["subnet"],
        "event": f"RELEASED {released['ip']}",
    })

    print(f"Released {released['ip']} from {client}.")
    print("That address is now available for reuse.")


def show_history():
    print("\n--- DHCP EVENT LOG ---")
    if not history:
        print("No events recorded yet.")
        return

    for event in history:
        print(
            f"{event['time']} | {event['client']:<10} | "
            f"{event['subnet']:<9} | {event['event']}"
        )


def show_pool_status():
    print("\n--- ADDRESS POOL STATUS ---")
    for subnet, pool in POOLS.items():
        total = (
            int(ipaddress.ip_address(pool["end"]))
            - int(ipaddress.ip_address(pool["start"]))
            + 1
        )
        available = len(get_available_ips(subnet))
        print(
            f"{subnet}: {total - available}/{total} allocated, "
            f"{available} available"
        )


def main():
    while True:
        print("\n" + "=" * 44)
        print(" MULTI-SUBNET DHCP SIMULATOR")
        print("=" * 44)
        print("1. Request IP (simulate DHCP DORA)")
        print("2. View active leases")
        print("3. Release an IP address")
        print("4. View DHCP event log")
        print("5. View pool utilization")
        print("6. Exit")

        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            request_ip()
        elif choice == "2":
            show_leases()
        elif choice == "3":
            release_ip()
        elif choice == "4":
            show_history()
        elif choice == "5":
            show_pool_status()
        elif choice == "6":
            print("DHCP simulation ended.")
            break
        else:
            print("Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()
