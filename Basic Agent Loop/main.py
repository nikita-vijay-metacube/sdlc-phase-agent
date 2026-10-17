import sys
from src.request_handler import FeatureRequest
from src.storage import JSONStorage
from src.analytics import RequestAnalytics
from src.agent import SimpleAgent

def display_menu():
    print("\n=== Feature Request Tracker ===")
    print("1. Add Request")
    print("2. View Requests")
    print("3. View Analytics & Generate Chart")
    print("4. Exit")
    print("===============================")

def handle_add_request(storage: JSONStorage, agent: SimpleAgent):
    print("\n--- Add New Feature Request ---")
    while True:
        description = input("Enter description (10-500 chars): ").strip()
        is_valid, error_msg = FeatureRequest.validate_description(description)
        if is_valid:
            break
        print(f"Error: {error_msg}")

    client = input("Enter client name: ").strip() or "Internal"
    project = input("Enter project name: ").strip() or "General"

    print("\n[Agent Loop Active]")
    print(" -> [Observe] Parsing input and checking context history...")
    print(" -> [Reason] Evaluating SDLC phase and confidence...")
    
    # Run Agent ORA Loop
    result = agent.process_request(description)
    
    print(f" -> [Act] Reasoning: {result['reasoning']}")
    print(f" -> [Act] {result['advice']}")

    req = FeatureRequest(
        description=description, 
        client=client, 
        project=project, 
        phase=result['phase'], 
        confidence=result['confidence'],
        advice=result['advice']
    )
    storage.append_request(req.__dict__)
    print(f"\nSuccess: Request [{req.id}] saved with Phase: {result['phase'].upper()}!")

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
        print(f"   Phase: {req.get('phase', 'Unassigned').upper()} [Confidence: {req.get('confidence', 'N/A')}]")
        print(f"   Agent Advice: {req.get('advice', 'N/A')}")
        print(f"   Timestamp: {req.get('timestamp')}")
    print("-" * 30)

def handle_analytics():
    print("\n--- Request Analytics ---")
    analytics = RequestAnalytics()
    stats = analytics.calculate_stats()
    
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Average Description Length: {stats['avg_length']} characters")
    
    print("\nKeyword Frequency:")
    if stats['keyword_counts']:
        for kw, count in stats['keyword_counts'].items():
            print(f"  - '{kw}': {count} time(s)")
    else:
        print("  No common keywords detected.")

    chart_path = analytics.generate_chart()
    print(f"\nSuccess: Analytics chart saved to {chart_path}")

def main():
    storage = JSONStorage()
    agent = SimpleAgent(memory_limit=2)
    
    while True:
        display_menu()
        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            handle_add_request(storage, agent)
        elif choice == "2":
            handle_view_requests(storage)
        elif choice == "3":
            handle_analytics()
        elif choice == "4":
            print("Exiting Feature Request Tracker. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please choose between 1 and 4.")

if __name__ == "__main__":
    main()