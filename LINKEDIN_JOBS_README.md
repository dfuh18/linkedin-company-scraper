# LinkedIn Job Search Scripts

This directory contains scripts for searching and scraping LinkedIn job postings using the `linkedin-jobs-scraper` package.

## Files

- `linkedin_job_search.py` - Comprehensive job search class with advanced features
- `linkedin_job_search_simple.py` - Simple example script to get started
- `requirements.txt` - Updated with the linkedin-jobs-scraper package

## Setup

1. **Install Chrome or Chromium browser** (required for scraping)

2. **Install Python packages:**

   ```bash
   pip install -r requirements.txt
   ```

3. **For authenticated sessions** (if needed in your environment):
   - Login to LinkedIn in Chrome
   - Open Developer Tools (F12)
   - Go to Application > Cookies > https://www.linkedin.com
   - Copy the `li_at` cookie value
   - Set environment variable: `LI_AT_COOKIE=your_cookie_value`

## Usage

### Simple Example

Run the simple example to test the setup:

```bash
python linkedin_job_search_simple.py
```

This will search for Python Developer and Data Scientist jobs with basic filters.

### Advanced Usage

The main script (`linkedin_job_search.py`) provides a comprehensive class with features:

```python
from linkedin_job_search import LinkedInJobSearcher

# Initialize searcher
searcher = LinkedInJobSearcher(
    headless=True,      # Run browser in background
    slow_mo=1.0,        # Delay between requests (adjust for rate limiting)
    max_workers=1,      # Number of concurrent workers
    output_dir="data"   # Output directory for results
)

# Create a basic search query
query = searcher.create_basic_query(
    keywords="Software Engineer",
    locations=["United States", "Remote"],
    limit=25
)

# Or create an advanced query with filters
advanced_query = searcher.create_advanced_query(
    keywords="Machine Learning Engineer",
    locations=["San Francisco", "New York", "Remote"],
    limit=50,
    relevance="RECENT",
    time_filter="MONTH",
    job_types=["FULL_TIME"],
    experience_levels=["MID_SENIOR"],
    work_arrangement=["REMOTE", "HYBRID"],
    salary_base="SALARY_100K"
)

# Run the search
searcher.search_jobs([query, advanced_query])

# Save results
searcher.save_to_csv("my_job_search.csv")
searcher.save_to_json("my_job_search.json")

# Get summary statistics
summary = searcher.get_job_summary()
print(summary)
```

## Available Filters

### Job Types

- `FULL_TIME`
- `PART_TIME`
- `CONTRACT`
- `TEMPORARY`

### Experience Levels

- `INTERNSHIP`
- `ENTRY_LEVEL`
- `ASSOCIATE`
- `MID_SENIOR`
- `DIRECTOR`

### Work Arrangement

- `ON_SITE`
- `REMOTE`
- `HYBRID`

### Time Filters

- `DAY` - Posted in last 24 hours
- `WEEK` - Posted in last week
- `MONTH` - Posted in last month
- `ANY` - Any time

### Salary Filters

- `SALARY_40K`, `SALARY_60K`, `SALARY_80K`, `SALARY_100K`
- `SALARY_120K`, `SALARY_140K`, `SALARY_160K`, `SALARY_180K`, `SALARY_200K`

### Relevance

- `RELEVANT` - Most relevant results
- `RECENT` - Most recent results

## Rate Limiting

LinkedIn implements rate limiting. If you encounter "Too many requests (429)" errors:

1. Increase `slow_mo` parameter (try 2.0 or higher)
2. Reduce `max_workers` to 1
3. Use smaller `limit` values in queries
4. Add delays between multiple script runs

## Company-Specific Searches

To search jobs from specific companies:

1. Go to the company's LinkedIn page
2. Click "Jobs" from the left menu
3. Copy the URL from "See all jobs" link
4. Use it in the `company_jobs_url` filter:

```python
query = searcher.create_advanced_query(
    keywords="Engineer",
    company_jobs_url="https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832&geoId=92000000"
)
```

## Output Format

### CSV Output

Jobs are saved with columns:

- job_id, title, company, company_link, location
- description, date, link, apply_link, insights
- scraped_at timestamp

### JSON Output

Jobs are saved as JSON array with full job data including HTML descriptions.

## Troubleshooting

### Common Issues

1. **Chrome/Chromedriver not found**

   - Install Chrome browser
   - Package should handle chromedriver automatically

2. **Authentication required**

   - Set `LI_AT_COOKIE` environment variable
   - Some environments (AWS, Heroku) require authentication

3. **Rate limiting (429 errors)**

   - Increase `slow_mo` parameter
   - Reduce concurrent workers
   - Use smaller search limits

4. **No jobs found**
   - Check if keywords/locations are correct
   - Try broader search terms
   - Verify LinkedIn has jobs for your criteria

### Environment Variables

```bash
# For authenticated sessions
LI_AT_COOKIE=your_linkedin_cookie

# For logging level
LOG_LEVEL=DEBUG
```

## Examples

### Search Tech Jobs

```python
# Search for various tech positions
queries = [
    searcher.create_advanced_query(
        keywords="Frontend Developer",
        locations=["Remote"],
        job_types=["FULL_TIME"],
        work_arrangement=["REMOTE"]
    ),
    searcher.create_advanced_query(
        keywords="Backend Engineer",
        locations=["San Francisco", "Seattle"],
        experience_levels=["MID_SENIOR"],
        salary_base="SALARY_120K"
    )
]
```

### Search by Company

```python
# Get company jobs URL from LinkedIn
google_jobs_url = "https://www.linkedin.com/jobs/search/?f_C=1441&geoId=92000000"

query = searcher.create_advanced_query(
    keywords="Software Engineer",
    company_jobs_url=google_jobs_url,
    limit=50
)
```

## Legal Notice

⚠️ **DISCLAIMER**: This tool is for personal/educational use only. All data extracted is publicly available on LinkedIn and remains owned by LinkedIn. Use responsibly and in accordance with LinkedIn's Terms of Service.
