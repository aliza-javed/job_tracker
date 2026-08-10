"""
utils.py
--------
Helper functions - Reusable code jo baar baar use hoga.
Topics: Functions, Exceptions, Datetime, String formatting
"""

from datetime import datetime


def get_current_date():
    """
    Current date return karta hai 'YYYY-MM-DD' format mein.
    datetime module practice.
    """
    return datetime.now().strftime("%Y-%m-%d")


def validate_date(date_string):
    """
    Date validate karta hai.
    Agar format galat ho toh ValueError raise hoga.
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_salary(salary):
    """
    Salary validate karta hai:
    - Integer honi chahiye
    - Positive honi chahiye
    """
    try:
        salary = int(salary)
        if salary < 0:
            return False
        return True
    except (ValueError, TypeError):
        return False


def validate_status(status):
    """
    Status valid options mein hona chahiye.
    Conditions (if-else) ka practice.
    """
    valid_statuses = [
        "Applied",
        "Interview Scheduled",
        "Offer Received",
        "Rejected",
        "Withdrawn"
    ]
    return status in valid_statuses


def format_job_display(job, index=None):
    """
    Job ko achi tarah display karne ke liye format karta hai.
    String formatting practice.
    """
    prefix = f"[{index}] " if index is not None else ""
    
    display = f"""
{prefix}Company    : {job['company']}
    Title       : {job['title']}
    Status      : {job['status']}
    Salary      : ${job['salary']:,}
    Applied Date: {job['applied_date']}
    """
    return display


def generate_job_id(jobs_list):
    """
    Naya unique ID generate karta hai.
    List comprehension + max function practice.
    """
    if not jobs_list:
        return 1
    
    # Sab IDs nikalo, max lo, +1 karo
    ids = [job.get("id", 0) for job in jobs_list]
    return max(ids) + 1


def print_separator(char="=", length=50):
    """Separator line print karta hai."""
    print(char * length)


def print_header(title):
    """Header print karta hai."""
    print_separator()
    print(f"  {title}")
    print_separator()


# Test
if __name__ == "__main__":
    print("Current date:", get_current_date())
    print("Valid date?", validate_date("2026-08-10"))
    print("Valid date?", validate_date("10-08-2026"))
    print("Valid salary?", validate_salary(30000))
    print("Valid status?", validate_status("Applied"))
    print("Valid status?", validate_status("Pending"))