import sys
from src.request_handler import FeatureRequest
from src.storage import JSONStorage

def display_menu():
    print("\n=== Feature Request Tracker ===")
    print("1. Add Request")
    print("2. View Requests")
    print("3. Exit")
    print("===============================")

def handle_add_request(storage: JSONStorage):
    print("\n--- Add New Feature Request ---")
    
    while True:
        description = input("Enter description (10-500 chars): ").strip()
        is_valid, error_msg = FeatureRequest.validate_description(description)
        if is_valid:
            break
        print(f"Error: {error_msg}")

    client = input("Enter client name: ").strip() or "Internal"
    project = input("Enter project name: ").strip() or "General"

    req = FeatureRequest(description=description, client=client, project=project)
    
    storage.append_request(req.__dict__)
    print(f"Success: Request [{req.id}] saved successfully!")

def handle_view_requests(storage: JSONStorage):
    print("\n--- Stored Feature Requests ---")
    requests = storage.load_requests()
    
    if not requests:
        print("No feature requests found.")
        return

    for idx, req in enumerate(requests, 1):
        print(f"\n{idx}. ID: {req.get('id')}")
        print(f"   Project: {req.get('project')} | Client: {req.get('client')}")
        print(f"   Description: {req.get('description')}")
        print(f"   Timestamp: {req.get('timestamp')}")
    print("-" * 30)

def main():
    storage = JSONStorage()
    
    while True:
        display_menu()
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            handle_add_request(storage)
        elif choice == "2":
            handle_view_requests(storage)
        elif choice == "3":
            print("Exiting Feature Request Tracker. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please choose between 1 and 3.")

if __name__ == "__main__":
    main()