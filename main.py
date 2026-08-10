"""
main.py
-------
Entry point - Menu driven program.
User se input lena, functions call karna.
Topics: Loops, Conditions, Input/Output, Functions
"""

from tracker import JobTracker
from utils import print_separator, print_header


def display_menu():
    """Menu display karta hai."""
    print_header("📋 JOB APPLICATION TRACKER")
    print("""
    1.  ➕  Add Job
    2.  ✏️   Update Job
    3.  🗑️   Delete Job
    4.  📄  View All Jobs
    5.  🔍  Search Jobs
    6.  🏷️   Filter by Status
    7.  📊  Statistics
    8.  📁  Export to CSV
    9.  🚪  Exit
    """)
    print_separator()


def get_job_input():
    """User se job details input leta hai."""
    print("\n--- Enter Job Details ---")
    
    company = input("Company Name: ")
    title = input("Job Title: ")
    
    # Status options show karo
    print("\nStatus Options:")
    print("  1. Applied")
    print("  2. Interview Scheduled")
    print("  3. Offer Received")
    print("  4. Rejected")
    print("  5. Withdrawn")
    
    status_choice = input("Choose status (1-5): ")
    status_map = {
        "1": "Applied",
        "2": "Interview Scheduled",
        "3": "Offer Received",
        "4": "Rejected",
        "5": "Withdrawn"
    }
    status = status_map.get(status_choice, "Applied")
    
    salary = input("Salary (number): ")
    applied_date = input("Applied Date (YYYY-MM-DD) or press Enter for today: ")
    
    if not applied_date.strip():
        applied_date = None
    
    return company, title, status, salary, applied_date


def main():
    """
    Main function - Program yahan se start hoga.
    While loop - jab tak user exit na kare.
    """
    tracker = JobTracker()
    
    # ── Main Loop ──
    while True:
        display_menu()
        choice = input("Enter your choice (1-9): ").strip()
        
        # ── Conditions ──
        if choice == "1":
            # Add Job
            company, title, status, salary, applied_date = get_job_input()
            tracker.add_job(company, title, status, salary, applied_date)
        
        elif choice == "2":
            # Update Job
            tracker.view_jobs()
            job_id = input("\nEnter Job ID to update: ")
            
            print("\nWhat do you want to update?")
            print("  1. Status")
            print("  2. Salary")
            print("  3. Company")
            print("  4. Title")
            
            update_choice = input("Choose (1-4): ")
            
            if update_choice == "1":
                new_status = input("New Status: ")
                tracker.update_job(job_id, status=new_status)
            elif update_choice == "2":
                new_salary = input("New Salary: ")
                tracker.update_job(job_id, salary=new_salary)
            elif update_choice == "3":
                new_company = input("New Company: ")
                tracker.update_job(job_id, company=new_company)
            elif update_choice == "4":
                new_title = input("New Title: ")
                tracker.update_job(job_id, title=new_title)
            else:
                print("❌ Invalid choice!")
        
        elif choice == "3":
            # Delete Job
            tracker.view_jobs()
            job_id = input("\nEnter Job ID to delete: ")
            tracker.delete_job(job_id)
        
        elif choice == "4":
            # View All Jobs
            tracker.view_jobs()
        
        elif choice == "5":
            # Search Jobs
            keyword = input("\nEnter keyword to search: ")
            tracker.search_jobs(keyword)
        
        elif choice == "6":
            # Filter by Status
            print("\nStatus Options:")
            print("  1. Applied")
            print("  2. Interview Scheduled")
            print("  3. Offer Received")
            print("  4. Rejected")
            print("  5. Withdrawn")
            
            status_choice = input("Choose status (1-5): ")
            status_map = {
                "1": "Applied",
                "2": "Interview Scheduled",
                "3": "Offer Received",
                "4": "Rejected",
                "5": "Withdrawn"
            }
            status = status_map.get(status_choice)
            if status:
                tracker.filter_by_status(status)
            else:
                print("❌ Invalid choice!")
        
        elif choice == "7":
            # Statistics
            tracker.show_statistics()
        
        elif choice == "8":
            # Export CSV
            tracker.export_csv()
        
        elif choice == "9":
            # Exit
            print("\n👋 Thank you for using Job Tracker! Goodbye!")
            break
        
        else:
            print("\n❌ Invalid choice! Please enter 1-9.")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")


# ── Program Start ──
if __name__ == "__main__":
    main()