# LinkedIn Scraper Suite - Streamlit Frontend

A comprehensive web interface for scraping LinkedIn job data and company information with an intuitive workflow.

## 🌟 Features

### Complete Workflow

1. **Job Search** - Search for jobs with advanced filters
2. **Company Selection** - Choose companies from job results
3. **Company Data Extraction** - Scrape detailed company information
4. **Results Analysis** - Analyze and filter all collected data

### Job Search Capabilities

- ✅ Keyword-based job search
- ✅ Multiple location support
- ✅ Advanced filters (experience level, job type, salary, etc.)
- ✅ Relevance and time-based filtering
- ✅ Configurable scraping parameters

### Company Data Extraction

- ✅ Automatic LinkedIn URL generation
- ✅ Detailed company information scraping
- ✅ Industry, size, and founding information
- ✅ Company descriptions and specialties
- ✅ LinkedIn company ID extraction

### Data Management

- ✅ Save to local files (JSON, CSV)
- ✅ Optional Supabase database integration
- ✅ Export functionality for all data
- ✅ Load previously saved results

### Analysis & Filtering

- ✅ Interactive data tables
- ✅ Search and filter capabilities
- ✅ Summary statistics and metrics
- ✅ Combined analysis of jobs and companies
- ✅ Visual charts and insights

## 🚀 Quick Start

### Option 1: Use the Startup Script (Windows)

```bash
# Simply double-click or run:
start_app.bat
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
streamlit run streamlit_app.py
```

## 📋 Prerequisites

### Required Software

- Python 3.7 or higher
- Chrome or Chromium browser
- ChromeDriver (automatically managed)

### Environment Variables (Optional)

For LinkedIn authentication and Supabase integration:

```bash
# Create a .env file with:
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
```

## 🎯 How to Use

### Step 1: Job Search

1. **Set Search Parameters**

   - Enter job keywords (e.g., "Software Engineer", "Data Scientist")
   - Select locations (multiple allowed)
   - Set number of jobs to scrape (5-100)

2. **Configure Advanced Filters** (Optional)

   - Relevance: Recent vs Relevant
   - Time posted: Day, Week, Month, Any
   - Job types: Full-time, Part-time, Contract, Temporary
   - Experience levels: Internship to Director level
   - Work arrangement: On-site, Remote, Hybrid
   - Minimum salary filters

3. **Scraper Settings**

   - Headless mode (recommended)
   - Delay between requests (avoid rate limiting)

4. **Start Search**
   - Click "🚀 Start Job Search"
   - Monitor progress in real-time
   - Results automatically saved to `data/` folder

### Step 2: Job Results & Company Selection

1. **Review Job Results**

   - Summary metrics displayed
   - Filter by company, location, or search terms
   - Browse job listings in table format

2. **Select Companies for Extraction**

   - Choose companies you want detailed data for
   - Use "Select All" for convenience
   - Preview shows company count and names

3. **Save & Proceed**
   - Save selected companies to `company-list.txt`
   - Click "🎯 Extract Company Data" to continue

### Step 3: Company Data Extraction

1. **Configure Extraction**

   - Choose save destinations (Supabase/Local)
   - Set delay between company requests
   - Select extraction mode (single session vs per-company)

2. **Preview Companies**

   - Review companies to be scraped
   - See generated LinkedIn URLs
   - Verify company names are correct

3. **Start Extraction**
   - Click "🚀 Start Company Data Extraction"
   - Monitor progress and logs
   - Results saved automatically

### Step 4: Results Analysis

1. **Company Data Analysis**

   - View summary statistics
   - Filter by industry, company size
   - Switch between Table, Cards, and Detailed views
   - Explore individual company profiles

2. **Job Data Analysis**

   - Analytics charts for top companies/locations
   - Search functionality across all job data
   - Filter and sort capabilities

3. **Combined Analysis**

   - Match companies between job search and company data
   - Industry distribution analysis
   - Comprehensive company profiles with job counts

4. **Export Options**
   - Export all data to timestamped folder
   - Multiple formats: JSON, CSV, TXT
   - Organized file structure for easy sharing

## 📁 Project Structure

```
linkedin-company-scraper/
├── streamlit_app.py           # Main Streamlit application
├── linkedin_job_search.py     # Job search functionality
├── linkedin-company-scraper.py # Company scraping functionality
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── start_app.bat             # Windows startup script
├── company-list.txt          # Selected companies (generated)
├── data/                     # Scraped data storage
│   ├── linkedin_jobs_*.json  # Job search results
│   └── companies_data_*.json # Company data results
└── exports/                  # Exported data archives
    └── export_*/            # Timestamped export folders
```

## ⚙️ Configuration

### Customizing Default Settings

Edit `config.py` to modify:

- Default search parameters
- Location options
- Filter options
- File paths
- Display settings

### Scraper Settings

- **Headless Mode**: Run browser in background (recommended)
- **Slow Mo**: Delay between requests (1.0-3.0 seconds recommended)
- **Max Workers**: Number of concurrent scrapers (keep at 1)
- **Delay Range**: Time between company extractions (3-10 seconds)

## 🔧 Troubleshooting

### Common Issues

1. **"linkedin-jobs-scraper not installed"**

   ```bash
   pip install linkedin-jobs-scraper==5.0.2
   ```

2. **"ChromeDriver not found"**

   - ChromeDriver is automatically downloaded
   - Ensure Chrome browser is installed
   - Check internet connection

3. **Rate Limiting (429 errors)**

   - Increase "Delay Between Requests"
   - Use headless mode
   - Reduce batch size

4. **No companies found**

   - Check company name spelling
   - Verify LinkedIn URLs are accessible
   - Try different search terms

5. **Login Required**
   - Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file
   - Handle security challenges manually when prompted

### Performance Tips

1. **For Large Batches**

   - Use longer delays (5+ seconds)
   - Enable headless mode
   - Process in smaller chunks

2. **Memory Management**

   - Export data regularly
   - Clear session state between runs
   - Monitor system resources

3. **Network Issues**
   - Check internet connectivity
   - Try different times of day
   - Use VPN if blocked

## 🎛️ Advanced Features

### Supabase Integration

1. Set up Supabase project
2. Add environment variables
3. Enable "Save to Supabase" option
4. Data automatically synced to cloud database

### Custom Company URLs

- Modify `company_name_to_linkedin_url()` function
- Add special cases for known companies
- Handle custom URL patterns

### Batch Processing

- Load company lists from files
- Process multiple search queries
- Schedule regular data updates

## 📊 Data Formats

### Job Data Fields

- job_id, title, company, location
- description, date, apply_link
- company_link, insights
- scraped_at timestamp

### Company Data Fields

- name, industry, company_size
- headquarters, founded, website
- about_us, specialties, company_type
- linkedin_url, linkedin_company_id
- scraped_at timestamp

## 🔒 Privacy & Ethics

### Important Notes

- ⚠️ For educational/personal use only
- ⚠️ Respect LinkedIn's robots.txt and terms of service
- ⚠️ Use reasonable delays to avoid overwhelming servers
- ⚠️ Don't share scraped data publicly
- ⚠️ Be mindful of rate limits and IP blocking

### Best Practices

- Use longer delays for large batches
- Don't scrape too frequently
- Respect website terms of service
- Consider using official APIs when available

## 🤝 Contributing

Feel free to:

- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is for educational purposes. Please respect LinkedIn's terms of service and use responsibly.

---

**Happy Scraping! 🚀**
