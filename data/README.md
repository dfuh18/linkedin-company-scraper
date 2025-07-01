# Data Organization

This folder contains organized output from the LinkedIn Company Scraper.

## Folder Structure

### 📁 `companies/`
Contains company data JSON files from scraping runs:
- `companies_data_YYYYMMDD_HHMMSS.json` - Timestamped scraping results
- Each file contains company information including LinkedIn IDs, industry, size, etc.

### 📁 `job_searches/`
Contains job search URL files generated from company data:
- `job_search_url_YYYYMMDD_HHMMSS.txt` - Job search URLs for scraped companies
- URLs are pre-configured with company filters for immediate use

### 📁 `test_outputs/`
Contains test files and experimental outputs:
- `big_tech_jobs_*.txt` - Job searches for well-known tech companies
- `test_job_search_url_*.txt` - Test URLs generated during API testing

## File Usage

### Company Data Files
Use these to:
- Load company information for analysis
- Extract LinkedIn company IDs for job searches
- Track scraping history and progress

### Job Search Files
Use these to:
- Browse jobs at specific companies
- Set up bookmarks for regular monitoring
- Share targeted job search URLs

### Test Output Files
Use these for:
- API testing and development
- Experimenting with different search parameters
- Validating functionality

## Latest Files

To find the most recent data:
```bash
# Most recent company data
ls -la data/companies/ | tail -1

# Most recent job search URLs  
ls -la data/job_searches/ | tail -1
```

## Integration with Scripts

The main scraper automatically saves to:
- Company data: `data/companies/companies_data_YYYYMMDD_HHMMSS.json`
- Job URLs: `data/job_searches/job_search_url_YYYYMMDD_HHMMSS.txt`

Test scripts look for files in:
- `data/companies/` for loading company data
- All folders for comprehensive testing
