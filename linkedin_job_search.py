"""
LinkedIn Job Search Script
Uses linkedin-jobs-scraper to search and extract job data from LinkedIn.

Features:
- Search for jobs by keywords, location, and filters
- Extract job details including title, company, description, salary, etc.
- Save results to CSV or JSON files
- Support for multiple search queries
- Rate limiting and error handling
"""

import logging
import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
    ExperienceLevelFilters,
    OnSiteOrRemoteFilters,
    SalaryBaseFilters,
    IndustryFilters,
)


class LinkedInJobSearcher:
    def __init__(self, headless=True, slow_mo=1.0, max_workers=1, output_dir="data"):
        """
        Initialize the LinkedIn Job Searcher.

        Args:
            headless (bool): Run browser in headless mode
            slow_mo (float): Delay between requests to avoid rate limiting
            max_workers (int): Number of concurrent workers
            output_dir (str): Directory to save output files
        """
        self.output_dir = output_dir
        self.jobs_data = []
        self.total_jobs_processed = 0

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Initialize scraper
        self.scraper = LinkedinScraper(
            chrome_executable_path=None,
            chrome_binary_location=None,
            chrome_options=None,
            headless=headless,
            max_workers=max_workers,
            slow_mo=slow_mo,
            page_load_timeout=40,
        )

        # Add event listeners
        self.scraper.on(Events.DATA, lambda data: self.on_data(data))
        self.scraper.on(Events.ERROR, lambda error: self.on_error(error))
        self.scraper.on(Events.END, lambda: self.on_end())
        self.scraper.on(Events.METRICS, lambda metrics: self.on_metrics(metrics))

    def on_data(self, data: EventData):
        """Handle job data extraction."""
        job_info = {
            "job_id": data.job_id,
            "title": data.title,
            "company": data.company,
            "company_link": data.company_link,
            "company_img_link": data.company_img_link,
            "location": data.place,
            "description": data.description,
            "description_html": data.description_html,
            "date": data.date,
            "date_text": data.date_text,
            "link": data.link,
            "apply_link": data.apply_link,
            "insights": data.insights,
            "scraped_at": datetime.now().isoformat(),
        }

        self.jobs_data.append(job_info)
        self.total_jobs_processed += 1

        self.logger.info(
            f"[JOB {self.total_jobs_processed}] {data.title} at {data.company}"
        )

    def on_metrics(self, metrics: EventMetrics):
        """Handle metrics data."""
        self.logger.info(
            f"[METRICS] Processed: {metrics.processed}, Failed: {metrics.failed}, Total: {metrics.total}"
        )

    def on_error(self, error):
        """Handle errors."""
        self.logger.error(f"[ERROR] {error}")

    def on_end(self):
        """Handle scraping completion."""
        self.logger.info(f"[COMPLETED] Total jobs scraped: {self.total_jobs_processed}")

    def create_basic_query(
        self,
        keywords: str = "",
        locations: List[str] = None,
        limit: int = 25,
        skip_promoted: bool = True,
    ) -> Query:
        """
        Create a basic job search query.

        Args:
            keywords (str): Job search keywords
            locations (List[str]): List of locations to search
            limit (int): Maximum number of jobs to scrape
            skip_promoted (bool): Skip promoted/sponsored jobs

        Returns:
            Query: Configured query object
        """
        if locations is None:
            locations = ["United States"]

        return Query(
            query=keywords,
            options=QueryOptions(
                locations=locations,
                apply_link=True,
                skip_promoted_jobs=skip_promoted,
                limit=limit,
            ),
        )

    def create_advanced_query(
        self,
        keywords: str = "",
        locations: List[str] = None,
        limit: int = 25,
        relevance: str = "RECENT",
        time_filter: str = "MONTH",
        job_types: List[str] = None,
        experience_levels: List[str] = None,
        work_arrangement: List[str] = None,
        salary_base: str = None,
        industries: List[str] = None,
        company_jobs_url: str = None,
    ) -> Query:
        """
        Create an advanced job search query with filters.

        Args:
            keywords (str): Job search keywords
            locations (List[str]): List of locations to search
            limit (int): Maximum number of jobs to scrape
            relevance (str): Relevance filter (RELEVANT, RECENT)
            time_filter (str): Time filter (DAY, WEEK, MONTH, ANY)
            job_types (List[str]): Job types (FULL_TIME, PART_TIME, CONTRACT, TEMPORARY)
            experience_levels (List[str]): Experience levels (INTERNSHIP, ENTRY_LEVEL, ASSOCIATE, MID_SENIOR, DIRECTOR)
            work_arrangement (List[str]): Work arrangement (ON_SITE, REMOTE, HYBRID)
            salary_base (str): Base salary filter (SALARY_40K, SALARY_60K, etc.)
            industries (List[str]): Industry filters
            company_jobs_url (str): Specific company jobs URL

        Returns:
            Query: Configured advanced query object
        """
        if locations is None:
            locations = ["United States"]

        if job_types is None:
            job_types = ["FULL_TIME"]

        # Convert string filters to filter objects
        filters = QueryFilters()

        if relevance == "RECENT":
            filters.relevance = RelevanceFilters.RECENT
        elif relevance == "RELEVANT":
            filters.relevance = RelevanceFilters.RELEVANT

        if time_filter == "DAY":
            filters.time = TimeFilters.DAY
        elif time_filter == "WEEK":
            filters.time = TimeFilters.WEEK
        elif time_filter == "MONTH":
            filters.time = TimeFilters.MONTH
        elif time_filter == "ANY":
            filters.time = TimeFilters.ANY

        # Job types
        type_filters = []
        for job_type in job_types:
            if job_type == "FULL_TIME":
                type_filters.append(TypeFilters.FULL_TIME)
            elif job_type == "PART_TIME":
                type_filters.append(TypeFilters.PART_TIME)
            elif job_type == "CONTRACT":
                type_filters.append(TypeFilters.CONTRACT)
            elif job_type == "TEMPORARY":
                type_filters.append(TypeFilters.TEMPORARY)
        if type_filters:
            filters.type = type_filters

        # Experience levels
        if experience_levels:
            exp_filters = []
            for exp in experience_levels:
                if exp == "INTERNSHIP":
                    exp_filters.append(ExperienceLevelFilters.INTERNSHIP)
                elif exp == "ENTRY_LEVEL":
                    exp_filters.append(ExperienceLevelFilters.ENTRY_LEVEL)
                elif exp == "ASSOCIATE":
                    exp_filters.append(ExperienceLevelFilters.ASSOCIATE)
                elif exp == "MID_SENIOR":
                    exp_filters.append(ExperienceLevelFilters.MID_SENIOR)
                elif exp == "DIRECTOR":
                    exp_filters.append(ExperienceLevelFilters.DIRECTOR)
            if exp_filters:
                filters.experience = exp_filters

        # Work arrangement
        if work_arrangement:
            work_filters = []
            for work in work_arrangement:
                if work == "ON_SITE":
                    work_filters.append(OnSiteOrRemoteFilters.ON_SITE)
                elif work == "REMOTE":
                    work_filters.append(OnSiteOrRemoteFilters.REMOTE)
                elif work == "HYBRID":
                    work_filters.append(OnSiteOrRemoteFilters.HYBRID)
            if work_filters:
                filters.on_site_or_remote = work_filters

        # Salary filter
        if salary_base:
            if salary_base == "SALARY_40K":
                filters.base_salary = SalaryBaseFilters.SALARY_40K
            elif salary_base == "SALARY_60K":
                filters.base_salary = SalaryBaseFilters.SALARY_60K
            elif salary_base == "SALARY_80K":
                filters.base_salary = SalaryBaseFilters.SALARY_80K
            elif salary_base == "SALARY_100K":
                filters.base_salary = SalaryBaseFilters.SALARY_100K
            elif salary_base == "SALARY_120K":
                filters.base_salary = SalaryBaseFilters.SALARY_120K
            elif salary_base == "SALARY_140K":
                filters.base_salary = SalaryBaseFilters.SALARY_140K
            elif salary_base == "SALARY_160K":
                filters.base_salary = SalaryBaseFilters.SALARY_160K
            elif salary_base == "SALARY_180K":
                filters.base_salary = SalaryBaseFilters.SALARY_180K
            elif salary_base == "SALARY_200K":
                filters.base_salary = SalaryBaseFilters.SALARY_200K

        # Company filter
        if company_jobs_url:
            filters.company_jobs_url = company_jobs_url

        return Query(
            query=keywords,
            options=QueryOptions(
                locations=locations,
                apply_link=True,
                skip_promoted_jobs=True,
                limit=limit,
                filters=filters,
            ),
        )

    def search_jobs(self, queries: List[Query]):
        """
        Execute job search with given queries.

        Args:
            queries (List[Query]): List of query objects to execute
        """
        self.logger.info(f"Starting job search with {len(queries)} queries...")
        self.jobs_data = []
        self.total_jobs_processed = 0

        try:
            self.scraper.run(queries)
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")

    def save_to_csv(self, filename: str = None):
        """
        Save job data to CSV file.

        Args:
            filename (str): Output filename (optional)
        """
        if not self.jobs_data:
            self.logger.warning("No job data to save")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Get all unique keys from job data
        all_keys = set()
        for job in self.jobs_data:
            all_keys.update(job.keys())

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
            writer.writeheader()
            writer.writerows(self.jobs_data)

        self.logger.info(f"Saved {len(self.jobs_data)} jobs to {filepath}")

    def save_to_json(self, filename: str = None):
        """
        Save job data to JSON file.

        Args:
            filename (str): Output filename (optional)
        """
        if not self.jobs_data:
            self.logger.warning("No job data to save")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_jobs_{timestamp}.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as jsonfile:
            json.dump(self.jobs_data, jsonfile, indent=2, ensure_ascii=False)

        self.logger.info(f"Saved {len(self.jobs_data)} jobs to {filepath}")

    def get_job_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of scraped jobs.

        Returns:
            Dict: Summary statistics
        """
        if not self.jobs_data:
            return {"total_jobs": 0}

        companies = [job.get("company", "Unknown") for job in self.jobs_data]
        locations = [job.get("location", "Unknown") for job in self.jobs_data]

        summary = {
            "total_jobs": len(self.jobs_data),
            "unique_companies": len(set(companies)),
            "unique_locations": len(set(locations)),
            "top_companies": self._get_top_items(companies, 5),
            "top_locations": self._get_top_items(locations, 5),
        }

        return summary

    def _get_top_items(self, items: List[str], top_n: int = 5) -> List[tuple]:
        """Get top N most frequent items."""
        from collections import Counter

        counter = Counter(items)
        return counter.most_common(top_n)


def main():
    """Example usage of the LinkedIn Job Searcher."""

    # Initialize the searcher
    searcher = LinkedInJobSearcher(
        headless=True,
        slow_mo=1.0,  # Adjust based on rate limiting
        max_workers=1,
        output_dir="data",
    )

    # Example 1: Basic search
    print("Example 1: Basic job search")
    basic_queries = [
        searcher.create_basic_query(
            keywords="Python Developer", locations=["United States", "Remote"], limit=10
        )
    ]

    searcher.search_jobs(basic_queries)
    searcher.save_to_csv("basic_python_jobs.csv")
    searcher.save_to_json("basic_python_jobs.json")

    # Example 2: Advanced search with filters
    print("\nExample 2: Advanced search with filters")
    advanced_queries = [
        searcher.create_advanced_query(
            keywords="Data Scientist",
            locations=["San Francisco", "New York", "Remote"],
            limit=15,
            relevance="RECENT",
            time_filter="MONTH",
            job_types=["FULL_TIME"],
            experience_levels=["MID_SENIOR"],
            work_arrangement=["REMOTE", "HYBRID"],
            salary_base="SALARY_100K",
        )
    ]

    searcher.search_jobs(advanced_queries)
    searcher.save_to_csv("advanced_data_scientist_jobs.csv")

    # Print summary
    summary = searcher.get_job_summary()
    print(f"\nJob Search Summary:")
    print(f"Total jobs: {summary['total_jobs']}")
    print(f"Unique companies: {summary['unique_companies']}")
    print(f"Top companies: {summary.get('top_companies', [])}")


if __name__ == "__main__":
    main()
