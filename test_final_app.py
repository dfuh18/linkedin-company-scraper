"""
Quick test script for the final Streamlit app functionality
"""

import json
import os
from datetime import datetime


def test_company_data_structure():
    """Test if company data files can be loaded properly"""
    data_dir = "data/companies"

    if not os.path.exists(data_dir):
        print("❌ data/companies directory not found")
        return False

    json_files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

    if not json_files:
        print("❌ No JSON files found in data/companies")
        return False

    print(f"📁 Found {len(json_files)} JSON files:")
    for file in json_files:
        print(f"  - {file}")

    # Test loading the most recent file
    latest_file = max(
        json_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x))
    )
    print(f"📂 Testing latest file: {latest_file}")

    try:
        with open(os.path.join(data_dir, latest_file), "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"✅ Successfully loaded {len(data)} companies")

        if data:
            print("📊 Sample company data structure:")
            sample = data[0]
            for key, value in sample.items():
                print(f"  {key}: {type(value).__name__}")

        return True

    except Exception as e:
        print(f"❌ Error loading {latest_file}: {e}")
        return False


def test_simplified_scraper_import():
    """Test if simplified scraper can be imported"""
    try:
        from simplified_scraper import scrape_companies_from_list

        print("✅ simplified_scraper import successful")
        return True
    except Exception as e:
        print(f"❌ simplified_scraper import failed: {e}")
        return False


def test_linkedin_job_search_import():
    """Test if LinkedIn job searcher can be imported"""
    try:
        from linkedin_job_search import LinkedInJobSearcher

        print("✅ linkedin_job_search import successful")
        return True
    except Exception as e:
        print(f"❌ linkedin_job_search import failed: {e}")
        return False


def main():
    print("🧪 Testing Final Streamlit App Components")
    print("=" * 50)

    all_passed = True

    tests = [
        ("Company Data Structure", test_company_data_structure),
        ("Simplified Scraper Import", test_simplified_scraper_import),
        ("LinkedIn Job Search Import", test_linkedin_job_search_import),
    ]

    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        result = test_func()
        all_passed = all_passed and result

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Final app should work correctly.")
    else:
        print("❌ Some tests failed. Check the issues above.")

    return all_passed


if __name__ == "__main__":
    main()
