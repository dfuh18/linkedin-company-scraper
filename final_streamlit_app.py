"""
Final LinkedIn Job & Company Scraper - Streamlit Frontend
Complete workflow: Job Search → Company Selection → Company Data Scraping → Results Analysis
Combines the best features from all previous versions.
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
import time
import subprocess
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Import modules
try:
    from linkedin_job_search import LinkedInJobSearcher
    # Import the robust company scraper functions
    import importlib.util
    spec = importlib.util.spec_from_file_location("linkedin_company_scraper", "linkedin-company-scraper.py")
    linkedin_company_scraper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(linkedin_company_scraper)
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="LinkedIn Job & Company Scraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "step" not in st.session_state:
        st.session_state.step = 1
    if "jobs_data" not in st.session_state:
        st.session_state.jobs_data = []
    if "selected_companies" not in st.session_state:
        st.session_state.selected_companies = []
    if "company_data" not in st.session_state:
        st.session_state.company_data = []
    if "search_params" not in st.session_state:
        st.session_state.search_params = {}


# Helper functions
def save_jobs_data(jobs_data: List[Dict], filename: str = None):
    """Save jobs data to JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_jobs_{timestamp}.json"

    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(jobs_data, f, indent=2, ensure_ascii=False)

    return filepath


def load_saved_jobs():
    """Load the most recent jobs data"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        return None

    json_files = [
        f
        for f in os.listdir(data_dir)
        if f.startswith("linkedin_jobs_") and f.endswith(".json")
    ]
    if not json_files:
        return None

    # Get the most recent file
    latest_file = max(
        json_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x))
    )

    try:
        with open(os.path.join(data_dir, latest_file), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading jobs data: {e}")
        return None


def save_companies_to_file(companies: List[str]):
    """Save selected companies to company-list.txt"""
    with open("company-list.txt", "w", encoding="utf-8") as f:
        for company in companies:
            f.write(f"{company}\n")


def load_company_data():
    """Load the most recent company scraping results"""
    data_dir = "data/companies"
    if not os.path.exists(data_dir):
        return []

    json_files = [
        f
        for f in os.listdir(data_dir)
        if f.endswith(".json") and f.startswith("companies_data_")
    ]

    if not json_files:
        return []

    # Get the most recent file
    latest_file = max(
        json_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x))
    )

    try:
        with open(os.path.join(data_dir, latest_file), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading company data: {e}")
        return []


def run_company_scraper_integrated(companies: List[str]):
    """Run the robust company scraper for selected companies with progressive saving"""
    try:
        # Save companies to file first
        save_companies_to_file(companies)

        # Prepare company URLs (convert company names to LinkedIn URLs)
        company_urls = []
        for company in companies:
            # Use the robust URL conversion function from the main scraper
            linkedin_url = linkedin_company_scraper.company_name_to_linkedin_url(company)
            company_urls.append(linkedin_url)

        # Prepare the progressive save file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data/companies", exist_ok=True)
        progressive_filepath = f"data/companies/companies_data_{timestamp}.json"

        # Use the robust scraper with session recovery and progressive saving
        results = linkedin_company_scraper.scrape_multiple_companies(
            company_urls, 
            delay_range=(3, 6),  # Reasonable delays
            mode="single_session",  # Use single session with recovery
            progressive_save_file=progressive_filepath  # Enable progressive saving
        )

        if results:
            return True, f"Successfully scraped {len(results)} companies with progressive saving to {progressive_filepath}"
        else:
            # Even if no results, check if progressive file has data
            if os.path.exists(progressive_filepath):
                try:
                    with open(progressive_filepath, "r", encoding="utf-8") as f:
                        saved_data = json.load(f)
                    if saved_data:
                        return True, f"Partial success: {len(saved_data)} companies saved to {progressive_filepath}"
                except:
                    pass
            return False, "No companies were successfully scraped"

    except Exception as e:
        return False, f"Error during company scraping: {str(e)}"


# Step 1: Job Search Parameters
def step1_job_search():
    """Step 1: Configure and execute job search"""
    st.title("🔍 Step 1: Job Search Configuration")
    st.markdown("Configure your LinkedIn job search parameters and start scraping.")

    # Main configuration area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Search Parameters")

        # Basic search parameters
        keywords = st.text_input(
            "🔍 Job Keywords",
            value="Python Developer",
            help="Enter job titles, skills, or keywords to search for",
        )

        # Location selection
        locations = st.multiselect(
            "📍 Locations",
            options=[
                "United States",
                "Remote",
                "San Francisco",
                "New York",
                "Los Angeles",
                "Chicago",
                "Boston",
                "Seattle",
                "Austin",
                "Denver",
                "United Kingdom",
                "Canada",
                "Germany",
                "Netherlands",
                "Switzerland",
                "Europe"
            ],
            default=["Europe", "Remote"],
            help="Select one or more locations to search in",
        )

        # Job limit
        limit = st.slider(
            "📊 Number of Jobs to Scrape",
            min_value=5,
            max_value=100,
            value=25,
            step=5,
            help="Number of jobs to scrape (more jobs = longer scraping time)",
        )

        # Advanced filters in expandable section
        with st.expander("🔧 Advanced Filters", expanded=False):
            col_left, col_right = st.columns(2)

            with col_left:
                relevance = st.selectbox(
                    "📈 Sort By",
                    options=["RECENT", "RELEVANT"],
                    index=0,
                    help="Sort jobs by most recent or most relevant",
                )

                time_filter = st.selectbox(
                    "⏰ Posted Time",
                    options=["DAY", "WEEK", "MONTH", "ANY"],
                    index=2,
                    help="Filter by when the job was posted",
                )

                job_types = st.multiselect(
                    "💼 Job Types",
                    options=["FULL_TIME", "PART_TIME", "CONTRACT", "TEMPORARY"],
                    default=["FULL_TIME"],
                    help="Select job types to include",
                )

            with col_right:
                experience_levels = st.multiselect(
                    "🎓 Experience Levels",
                    options=[
                        "INTERNSHIP",
                        "ENTRY_LEVEL",
                        "ASSOCIATE",
                        "MID_SENIOR",
                        "DIRECTOR",
                    ],
                    default=["MID_SENIOR"],
                    help="Select experience levels to include",
                )

                work_arrangement = st.multiselect(
                    "🏠 Work Arrangement",
                    options=["ON_SITE", "REMOTE", "HYBRID"],
                    default=["REMOTE", "HYBRID"],
                    help="Select work arrangements",
                )

                salary_base = st.selectbox(
                    "💰 Minimum Salary",
                    options=[
                        None,
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
                    index=0,
                    help="Filter by minimum base salary",
                )

        # Scraper settings
        with st.expander("⚙️ Scraper Settings", expanded=False):
            col_settings_left, col_settings_right = st.columns(2)

            with col_settings_left:
                headless = st.checkbox(
                    "🕶️ Headless Mode",
                    value=True,
                    help="Run browser in background (recommended for better performance)",
                )

                slow_mo = st.slider(
                    "⏱️ Slow Motion (seconds)",
                    min_value=0.5,
                    max_value=3.0,
                    value=1.0,
                    step=0.1,
                    help="Delay between requests to avoid rate limiting",
                )

    with col2:
        st.subheader("Quick Actions")

        # Load previous job results
        if st.button(
            "📂 Load Previous Job Results",
            help="Load the most recent job search results",
        ):
            saved_jobs = load_saved_jobs()
            if saved_jobs:
                st.session_state.jobs_data = saved_jobs
                st.success(f"✅ Loaded {len(saved_jobs)} jobs from previous search")
                st.session_state.step = 2
                st.rerun()
            else:
                st.warning("No previous job data found")

        # Load previous company data
        if st.button(
            "🏢 Load Previous Company Data", 
            help="Load existing company data for analysis"
        ):
            company_data = load_company_data()
            if company_data:
                st.session_state.company_data = company_data
                st.success(f"✅ Loaded {len(company_data)} companies from previous scraping")
                st.session_state.step = 4
                st.rerun()
            else:
                st.warning("No previous company data found")

        # Search button
        if st.button(
            "🚀 Start Job Search",
            type="primary",
            help="Begin scraping jobs with current parameters",
        ):
            if not keywords.strip():
                st.error("Please enter job keywords")
                return

            if not locations:
                st.error("Please select at least one location")
                return

            # Initialize searcher
            searcher = LinkedInJobSearcher(
                headless=headless, slow_mo=slow_mo, max_workers=1, output_dir="data"
            )

            # Create query
            try:
                query = searcher.create_advanced_query(
                    keywords=keywords,
                    locations=locations,
                    limit=limit,
                    job_types=job_types,
                    experience_levels=experience_levels,
                    time_filter=time_filter,
                    relevance=relevance,
                    work_arrangement=work_arrangement,
                    salary_base=salary_base,
                )

                # Store search parameters
                st.session_state.search_params = {
                    "keywords": keywords,
                    "locations": locations,
                    "limit": limit,
                    "job_types": job_types,
                    "experience_levels": experience_levels,
                    "time_filter": time_filter,
                    "relevance": relevance,
                    "work_arrangement": work_arrangement,
                    "salary_base": salary_base,
                }

                with st.spinner(
                    "Searching LinkedIn jobs... This may take a few minutes."
                ):
                    searcher.search_jobs([query])  # Pass query as a list
                    jobs = searcher.jobs_data  # Get the results from the searcher

                if jobs:
                    st.session_state.jobs_data = jobs
                    st.success(f"✅ Found {len(jobs)} jobs!")

                    # Save jobs data
                    filepath = save_jobs_data(jobs)
                    st.info(f"💾 Jobs saved to {filepath}")

                    # Auto-advance to next step
                    time.sleep(2)
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.warning("No jobs found with current search criteria")

            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")


# Step 2: Job Results and Company Selection (Enhanced with grouping)
def step2_job_results():
    """Step 2: Display job results and allow company selection with enhanced UI"""
    st.title("📊 Step 2: Job Results & Company Selection")

    if not st.session_state.jobs_data:
        st.warning(
            "⚠️ No job data available. Please go back to Step 1 and run a job search."
        )
        if st.button("← Back to Job Search"):
            st.session_state.step = 1
            st.rerun()
        return

    jobs_df = pd.DataFrame(st.session_state.jobs_data)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs", len(jobs_df))
    with col2:
        st.metric(
            "Unique Companies",
            jobs_df["company"].nunique() if "company" in jobs_df.columns else 0,
        )
    with col3:
        st.metric("Selected Companies", len(st.session_state.selected_companies))
    with col4:
        completion = (
            len(st.session_state.selected_companies)
            / jobs_df["company"].nunique()
            * 100
            if "company" in jobs_df.columns and jobs_df["company"].nunique() > 0
            else 0
        )
        st.metric("Selection Progress", f"{completion:.1f}%")

    # Filter section
    st.subheader("🔍 Filter Jobs")
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        company_filter = st.selectbox(
            "Filter by Company",
            (
                ["All"] + sorted(jobs_df["company"].unique())
                if "company" in jobs_df.columns
                else ["All"]
            ),
        )

    with col_filter2:
        location_filter = st.selectbox(
            "Filter by Location",
            (
                ["All"] + sorted(jobs_df["location"].unique())
                if "location" in jobs_df.columns
                else ["All"]
            ),
        )

    with col_filter3:
        title_search = st.text_input(
            "Search Job Titles", placeholder="Enter keywords..."
        )

    # Apply filters
    filtered_df = jobs_df.copy()

    if company_filter != "All":
        filtered_df = filtered_df[filtered_df["company"] == company_filter]

    if location_filter != "All":
        filtered_df = filtered_df[filtered_df["location"] == location_filter]

    if title_search:
        filtered_df = filtered_df[
            filtered_df["title"].str.contains(title_search, case=False, na=False)
        ]

    st.info(f"Showing {len(filtered_df)} of {len(jobs_df)} jobs")

    # Visualizations
    st.subheader("📈 Job Analytics")

    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        # Top companies chart
        if "company" in jobs_df.columns:
            company_counts = jobs_df["company"].value_counts().head(10)
            fig = px.bar(
                x=company_counts.values,
                y=company_counts.index,
                orientation="h",
                title="Top 10 Companies by Job Count",
                labels={"x": "Number of Jobs", "y": "Company"},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with viz_col2:
        # Location distribution
        if "location" in jobs_df.columns:
            location_counts = jobs_df["location"].value_counts().head(10)
            fig = px.pie(
                values=location_counts.values,
                names=location_counts.index,
                title="Job Distribution by Location",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Enhanced Company selection with grouping
    st.subheader("🏢 Select Companies for Detailed Scraping")

    # Bulk selection options
    col_bulk1, col_bulk2, col_bulk3 = st.columns(3)

    with col_bulk1:
        if st.button("Select Top 10 Companies"):
            top_companies = jobs_df["company"].value_counts().head(10).index.tolist()
            st.session_state.selected_companies = list(
                set(st.session_state.selected_companies + top_companies)
            )
            st.rerun()

    with col_bulk2:
        if st.button("Select All Visible"):
            visible_companies = (
                filtered_df["company"].unique().tolist()
                if "company" in filtered_df.columns
                else []
            )
            st.session_state.selected_companies = list(
                set(st.session_state.selected_companies + visible_companies)
            )
            st.rerun()

    with col_bulk3:
        if st.button("Clear Selection"):
            st.session_state.selected_companies = []
            st.rerun()

    # Enhanced company view with job grouping
    st.subheader(f"📋 Companies & Job Listings ({len(filtered_df)} jobs)")

    # Group by company for better organization
    if "company" in filtered_df.columns:
        company_groups = filtered_df.groupby("company")

        for company_name, company_jobs in company_groups:
            is_selected = company_name in st.session_state.selected_companies

            # Company header with selection checkbox
            col_select, col_company_info = st.columns([0.1, 0.9])

            with col_select:
                if st.checkbox(
                    "", value=is_selected, key=f"company_select_{company_name}"
                ):
                    if company_name not in st.session_state.selected_companies:
                        st.session_state.selected_companies.append(company_name)
                        st.rerun()
                else:
                    if company_name in st.session_state.selected_companies:
                        st.session_state.selected_companies.remove(company_name)
                        st.rerun()

            with col_company_info:
                # Company overview with expandable job details
                with st.expander(
                    f"🏢 **{company_name}** ({len(company_jobs)} jobs) {'✅ Selected' if is_selected else ''}",
                    expanded=False,
                ):
                    # Company summary
                    locations = company_jobs["location"].unique()
                    st.write(
                        f"📍 **Locations:** {', '.join(locations[:3])}{' and more...' if len(locations) > 3 else ''}"
                    )

                    # Job listings for this company
                    st.write("**Job Listings:**")
                    for idx, job in company_jobs.iterrows():
                        job_col1, job_col2 = st.columns([3, 1])

                        with job_col1:
                            st.markdown(f"• **{job['title']}** - {job['location']}")
                            if "date" in job and job["date"]:
                                st.markdown(f"  📅 Posted: {job['date']}")

                            # Show job description if available
                            if "description" in job and job["description"]:
                                with st.expander(
                                    f"� Description - {job['title']}", expanded=False
                                ):
                                    st.write(
                                        job["description"][:500] + "..."
                                        if len(job["description"]) > 500
                                        else job["description"]
                                    )

                        with job_col2:
                            if "link" in job and job["link"]:
                                st.link_button("🔗 View Job", job["link"])

    # Navigation
    st.subheader("🎯 Next Steps")
    col_nav1, col_nav2, col_nav3 = st.columns(3)

    with col_nav1:
        if st.button("← Back to Search"):
            st.session_state.step = 1
            st.rerun()

    with col_nav2:
        if st.button(
            "📊 View Current Results",
            disabled=len(st.session_state.selected_companies) == 0,
        ):
            st.session_state.step = 4
            st.rerun()

    with col_nav3:
        if st.button(
            "🚀 Scrape Companies",
            type="primary",
            disabled=len(st.session_state.selected_companies) == 0,
        ):
            st.session_state.step = 3
            st.rerun()


# Step 3: Company Data Scraping (Integrated)
def step3_company_scraping():
    """Step 3: Scrape detailed company data using integrated scraper"""
    st.title("🏢 Step 3: Company Data Scraping")

    if not st.session_state.selected_companies:
        st.warning(
            "⚠️ No companies selected. Please go back to Step 2 and select companies."
        )
        if st.button("← Back to Job Results"):
            st.session_state.step = 2
            st.rerun()
        return

    st.info(
        f"Ready to scrape data for {len(st.session_state.selected_companies)} companies"
    )

    # Display selected companies
    st.subheader("📋 Selected Companies")
    for i, company in enumerate(st.session_state.selected_companies, 1):
        st.write(f"{i}. {company}")

    # Scraping configuration
    st.subheader("⚙️ Scraping Configuration")

    col_config1, col_config2 = st.columns(2)

    with col_config1:
        scrape_limit = st.number_input(
            "Limit Companies (for testing)",
            min_value=1,
            max_value=len(st.session_state.selected_companies),
            value=min(5, len(st.session_state.selected_companies)),
            help="Limit the number of companies to scrape for testing",
        )

    with col_config2:
        delay_seconds = st.slider(
            "Delay Between Companies (seconds)",
            min_value=1,
            max_value=10,
            value=4,
            help="Delay to avoid rate limiting",
        )

    # Start scraping
    if st.button("🚀 Start Company Scraping", type="primary"):
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_container = st.empty()

        try:
            companies_to_scrape = st.session_state.selected_companies[:scrape_limit]
            status_text.text(
                f"Starting scraper for {len(companies_to_scrape)} companies..."
            )

            # Call the integrated scraper
            with st.spinner("Scraping in progress... This may take several minutes."):
                success, message = run_company_scraper_integrated(companies_to_scrape)

            # Clear the spinner and show results
            if success:
                progress_bar.progress(1.0)
                status_text.text("✅ Scraping completed successfully!")

                # Load the scraped data immediately
                st.session_state.company_data = load_company_data()

                with result_container.container():
                    st.success(message)

                    # Show preview if data available
                    if st.session_state.company_data:
                        st.subheader("📊 Preview of Scraped Data")
                        preview_df = pd.DataFrame(st.session_state.company_data)
                        available_cols = [
                            col
                            for col in [
                                "name",
                                "industry",
                                "company_size",
                                "headquarters",
                                "website",
                            ]
                            if col in preview_df.columns
                        ]
                        if available_cols:
                            st.dataframe(preview_df[available_cols].head())

                    # Provide navigation options instead of auto-advance
                    st.info("🎉 Scraping completed! Choose your next step:")
                    
                    col_nav1, col_nav2 = st.columns(2)
                    with col_nav1:
                        if st.button("📊 View Results & Analysis", type="primary", key="goto_analysis"):
                            st.session_state.step = 4
                            st.rerun()
                    
                    with col_nav2:
                        if st.button("🔄 Scrape More Companies", key="scrape_more"):
                            st.session_state.step = 2
                            st.rerun()

            else:
                progress_bar.progress(0.0)
                status_text.text("❌ Scraping failed")
                
                with result_container.container():
                    st.error(f"❌ {message}")
                    
                    # Check if partial data was saved
                    partial_data = load_company_data()
                    if partial_data:
                        st.warning(f"⚠️ Partial data available: {len(partial_data)} companies were saved before the failure.")
                        st.session_state.company_data = partial_data
                        
                        if st.button("📊 View Partial Results", key="view_partial"):
                            st.session_state.step = 4
                            st.rerun()

        except Exception as e:
            progress_bar.progress(0.0)
            status_text.text("❌ Scraping failed with error")
            
            with result_container.container():
                st.error(f"❌ Scraping error: {str(e)}")
                
                # Still check for partial data in case of unexpected errors
                try:
                    partial_data = load_company_data()
                    if partial_data:
                        st.info(f"ℹ️ Found existing data: {len(partial_data)} companies")
                        if st.button("📊 Load Existing Data", key="load_existing"):
                            st.session_state.company_data = partial_data
                            st.session_state.step = 4
                            st.rerun()
                except:
                    pass

    # Navigation
    st.subheader("🎯 Navigation")
    if st.button("← Back to Job Results"):
        st.session_state.step = 2
        st.rerun()


# Step 4: Enhanced Results Analysis
def step4_results_analysis():
    """Step 4: Enhanced analysis and visualization of all scraped data"""
    st.title("📊 Step 4: Results Analysis & Export")

    # Load company data if not in session state
    if not st.session_state.company_data:
        st.session_state.company_data = load_company_data()

        # Debug info for file loading
        data_dir = "data/companies"
        if os.path.exists(data_dir):
            all_files = os.listdir(data_dir)
            company_files = [f for f in all_files if f.endswith(".json")]
            if company_files:
                st.info(
                    f"📁 Found {len(company_files)} company data files: {', '.join(company_files)}"
                )
                latest_file = max(
                    company_files,
                    key=lambda x: os.path.getctime(os.path.join(data_dir, x)),
                )
                st.info(f"📂 Loading from latest file: {latest_file}")
            else:
                st.warning("📁 No JSON files found in data/companies directory")
        else:
            st.warning("📁 data/companies directory does not exist")

    if not st.session_state.jobs_data and not st.session_state.company_data:
        st.warning("⚠️ No data available for analysis.")
        if st.button("← Start Over"):
            st.session_state.step = 1
            st.rerun()
        return

    # Enhanced tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Overview",
            "🏢 Company Analysis",
            "💼 Job Analysis",
            "🔗 Cross Analysis",
            "📤 Export",
        ]
    )

    with tab1:
        st.subheader("📊 Data Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Jobs Scraped", len(st.session_state.jobs_data))

        with col2:
            st.metric("Companies Scraped", len(st.session_state.company_data))

        with col3:
            if st.session_state.jobs_data:
                jobs_df = pd.DataFrame(st.session_state.jobs_data)
                unique_companies = (
                    jobs_df["company"].nunique() if "company" in jobs_df.columns else 0
                )
                st.metric("Unique Job Companies", unique_companies)

        with col4:
            if st.session_state.company_data:
                companies_with_data = sum(
                    1 for c in st.session_state.company_data if c.get("name")
                )
                st.metric("Companies with Full Data", companies_with_data)

        # Search parameters summary
        if st.session_state.search_params:
            with st.expander("🔍 Search Parameters Used", expanded=False):
                params_df = pd.DataFrame([st.session_state.search_params])
                st.dataframe(params_df.T, use_container_width=True)

    with tab2:
        st.subheader("🏢 Enhanced Company Analysis")

        if st.session_state.company_data:
            st.success(
                f"✅ Loaded {len(st.session_state.company_data)} companies from scraped data"
            )
            company_df = pd.DataFrame(st.session_state.company_data)

            # Show a sample of loaded data
            with st.expander("📊 Preview of Loaded Company Data", expanded=False):
                st.write("**Sample companies loaded:**")
                sample_companies = [
                    comp.get("name", "Unknown")
                    for comp in st.session_state.company_data[:5]
                ]
                for i, comp_name in enumerate(sample_companies, 1):
                    st.write(f"{i}. {comp_name}")
                if len(st.session_state.company_data) > 5:
                    st.write(
                        f"... and {len(st.session_state.company_data) - 5} more companies"
                    )

            # Advanced filter options
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                industry_filter = st.multiselect(
                    "Filter by Industry",
                    options=sorted(
                        [
                            i
                            for i in company_df["industry"].unique()
                            if i and str(i) != "nan"
                        ]
                    ),
                    help="Select multiple industries",
                )

            with col_f2:
                size_filter = st.multiselect(
                    "Filter by Company Size",
                    options=sorted(
                        [
                            s
                            for s in company_df["company_size"].unique()
                            if s and str(s) != "nan"
                        ]
                    ),
                    help="Select company sizes",
                )

            with col_f3:
                founded_range = st.slider(
                    "Founded Year Range",
                    min_value=1800,
                    max_value=2025,
                    value=(1990, 2025),
                    help="Filter by founding year",
                )

            # Apply filters
            filtered_company_df = company_df.copy()
            if industry_filter:
                filtered_company_df = filtered_company_df[
                    filtered_company_df["industry"].isin(industry_filter)
                ]
            if size_filter:
                filtered_company_df = filtered_company_df[
                    filtered_company_df["company_size"].isin(size_filter)
                ]

            # Enhanced visualizations
            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                # Industry distribution with enhanced styling
                if "industry" in company_df.columns:
                    industry_counts = company_df["industry"].value_counts().head(15)
                    fig = px.bar(
                        x=industry_counts.values,
                        y=industry_counts.index,
                        orientation="h",
                        title="Companies by Industry",
                        color=industry_counts.values,
                        color_continuous_scale="viridis",
                    )
                    fig.update_layout(height=500, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with viz_col2:
                # Company size distribution
                if "company_size" in company_df.columns:
                    size_counts = company_df["company_size"].value_counts()
                    fig = px.pie(
                        values=size_counts.values,
                        names=size_counts.index,
                        title="Company Size Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)

            # Company details table with search
            st.subheader("📋 Company Details")

            search_company = st.text_input(
                "🔍 Search companies:", placeholder="Company name, industry, etc."
            )

            display_columns = [
                "name",
                "industry",
                "company_size",
                "headquarters",
                "founded",
                "website",
                "about_us",
            ]
            available_columns = [
                col for col in display_columns if col in filtered_company_df.columns
            ]

            display_df = filtered_company_df[available_columns].copy()

            if search_company:
                mask = display_df.apply(
                    lambda row: row.astype(str)
                    .str.contains(search_company, case=False, na=False)
                    .any(),
                    axis=1,
                )
                display_df = display_df[mask]

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.info("No company data available. Please scrape some companies first.")

    with tab3:
        st.subheader("💼 Enhanced Job Analysis")

        if st.session_state.jobs_data:
            jobs_df = pd.DataFrame(st.session_state.jobs_data)

            # Job analytics visualizations
            viz_col1, viz_col2 = st.columns(2)

            with viz_col1:
                # Jobs by location
                if "location" in jobs_df.columns:
                    location_counts = jobs_df["location"].value_counts().head(15)
                    fig = px.bar(
                        x=location_counts.index,
                        y=location_counts.values,
                        title="Jobs by Location",
                        color=location_counts.values,
                        color_continuous_scale="plasma",
                    )
                    fig.update_layout(height=400, xaxis_tickangle=-45, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            with viz_col2:
                # Jobs over time
                if "date" in jobs_df.columns:
                    # Convert date column and create posting timeline
                    jobs_df["date_parsed"] = pd.to_datetime(
                        jobs_df["date"], errors="coerce"
                    )
                    date_counts = (
                        jobs_df["date_parsed"].dt.date.value_counts().sort_index()
                    )

                    fig = px.line(
                        x=date_counts.index,
                        y=date_counts.values,
                        title="Job Postings Over Time",
                        markers=True,
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

            # Job details view with enhanced options
            view_option = st.radio(
                "Select view:",
                ["📊 Summary Table", "📄 Detailed View", "🔍 Job Descriptions"],
                horizontal=True,
            )

            if view_option == "📊 Summary Table":
                summary_columns = ["title", "company", "location", "date", "link"]
                available_summary_cols = [
                    col for col in summary_columns if col in jobs_df.columns
                ]
                st.dataframe(
                    jobs_df[available_summary_cols],
                    use_container_width=True,
                    hide_index=True,
                )

            elif view_option == "📄 Detailed View":
                st.dataframe(jobs_df, use_container_width=True, hide_index=True)

            elif view_option == "🔍 Job Descriptions":
                search_term = st.text_input(
                    "🔍 Search jobs:",
                    placeholder="e.g., Python, Data Scientist, Remote",
                )

                filtered_jobs = jobs_df.copy()
                if search_term:
                    mask = jobs_df["title"].str.contains(
                        search_term, case=False, na=False
                    ) | jobs_df["company"].str.contains(
                        search_term, case=False, na=False
                    )
                    if "description" in jobs_df.columns:
                        mask |= jobs_df["description"].str.contains(
                            search_term, case=False, na=False
                        )
                    filtered_jobs = jobs_df[mask]

                st.write(f"Showing {len(filtered_jobs)} jobs")

                for idx, job in filtered_jobs.iterrows():
                    with st.expander(
                        f"📄 {job['title']} at {job['company']}", expanded=False
                    ):
                        col_info, col_link = st.columns([3, 1])

                        with col_info:
                            st.write(f"📍 **Location:** {job['location']}")
                            if "date" in job:
                                st.write(f"📅 **Posted:** {job['date']}")
                            if "description" in job and job["description"]:
                                st.write("**Description:**")
                                st.write(job["description"])

                        with col_link:
                            if "link" in job and job["link"]:
                                st.link_button("🔗 View Job", job["link"])

        else:
            st.info("No job data available.")

    with tab4:
        st.subheader("🔗 Cross Analysis: Jobs & Companies")

        if st.session_state.jobs_data and st.session_state.company_data:
            jobs_df = pd.DataFrame(st.session_state.jobs_data)
            company_df = pd.DataFrame(st.session_state.company_data)

            # Match companies between job and company data
            job_companies = (
                set(jobs_df["company"].unique())
                if "company" in jobs_df.columns
                else set()
            )
            scraped_companies = (
                set(company_df["name"].unique())
                if "name" in company_df.columns
                else set()
            )

            matched_companies = job_companies & scraped_companies

            st.metric("Companies with Both Job & Company Data", len(matched_companies))

            if matched_companies:
                # Create combined analysis
                st.subheader("📊 Combined Company Analysis")

                # Show companies with both data types
                for company in list(matched_companies)[
                    :10
                ]:  # Limit to top 10 for display
                    with st.expander(
                        f"🏢 {company} - Complete Profile", expanded=False
                    ):
                        col_company, col_jobs = st.columns(2)

                        with col_company:
                            st.write("**Company Information:**")
                            company_info = company_df[
                                company_df["name"] == company
                            ].iloc[0]
                            if "industry" in company_info:
                                st.write(f"🏭 **Industry:** {company_info['industry']}")
                            if "company_size" in company_info:
                                st.write(f"👥 **Size:** {company_info['company_size']}")
                            if "headquarters" in company_info:
                                st.write(f"📍 **HQ:** {company_info['headquarters']}")
                            if "website" in company_info:
                                st.write(f"🌐 **Website:** {company_info['website']}")

                        with col_jobs:
                            st.write("**Available Jobs:**")
                            company_jobs = jobs_df[jobs_df["company"] == company]
                            for _, job in company_jobs.iterrows():
                                st.write(f"• {job['title']} - {job['location']}")

        else:
            st.info("Cross analysis requires both job and company data.")

    with tab5:
        st.subheader("📤 Export Data")

        col_e1, col_e2 = st.columns(2)

        with col_e1:
            st.write("**Company Data Export**")
            if st.session_state.company_data:
                # JSON export
                company_json = json.dumps(
                    st.session_state.company_data, indent=2, ensure_ascii=False
                )
                st.download_button(
                    label="📄 Download Company Data (JSON)",
                    data=company_json,
                    file_name=f"company_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

                # CSV export
                company_df = pd.DataFrame(st.session_state.company_data)
                csv = company_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Company Data (CSV)",
                    data=csv,
                    file_name=f"company_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No company data to export")

        with col_e2:
            st.write("**Job Data Export**")
            if st.session_state.jobs_data:
                # JSON export
                jobs_json = json.dumps(
                    st.session_state.jobs_data, indent=2, ensure_ascii=False
                )
                st.download_button(
                    label="📄 Download Job Data (JSON)",
                    data=jobs_json,
                    file_name=f"job_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )

                # CSV export
                jobs_df = pd.DataFrame(st.session_state.jobs_data)
                csv = jobs_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Job Data (CSV)",
                    data=csv,
                    file_name=f"job_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No job data to export")

        # Combined export
        if st.session_state.jobs_data and st.session_state.company_data:
            st.write("**Combined Export**")
            combined_data = {
                "jobs": st.session_state.jobs_data,
                "companies": st.session_state.company_data,
                "search_params": st.session_state.search_params,
                "export_timestamp": datetime.now().isoformat(),
            }
            combined_json = json.dumps(combined_data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📦 Download Combined Data (JSON)",
                data=combined_json,
                file_name=f"linkedin_complete_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )

    # Navigation
    st.subheader("🎯 Navigation")
    col_nav1, col_nav2, col_nav3 = st.columns(3)

    with col_nav1:
        if st.button("← Back to Scraping"):
            st.session_state.step = 3
            st.rerun()

    with col_nav2:
        if st.button("🔄 Start Over"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                if key.startswith(
                    ("jobs_", "company_", "selected_", "search_", "step")
                ):
                    del st.session_state[key]
            st.session_state.step = 1
            st.rerun()

    with col_nav3:
        if st.button("📊 Refresh Data"):
            st.session_state.company_data = load_company_data()
            st.rerun()


# Main application
def main():
    # Initialize session state
    init_session_state()

    # Enhanced sidebar navigation
    st.sidebar.title("🔍 LinkedIn Scraper")
    st.sidebar.markdown("---")

    # Step indicators with progress
    steps = [
        ("🔍", "Job Search", 1),
        ("📊", "Select Companies", 2),
        ("🏢", "Scrape Data", 3),
        ("📈", "View Results", 4),
    ]

    current_step = st.session_state.step

    st.sidebar.subheader("📋 Workflow Progress")
    for icon, label, step_num in steps:
        if step_num == current_step:
            st.sidebar.markdown(f"**➤ {icon} {label}** (Current)")
        elif step_num < current_step:
            st.sidebar.markdown(f"✅ {icon} {label}")
        else:
            st.sidebar.markdown(f"⏸️ {icon} {label}")

    st.sidebar.markdown("---")

    # Enhanced status panel
    st.sidebar.subheader("📊 Current Status")

    # Status metrics with better formatting
    jobs_count = len(st.session_state.jobs_data)
    companies_selected = len(st.session_state.selected_companies)
    companies_scraped = len(st.session_state.company_data)

    st.sidebar.metric("Jobs Found", jobs_count)
    st.sidebar.metric("Companies Selected", companies_selected)
    st.sidebar.metric("Companies Scraped", companies_scraped)

    # Progress bar
    total_progress = (
        (jobs_count > 0) * 25
        + (companies_selected > 0) * 25
        + (companies_scraped > 0) * 50
    )
    st.sidebar.progress(total_progress / 100)
    st.sidebar.caption(f"Overall Progress: {total_progress}%")

    # Quick navigation
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Quick Navigation")

    if st.sidebar.button("Step 1: Job Search"):
        st.session_state.step = 1
        st.rerun()

    if st.sidebar.button("Step 2: Select Companies", disabled=jobs_count == 0):
        st.session_state.step = 2
        st.rerun()

    if st.sidebar.button("Step 3: Scrape Companies", disabled=companies_selected == 0):
        st.session_state.step = 3
        st.rerun()

    if st.sidebar.button("Step 4: View Results"):
        st.session_state.step = 4
        st.rerun()

    # Quick load options
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Quick Load")
    
    if st.sidebar.button("📊 Load Job Data"):
        saved_jobs = load_saved_jobs()
        if saved_jobs:
            st.session_state.jobs_data = saved_jobs
            st.session_state.step = 2
            st.rerun()
        else:
            st.sidebar.error("No job data found")
    
    if st.sidebar.button("🏢 Load Company Data"):
        company_data = load_company_data()
        if company_data:
            st.session_state.company_data = company_data
            st.session_state.step = 4
            st.rerun()
        else:
            st.sidebar.error("No company data found")

    # App info
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ About")
    st.sidebar.markdown(
        """
        **Final LinkedIn Scraper** combines:
        - 🔍 Advanced job search
        - 🏢 Company data scraping
        - 📊 Enhanced analytics
        - 📤 Multi-format export
        """
    )

    # Main content based on current step
    if current_step == 1:
        step1_job_search()
    elif current_step == 2:
        step2_job_results()
    elif current_step == 3:
        step3_company_scraping()
    elif current_step == 4:
        step4_results_analysis()


if __name__ == "__main__":
    main()
