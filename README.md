# LinkedIn Company Scraper

A focused Python tool that extracts comprehensive company information from LinkedIn company pages. Built for researchers, analysts, and developers who need structured company data.

## 🎯 Features

- **Comprehensive Data Extraction**: Company name, industry, size, headquarters, specialties, and more
- **Batch Processing**: Scrape multiple companies with intelligent rate limiting
- **Company Name Input**: Provide company names and get LinkedIn URLs automatically
- **LinkedIn ID Extraction**: Get company IDs for integration with job search tools
- **Organized Output**: Clean JSON files with timestamped data
- **Optional Integrations**: Supabase database storage and Gemini URL verification
- **Stealth Mode**: Enhanced browser configuration to avoid detection

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the `.env.example` template:
   ```bash
   cp .env.example .env
   ```

4. Configure your LinkedIn credentials in the `.env` file:
   ```
   LINKEDIN_EMAIL=your_linkedin_email@example.com
   LINKEDIN_PASSWORD=your_linkedin_password
   ```

5. (Optional) Configure Supabase for database storage:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   ```

## 🚀 Quick Start

### Basic Scraping (Company Names)

1. Add company names to `company-list.txt`:
   ```
   Microsoft
   Google
   Apple
   Meta
   ```

2. Run the scraper:
   ```bash
   python linkedin-company-scraper.py --batch-size 5
   ```

### Command Line Options

```bash
# Scrape first 10 companies with 3-second delays
python linkedin-company-scraper.py --batch-size 10 --delay 3

# Use Gemini for URL verification
python linkedin-company-scraper.py --use-gemini --batch-size 5

# Use per-company session mode (slower but more reliable)
python linkedin-company-scraper.py --mode per_company --batch-size 3
```

### Basic Usage Example

```python
from linkedin_company_scraper import scrape_company

# Scrape a single company
company_data = scrape_company("https://www.linkedin.com/company/microsoft")
print(f"Company: {company_data['name']}")
print(f"Industry: {company_data['industry']}")
print(f"LinkedIn ID: {company_data['linkedin_company_id']}")
```

## 📊 Data Extracted

The scraper extracts comprehensive company information:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Company name | "Microsoft" |
| `linkedin_company_id` | LinkedIn company ID | "1035" |
| `industry` | Business industry | "Software Development" |
| `company_size` | Employee count range | "10,001+ employees" |
| `about_us` | Company description | "Technology company..." |
| `website` | Official website | "https://microsoft.com" |
| `headquarters` | HQ location | "Redmond, Washington" |
| `founded` | Year founded | "1975" |
| `specialties` | Key business areas | "Cloud, AI, Productivity" |
| `company_type` | Organization type | "Public Company" |
| `linkedin_url` | LinkedIn page URL | "https://linkedin.com/company/microsoft" |
| `scraped_at` | Timestamp | "2025-06-30T19:04:52" |

## 📁 Output Structure

The scraper creates organized output files:

```
data/
├── companies/
│   ├── companies_data_20250630_190452.json    # Timestamped scraping results
│   └── companies_data_20250630_120000.json    # Previous runs
└── README.md                                   # Data documentation
```

### Sample Output
```json
[
  {
    "name": "Microsoft",
    "linkedin_company_id": "1035",
    "industry": "Software Development",
    "company_size": "10,001+ employees",
    "website": "https://microsoft.com",
    "about_us": "Microsoft is a technology company...",
    "linkedin_url": "https://linkedin.com/company/microsoft",
    "scraped_at": "2025-06-30T19:04:52"
  }
]
```

### Company IDs for Integration
The scraper extracts LinkedIn company IDs that can be used with:
- Job search APIs
- LinkedIn marketing tools  
- Business intelligence platforms
- Custom analytics dashboards

## ⚙️ Configuration Options

### Session Modes
- **`single_session`** (default): Reuse browser session for all companies (faster)
- **`per_company`**: New browser session per company (more reliable)

### Rate Limiting
- Configurable delays between requests (default: 2-5 seconds)
- Human-like pauses and randomization
- Automatic session recovery

### Optional Integrations
- **Gemini API**: Verify LinkedIn URLs before scraping
- **Supabase**: Store data in PostgreSQL database
- **Custom Input**: Use company names instead of URLs

## 🔧 Requirements

- **Python 3.7+**
- **Google Chrome browser** (ChromeDriver managed automatically)
- **LinkedIn account** with valid credentials
- **Internet connection**

### Dependencies
All Python dependencies are listed in `requirements.txt`:
- `selenium` - Web automation
- `linkedin-scraper` - LinkedIn page parsing
- `python-dotenv` - Environment configuration
- `supabase` - Optional database integration
- `webdriver-manager` - Automatic ChromeDriver management

## Database Schema

If using Supabase, create a `companies` table with the following columns:

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name TEXT,
    about_us TEXT,
    website TEXT,
    industry TEXT,
    company_size TEXT,
    headquarters TEXT,
    founded TEXT,
    specialties TEXT[],
    company_type TEXT,
    linkedin_url TEXT UNIQUE,
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## ⚠️ Important Notes

### Legal & Ethical Use
- **LinkedIn Terms**: Ensure compliance with LinkedIn's Terms of Service
- **Rate Limiting**: Respect LinkedIn's servers with reasonable delays
- **Account Safety**: Consider using a dedicated LinkedIn account
- **Data Privacy**: Handle scraped data responsibly

### Technical Considerations
- **Detection Avoidance**: Built-in stealth features to minimize detection
- **Session Management**: Automatic recovery from login challenges
- **Error Handling**: Robust error handling for network issues
- **Data Validation**: Verification of extracted company information

## 🤝 Integration with Job Search Tools

This scraper is designed to work seamlessly with job search tools:

```python
# Load company data
import json
with open('data/companies/companies_data_latest.json') as f:
    companies = json.load(f)

# Extract company IDs for job searches
company_ids = [c['linkedin_company_id'] for c in companies if c['linkedin_company_id']]
print(f"Ready for job search: {company_ids}")
```

## 🛠️ Development

### Project Structure
```
linkedin-company-scraper/
├── linkedin-company-scraper.py     # Main application
├── requirements.txt                # Python dependencies
├── company-list.txt               # Input company names
├── .env.example                   # Configuration template
├── data/                         # Output directory
├── gemini_linkedin_finder.py     # Optional Gemini integration
└── README.md                     # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **ChromeDriver Issues**: The script automatically manages ChromeDriver, but ensure Chrome browser is installed.

2. **Login Issues**: Verify your LinkedIn credentials in the `.env` file.

3. **Rate Limiting**: If you encounter rate limiting, increase the delay between requests:
   ```python
   results = scrape_multiple_companies(company_urls, delay_range=(5, 10))
   ```

4. **Element Not Found**: LinkedIn occasionally changes their page structure. The `linkedin_scraper` package may need updates.

## License

This project is for educational purposes. Please respect LinkedIn's Terms of Service and applicable laws.
