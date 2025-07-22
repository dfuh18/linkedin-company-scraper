"""
Simple LinkedIn Job Search Example
A basic script to demonstrate the linkedin-jobs-scraper usage.
"""

import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters,
    TimeFilters,
    TypeFilters,
    ExperienceLevelFilters,
    OnSiteOrRemoteFilters,
)

# Configure logging
logging.basicConfig(level=logging.INFO)


def main():
    # Storage for job data
    jobs_data = []

    # Event handlers
    def on_data(data: EventData):
        job_info = {
            "title": data.title,
            "company": data.company,
            "location": data.place,
            "date": data.date,
            "link": data.link,
            "apply_link": data.apply_link,
            "description_length": len(data.description) if data.description else 0,
        }
        jobs_data.append(job_info)
        print(f"Found job: {data.title} at {data.company} in {data.place}")

    def on_metrics(metrics: EventMetrics):
        print(
            f"Metrics - Processed: {metrics.processed}, Failed: {metrics.failed}, Total: {metrics.total}"
        )

    def on_error(error):
        print(f"Error: {error}")

    def on_end():
        print(f"Scraping completed! Found {len(jobs_data)} jobs.")

    # Initialize scraper
    scraper = LinkedinScraper(
        chrome_executable_path=None,
        chrome_binary_location=None,
        chrome_options=None,
        headless=True,  # Set to False to see browser window
        max_workers=1,
        slow_mo=1.0,  # Slow down to avoid rate limiting
        page_load_timeout=40,
    )

    # Add event listeners
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)
    scraper.on(Events.METRICS, on_metrics)

    # Define search queries
    queries = [
        # Basic search
        Query(
            query="Python Developer",
            options=QueryOptions(
                locations=["United States"],
                limit=5,  # Small limit for testing
                apply_link=True,
                skip_promoted_jobs=True,
            ),
        ),
        # Advanced search with filters
        Query(
            query="Data Scientist",
            options=QueryOptions(
                locations=["Remote", "San Francisco"],
                limit=5,
                apply_link=True,
                skip_promoted_jobs=True,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.WEEK,
                    type=[TypeFilters.FULL_TIME],
                    experience=[ExperienceLevelFilters.MID_SENIOR],
                    on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE],
                ),
            ),
        ),
    ]

    try:
        # Run the scraper
        print("Starting LinkedIn job search...")
        scraper.run(queries)

        # Print results
        print(f"\n=== RESULTS ===")
        print(f"Total jobs found: {len(jobs_data)}")

        for i, job in enumerate(jobs_data, 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Date: {job['date']}")
            print(f"   Link: {job['link']}")
            if job["apply_link"]:
                print(f"   Apply Link: {job['apply_link']}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("This might be due to:")
        print("1. Chrome/Chromedriver not being installed")
        print("2. Network connectivity issues")
        print("3. LinkedIn rate limiting")
        print("4. Authentication requirements in your environment")


if __name__ == "__main__":
    main()
