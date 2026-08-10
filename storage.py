"""
storage.py
----------
File handling - JSON aur CSV mein data save/load karna.
Topics: File I/O, JSON, CSV, Exceptions, Modules
"""

import json
import csv
import os
from logger_config import setup_logger

# Logger setup
logger = setup_logger()

# File names
JSON_FILE = "jobs.json"
CSV_FILE = "jobs.csv"


def save_to_json(jobs_list):
    """
    Jobs list ko JSON file mein save karta hai.
    JSON = JavaScript Object Notation - data store karne ka standard format.
    
    with statement = file automatically close ho jayegi
    indent = readable format mein save hoga
    """
    try:
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(jobs_list, file, indent=4, ensure_ascii=False)
        logger.info(f"{len(jobs_list)} jobs saved to {JSON_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        return False


def load_from_json():
    """
    JSON file se jobs load karta hai.
    Agar file nahi hai toh empty list return karega.
    """
    try:
        if not os.path.exists(JSON_FILE):
            logger.info("No existing data found. Starting fresh.")
            return []
        
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            jobs = json.load(file)
        
        logger.info(f"{len(jobs)} jobs loaded from {JSON_FILE}")
        return jobs
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON file corrupted: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading from JSON: {e}")
        return []


def export_to_csv(jobs_list):
    """
    Jobs ko CSV file mein export karta hai.
    CSV = Comma Separated Values - Excel mein khul jayega.
    """
    if not jobs_list:
        logger.warning("No jobs to export!")
        return False
    
    try:
        # Field names - CSV ke columns
        fieldnames = ["id", "company", "title", "status", "salary", "applied_date"]
        
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Header likho
            writer.writeheader()
            
            # Har job row likho
            for job in jobs_list:
                writer.writerow(job)
        
        logger.info(f"{len(jobs_list)} jobs exported to {CSV_FILE}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return False


def import_from_csv():
    """
    CSV file se jobs import karta hai.
    """
    try:
        if not os.path.exists(CSV_FILE):
            logger.warning("CSV file not found!")
            return []
        
        jobs = []
        with open(CSV_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Salary ko integer mein convert karo
                row["salary"] = int(row["salary"])
                row["id"] = int(row["id"])
                jobs.append(row)
        
        logger.info(f"{len(jobs)} jobs imported from {CSV_FILE}")
        return jobs
    
    except Exception as e:
        logger.error(f"Error importing from CSV: {e}")
        return []


# Test
if __name__ == "__main__":
    test_jobs = [
        {
            "id": 1,
            "company": "Adzuna",
            "title": "Junior Python Developer",
            "status": "Applied",
            "salary": 30000,
            "applied_date": "2026-08-10"
        }
    ]
    
    save_to_json(test_jobs)
    loaded = load_from_json()
    print("Loaded:", loaded)
    
    export_to_csv(test_jobs)
    imported = import_from_csv()
    print("Imported:", imported)