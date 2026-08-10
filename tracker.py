"""
tracker.py
----------
Main tracker class - Sab business logic yahan hoga.
Topics: Classes, Dictionaries, Lists, Loops, Conditions, Functions, Exceptions
"""

from storage import save_to_json, load_from_json, export_to_csv
from utils import (
    get_current_date,
    validate_date,
    validate_salary,
    validate_status,
    format_job_display,
    generate_job_id,
    print_separator,
    print_header
)
from logger_config import setup_logger


class JobTracker:
    """
    Job Application Tracker class.
    Har feature ek method hoga.
    """
    
    def __init__(self):
        """Constructor - jab bhi tracker start hoga, data load hoga."""
        self.logger = setup_logger()
        self.jobs = load_from_json()
        self.valid_statuses = [
            "Applied",
            "Interview Scheduled",
            "Offer Received",
            "Rejected",
            "Withdrawn"
        ]
        self.logger.info("Job Tracker initialized!")
    
    # ─────────────────────────────────────────────
    # 1. ADD JOB
    # ─────────────────────────────────────────────
    def add_job(self, company, title, status, salary, applied_date=None):
        """
        Naya job add karta hai.
        Dictionary banai jayegi, list mein append hogi.
        """
        try:
            # ── Validation ──
            if not company or not company.strip():
                raise ValueError("Company name cannot be empty!")
            
            if not title or not title.strip():
                raise ValueError("Job title cannot be empty!")
            
            if not validate_status(status):
                raise ValueError(
                    f"Invalid status! Choose from: {', '.join(self.valid_statuses)}"
                )
            
            if not validate_salary(salary):
                raise ValueError("Salary must be a positive number!")
            
            # Date nahi diya toh aaj ki date lo
            if applied_date is None:
                applied_date = get_current_date()
            elif not validate_date(applied_date):
                raise ValueError("Date format should be YYYY-MM-DD!")
            
            # ── Job Dictionary Create ──
            job = {
                "id": generate_job_id(self.jobs),
                "company": company.strip().title(),
                "title": title.strip().title(),
                "status": status,
                "salary": int(salary),
                "applied_date": applied_date
            }
            
            # ── List mein Append ──
            self.jobs.append(job)
            
            # ── Save to File ──
            save_to_json(self.jobs)
            
            self.logger.info(f"Job added: {title} at {company}")
            print(f"\n✅ Job added successfully! (ID: {job['id']})")
            return True
        
        except ValueError as e:
            self.logger.warning(f"Validation error: {e}")
            print(f"\n❌ Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error adding job: {e}")
            print(f"\n❌ Unexpected error: {e}")
            return False
    
    # ─────────────────────────────────────────────
    # 2. UPDATE JOB
    # ─────────────────────────────────────────────
    def update_job(self, job_id, **kwargs):
        """
        Job update karta hai ID se.
        **kwargs = keyword arguments - jo bhi field update karna ho.
        """
        try:
            # Job dhundho
            job = self._find_job_by_id(job_id)
            if not job:
                raise ValueError(f"Job with ID {job_id} not found!")
            
            # Allowed fields
            allowed_fields = ["company", "title", "status", "salary", "applied_date"]
            
            # Har field update karo
            for key, value in kwargs.items():
                if key not in allowed_fields:
                    print(f"⚠️  '{key}' is not a valid field. Skipping.")
                    continue
                
                # Validation
                if key == "status" and not validate_status(value):
                    print(f"⚠️  Invalid status '{value}'. Skipping.")
                    continue
                
                if key == "salary" and not validate_salary(value):
                    print(f"⚠️  Invalid salary '{value}'. Skipping.")
                    continue
                
                if key == "applied_date" and not validate_date(value):
                    print(f"⚠️  Invalid date '{value}'. Skipping.")
                    continue
                
                # Update
                if key == "salary":
                    job[key] = int(value)
                elif key in ["company", "title"]:
                    job[key] = value.strip().title()
                else:
                    job[key] = value
            
            # Save
            save_to_json(self.jobs)
            self.logger.info(f"Job {job_id} updated")
            print(f"\n✅ Job {job_id} updated successfully!")
            return True
        
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error updating job: {e}")
            print(f"\n❌ Error: {e}")
            return False
    
    # ─────────────────────────────────────────────
    # 3. DELETE JOB
    # ─────────────────────────────────────────────
    def delete_job(self, job_id):
        """
        Job delete karta hai ID se.
        List se remove karna.
        """
        try:
            job = self._find_job_by_id(job_id)
            if not job:
                raise ValueError(f"Job with ID {job_id} not found!")
            
            # Confirm
            print(f"\nJob to delete: {job['title']} at {job['company']}")
            confirm = input("Are you sure? (y/n): ").lower()
            
            if confirm == "y":
                self.jobs.remove(job)
                save_to_json(self.jobs)
                self.logger.info(f"Job {job_id} deleted")
                print(f"\n✅ Job {job_id} deleted successfully!")
                return True
            else:
                print("\n❌ Deletion cancelled.")
                return False
        
        except ValueError as e:
            print(f"\n❌ Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting job: {e}")
            print(f"\n❌ Error: {e}")
            return False
    
    # ─────────────────────────────────────────────
    # 4. VIEW JOBS
    # ─────────────────────────────────────────────
    def view_jobs(self):
        """
        Saari jobs display karta hai.
        Loop + Dictionary access practice.
        """
        if not self.jobs:
            print("\n📭 No jobs found. Add some jobs first!")
            return
        
        print_header(f"ALL JOBS ({len(self.jobs)} total)")
        
        # Loop through all jobs
        for index, job in enumerate(self.jobs, 1):
            print(format_job_display(job, index))
            print("-" * 40)
    
    # ─────────────────────────────────────────────
    # 5. SEARCH JOBS
    # ─────────────────────────────────────────────
    def search_jobs(self, keyword):
        """
        Keyword se jobs search karta hai.
        Company ya title mein search hoga.
        """
        if not keyword:
            print("\n❌ Please enter a keyword to search!")
            return []
        
        keyword = keyword.lower()
        results = []
        
        # Loop + Condition
        for job in self.jobs:
            if (keyword in job["company"].lower() or 
                keyword in job["title"].lower()):
                results.append(job)
        
        # Results display
        if results:
            print_header(f"SEARCH RESULTS for '{keyword}' ({len(results)} found)")
            for index, job in enumerate(results, 1):
                print(format_job_display(job, index))
                print("-" * 40)
        else:
            print(f"\n🔍 No jobs found matching '{keyword}'")
        
        return results
    
    # ─────────────────────────────────────────────
    # 6. FILTER BY STATUS
    # ─────────────────────────────────────────────
    def filter_by_status(self, status):
        """
        Status ke hisaab se jobs filter karta hai.
        List comprehension practice.
        """
        if not validate_status(status):
            print(f"\n❌ Invalid status! Choose from: {', '.join(self.valid_statuses)}")
            return []
        
        # List comprehension - ek line mein filter
        filtered = [job for job in self.jobs if job["status"] == status]
        
        if filtered:
            print_header(f"JOBS WITH STATUS: {status} ({len(filtered)} found)")
            for index, job in enumerate(filtered, 1):
                print(format_job_display(job, index))
                print("-" * 40)
        else:
            print(f"\n📭 No jobs with status '{status}'")
        
        return filtered
    
    # ─────────────────────────────────────────────
    # 7. STATISTICS
    # ─────────────────────────────────────────────
    def show_statistics(self):
        """
        Statistics dikhata hai - count, average salary, etc.
        Dictionary + Loop + Conditions practice.
        """
        if not self.jobs:
            print("\n📭 No data for statistics!")
            return
        
        total_jobs = len(self.jobs)
        
        # Status count - Dictionary comprehension
        status_counts = {}
        for status in self.valid_statuses:
            count = len([j for j in self.jobs if j["status"] == status])
            if count > 0:
                status_counts[status] = count
        
        # Salary stats
        salaries = [job["salary"] for job in self.jobs]
        avg_salary = sum(salaries) / len(salaries)
        max_salary = max(salaries)
        min_salary = min(salaries)
        
        # Display
        print_header("📊 JOB STATISTICS")
        print(f"  Total Applications : {total_jobs}")
        print(f"  Average Salary     : ${avg_salary:,.2f}")
        print(f"  Highest Salary     : ${max_salary:,}")
        print(f"  Lowest Salary      : ${min_salary:,}")
        print_separator("-")
        print("  Status Breakdown:")
        for status, count in status_counts.items():
            percentage = (count / total_jobs) * 100
            bar = "█" * int(percentage / 5)  # Visual bar
            print(f"    {status:25s}: {count:3d} ({percentage:5.1f}%) {bar}")
        print_separator()
    
    # ─────────────────────────────────────────────
    # 8. EXPORT CSV
    # ─────────────────────────────────────────────
    def export_csv(self):
        """CSV export wrapper."""
        if export_to_csv(self.jobs):
            print(f"\n✅ Jobs exported to jobs.csv successfully!")
        else:
            print(f"\n❌ Export failed!")
    
    # ─────────────────────────────────────────────
    # HELPER METHOD (Private)
    # ─────────────────────────────────────────────
    def _find_job_by_id(self, job_id):
        """
        Job ID se dhundhta hai.
        Private method - underscore se start.
        """
        try:
            job_id = int(job_id)
            for job in self.jobs:
                if job["id"] == job_id:
                    return job
            return None
        except (ValueError, TypeError):
            return None


# ── Test ──
if __name__ == "__main__":
    tracker = JobTracker()
    
    # Add test jobs
    tracker.add_job("Adzuna", "Junior Python Developer", "Applied", 30000, "2026-08-10")
    tracker.add_job("Google", "Software Engineer", "Interview Scheduled", 80000, "2026-08-09")
    tracker.add_job("Microsoft", "Data Analyst", "Offer Received", 65000, "2026-08-08")
    
    # View
    tracker.view_jobs()
    
    # Search
    tracker.search_jobs("python")
    
    # Filter
    tracker.filter_by_status("Applied")
    
    # Statistics
    tracker.show_statistics()