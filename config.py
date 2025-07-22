# Configuration for LinkedIn Scraper Suite

# Streamlit App Configuration
APP_CONFIG = {
    "page_title": "LinkedIn Scraper Suite",
    "page_icon": "🔍",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Default Search Parameters
DEFAULT_SEARCH = {
    "keywords": "Software Engineer",
    "locations": ["United States", "Remote"],
    "limit": 25,
    "headless": True,
    "slow_mo": 1.0,
}

# Advanced Filter Options
FILTER_OPTIONS = {
    "relevance": ["RECENT", "RELEVANT"],
    "time_filter": ["DAY", "WEEK", "MONTH", "ANY"],
    "job_types": ["FULL_TIME", "PART_TIME", "CONTRACT", "TEMPORARY"],
    "experience_levels": [
        "INTERNSHIP",
        "ENTRY_LEVEL",
        "ASSOCIATE",
        "MID_SENIOR",
        "DIRECTOR",
    ],
    "work_arrangement": ["ON_SITE", "REMOTE", "HYBRID"],
    "salary_base": [
        "None",
        "SALARY_40K",
        "SALARY_60K",
        "SALARY_80K",
        "SALARY_100K",
        "SALARY_120K",
        "SALARY_140K",
        "SALARY_160K",
        "SALARY_180K",
        "SALARY_200K",
    ],
}

# Location Options
LOCATION_OPTIONS = [
    "United States",
    "Remote",
    "San Francisco",
    "New York",
    "Los Angeles",
    "Seattle",
    "Austin",
    "Boston",
    "Chicago",
    "Denver",
    "Europe",
    "Canada",
    "London",
    "Toronto",
    "Berlin",
    "Amsterdam",
    "Paris",
    "Dublin",
    "Switzerland",
]

# File Paths
PATHS = {
    "data_dir": "data",
    "exports_dir": "exports",
    "company_list_file": "company-list.txt",
}

# Scraper Settings
SCRAPER_CONFIG = {
    "delay_range": {"min": 2, "max": 10, "default": 5},
    "extraction_modes": ["single_session", "per_company"],
    "max_workers": 1,
    "page_load_timeout": 40,
}

# Display Settings
DISPLAY_CONFIG = {
    "max_companies_preview": 10,
    "max_description_length": 500,
    "jobs_table_height": 400,
    "companies_table_height": 400,
}

# Database Configuration (Optional)
DATABASE_CONFIG = {
    "use_supabase": False,  # Set to True if you want to use Supabase by default
    "supabase_url_env": "SUPABASE_URL",
    "supabase_key_env": "SUPABASE_SERVICE_ROLE_KEY",
}
