import sys
import time
from src.request_handler import FeatureRequest
from src.storage import JSONStorage
from src.analytics import RequestAnalytics
from src.langchain_agent import LangChainStyleAgent
from src.document_generator import DocumentGenerator
from src.metrics_logger import MetricsLogger
from src.security import SecurityManager

def display_help():
    print("\n=============================================")
    print("        SDLC FEATURE TRACKER - HELP          ")
    print("=============================================")
    print("1. Add Request: Captures feature description,")
    print("   sanitizes input, runs rate-limiting checks,")
    print("   detects SDLC phase via AI, and generates Markdown docs.")
    print("2. View Requests: Lists all stored records with phases.")
    print("3. View Analytics: Summarizes metrics and saves PNG chart.")
    print("4. Performance Dashboard: Displays success rate & response times.")
    print("5. Help: Displays this user guide.")
    print("6. Exit: Safely closes the application.")
    print("=============================================")

def display_menu():
    print("\n=== Feature Request Tracker ===")
    print("1. Add Request")
    print("2. View Requests")
    print("3. View Analytics & Generate Chart")
    print("4. View Performance Dashboard & Logs")
    print("5. Help & Documentation")
    print("6. Exit")
    print("===============================")

def handle_add_request(storage: JSONStorage, agent: LangChainStyleAgent, doc_gen: DocumentGenerator, logger: MetricsLogger, security: SecurityManager):
    print("\n--- Add New Feature Request ---")
    
    # 1. Rate Limit Check
    allowed, rate_msg = security.check_rate_limit()
    if not allowed:
        print(f"Security Notice: {rate_msg}")
        return

    # 2. Input Collection & Validation Loop
    while True:
        raw_description = input("Enter description (10-500 chars): ")
        is_valid, sanitized_or_error = security.validate_request_description(raw_description)
        if is_valid:
            description = sanitized_or_error
            break
        print(f"Validation Error: {sanitized_or_error}")

    client = security.sanitize_input(input("Enter client name: ").strip() or "Internal")
    project = security.sanitize_input(input("Enter project name: ").strip() or "General")

    print("\n[Executing Secure Agent Workflow...]")
    start_time = time.time()
    success = True
    error_msg = None
    result = {}

    try:
        result = agent.process_request(description)
    except Exception as e:
        success = False
        error_msg = str(e)
        result = {
            "phase": "requirements",
            "confidence": "Low",
            "advice": "Review manually due to unexpected processing exception."
        }
    
    response_time = time.time() - start_time

    # 3. Log Audit & Metrics Event
    logger.log_event(
        description=description,
        phase=result.get('phase', 'unassigned'),
        success=success,
        response_time=response_time,
        error=error_msg
    )

    print(f" -> Phase Detected: {result['phase'].upper()} (Confidence: {result['confidence']}) [Time: {response_time:.3f}s]")
    print(f" -> {result['advice']}")

    # 4. Generate Document Artifact
    temp_data = {
        "id": "new",
        "description": description,
        "client": client,
        "project": project,
        "phase": result['phase']
    }
    artifact_path = doc_gen.create_document(temp_data, llm_model=getattr(agent, "model", None))

    # 5. Save to Persistent JSON Storage
    req = FeatureRequest(
        description=description, 
        client=client, 
        project=project, 
        phase=result['phase'], 
        confidence=result['confidence'],
        advice=result['advice'],
        artifact_path=artifact_path
    )
    storage.append_request(req.__dict__)
    
    print(f"\nSuccess: Request [{req.id}] processed and saved!")
    print(f" -> Organized Artifact Generated: {artifact_path}")

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
        print(f"   Artifact File: {req.get('artifact_path', 'N/A')}")
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

def handle_dashboard(logger: MetricsLogger):
    print("\n=== Agent Performance Dashboard ===")
    stats = logger.get_dashboard_stats()
    
    print(f"Total Interactions Processed : {stats['total_interactions']}")
    print(f"Success Rate Percentage     : {stats['success_rate']}%")
    print(f"Average Response Time       : {stats['avg_response_time']} seconds")
    
    print("\nMost Detected Phases:")
    if stats['phases_detected']:
        sorted_phases = sorted(stats['phases_detected'].items(), key=lambda x: x[1], reverse=True)
        for phase, count in sorted_phases:
            print(f"  - {phase.upper()}: {count} time(s)")
    else:
        print("  No phase data recorded yet.")

    print("\nRecent Errors / Debug Logs:")
    if stats['recent_errors']:
        for err in stats['recent_errors']:
            print(f"  [ERROR] {err}")
    else:
        print("  No recent errors logged. System running smoothly!")
    print("====================================")

def main():
    storage = JSONStorage()
    agent = LangChainStyleAgent(memory_window=2)
    doc_gen = DocumentGenerator()
    logger = MetricsLogger()
    security = SecurityManager(rate_limit_seconds=1.0)
    
    print("Welcome to the SDLC Feature Request Tracker & AI Agent System!")

    while True:
        display_menu()
        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            handle_add_request(storage, agent, doc_gen, logger, security)
        elif choice == "2":
            handle_view_requests(storage)
        elif choice == "3":
            handle_analytics()
        elif choice == "4":
            handle_dashboard(logger)
        elif choice == "5":
            display_help()
        elif choice == "6":
            print("Exiting Feature Request Tracker. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please choose between 1 and 6.")

if __name__ == "__main__":
    main()