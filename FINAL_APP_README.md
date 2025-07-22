# LinkedIn Job & Company Scraper - Final Version

A comprehensive Streamlit application that combines job searching and company data scraping from LinkedIn into one seamless workflow.

## Features

### 🔍 Job Search

- Advanced LinkedIn job search with multiple filters
- Location, experience level, job type filtering
- Salary range and work arrangement options
- Real-time progress tracking

### 🏢 Company Analysis

- Automated company data scraping
- Industry and company size analysis
- Headquarters and founding information
- Website and specialty extraction

### 📊 Enhanced Analytics

- Interactive data visualizations
- Cross-analysis between jobs and companies
- Company grouping with expandable job listings
- Advanced filtering and search capabilities

### 📤 Multi-Format Export

- JSON and CSV export options
- Combined data export
- Search parameter preservation

## Quick Start

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   Create a `.env` file:

   ```
   LINKEDIN_EMAIL=your_email@example.com
   LINKEDIN_PASSWORD=your_password
   ```

3. **Run the Application**
   ```bash
   streamlit run final_streamlit_app.py
   ```
   Or use the batch file:
   ```bash
   start_app.bat
   ```

## Workflow

### Step 1: Job Search

- Configure search parameters (keywords, locations, filters)
- Execute LinkedIn job scraping
- View real-time progress and results

### Step 2: Company Selection

- Browse jobs grouped by company
- Select companies for detailed scraping
- Use bulk selection options for efficiency

### Step 3: Company Scraping

- Scrape detailed company information
- Monitor progress with real-time updates
- Handle rate limiting automatically

### Step 4: Results Analysis

- **Overview**: Summary metrics and search parameters
- **Company Analysis**: Industry distribution, size analysis, detailed profiles
- **Job Analysis**: Location trends, posting timelines, job descriptions
- **Cross Analysis**: Match jobs with company data for complete insights
- **Export**: Multiple format downloads with combined data options

## Key Improvements

This final version combines the best features from previous iterations:

- **Job Search Engine**: From `streamlit_app.py` - robust job search functionality
- **Company UI**: From `enhanced_streamlit_company_app.py` - enhanced company grouping and selection
- **Data Integration**: From `simplified_scraper.py` - reliable company data extraction
- **Analytics**: Enhanced visualizations and cross-analysis capabilities

## File Structure

```
linkedin-company-scraper/
├── final_streamlit_app.py          # Main application
├── linkedin_job_search.py          # Job search functionality
├── simplified_scraper.py           # Company scraping
├── start_app.bat                   # Windows launcher
├── requirements.txt                # Dependencies
├── .env                           # Environment variables (create this)
├── data/                          # Output directory
│   ├── linkedin_jobs_*.json       # Job search results
│   └── companies/                 # Company data
│       └── companies_data_*.json  # Company scraping results
└── company-list.txt               # Selected companies list
```

## Dependencies

- **Selenium**: Web automation for LinkedIn scraping
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **LinkedIn-Scraper**: LinkedIn company data extraction
- **LinkedIn-Jobs-Scraper**: Job search functionality

## Environment Variables

Set these in your `.env` file:

- `LINKEDIN_EMAIL`: Your LinkedIn email
- `LINKEDIN_PASSWORD`: Your LinkedIn password
- `SUPABASE_URL`: (Optional) For database storage
- `SUPABASE_SERVICE_ROLE_KEY`: (Optional) For database storage

## Usage Tips

1. **Rate Limiting**: The app includes automatic delays to prevent LinkedIn blocking
2. **Data Persistence**: All data is saved locally in JSON format
3. **Resume Workflow**: You can load previous job searches and continue from any step
4. **Bulk Operations**: Use bulk selection for efficient company choosing
5. **Export Options**: Multiple formats available for different use cases

## Troubleshooting

- **Login Issues**: Ensure correct LinkedIn credentials in `.env`
- **Scraping Failures**: Check internet connection and LinkedIn accessibility
- **Memory Issues**: Reduce job limit for large searches
- **Performance**: Enable headless mode for better performance

## Support

For issues or questions, check the logs in the Streamlit interface or review the error messages in the application.
