import os
import time
import random
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_scraper import Company, actions
import asyncio
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()


def make_driver(headless: bool = False, implicit_wait: int = 5) -> webdriver.Chrome:
    """Return a configured Chrome WebDriver with enhanced stealth."""
    opts = webdriver.ChromeOptions()

    if headless:
        opts.add_argument("--headless=new")

    # Enhanced stealth options
    opts.add_argument("--disable-gpu")
    opts.add_argument("--log-level=3")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-plugins")
    opts.add_argument("--disable-images")  # Faster loading
    opts.add_argument("--disable-javascript")  # May help with detection
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Remove automation indicators
    opts.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"]
    )
    opts.add_experimental_option("useAutomationExtension", False)

    # Add prefs to appear more human-like
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2  # Block notifications
        }
    }
    opts.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )
        driver.implicitly_wait(implicit_wait)

        # Execute stealth scripts
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})"
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})"
        )

        print("✅ Driver created with stealth configuration")
        return driver

    except Exception as e:
        print(f"❌ Driver creation failed: {e}")
        print("💡 Trying basic configuration...")

        # Fallback to basic configuration
        basic_opts = webdriver.ChromeOptions()
        if headless:
            basic_opts.add_argument("--headless=new")
        basic_opts.add_argument("--disable-gpu")
        basic_opts.add_argument("--no-sandbox")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=basic_opts
        )
        driver.implicitly_wait(implicit_wait)
        return driver


def maybe_login(driver):
    """Log in with environment-variable creds if not already signed in."""
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        raise RuntimeError("Set LINKEDIN_EMAIL / LINKEDIN_PASSWORD env vars")

    print(
        f"🔐 Logging in as {email[:5]}...@{email.split('@')[1] if '@' in email else 'unknown'}"
    )

    try:
        actions.login(driver, email, password)
        time.sleep(random.uniform(3, 5))  # human-like pause

        # Check for security challenge
        current_url = driver.current_url
        page_source = driver.page_source.lower()

        if (
            "challenge" in current_url
            or "verification" in current_url
            or "security" in page_source
        ):
            print("⚠️  Security challenge detected!")
            print("🔍 Current URL:", current_url)

            if "email" in page_source and "verification" in page_source:
                print(
                    "📧 Email verification detected - waiting 30 seconds for auto-completion..."
                )
                time.sleep(30)
            elif "phone" in page_source and "verification" in page_source:
                print(
                    "📱 Phone verification detected - waiting 30 seconds for auto-completion..."
                )
                time.sleep(30)
            else:
                print(
                    "🤖 Bot detection / CAPTCHA challenge detected - waiting 30 seconds..."
                )
                time.sleep(30)

            # Check status after wait
            time.sleep(2)
            current_url = driver.current_url
            if "feed" in current_url or "in.linkedin.com" in current_url:
                print("✅ Challenge appears to be resolved!")
            else:
                print("⚠️  Challenge may still be active, continuing anyway...")

        # Add automatic 2 second delay after login
        print("⏳ Waiting 2 seconds after login...")
        time.sleep(2)

        # Final check
        current_url = driver.current_url
        if (
            "feed" in current_url
            or "mynetwork" in current_url
            or "linkedin.com/in/" in current_url
        ):
            print("✅ Login successful!")
        else:
            print(f"⚠️  Login status unclear. Current URL: {current_url}")
            print("🚀 Continuing with scraping anyway...")

    except Exception as e:
        print(f"❌ Login error: {e}")
        print("🔍 Current URL:", driver.current_url)
        print("🚀 Continuing with scraping despite login issues...")


def scrape_company(company_url: str, driver=None):
    """Scrape company information from LinkedIn."""
    driver_created = False

    try:
        if driver is None:
            # Only create a new driver if none is provided (for standalone usage)
            driver = make_driver(headless=False)
            driver_created = True
            maybe_login(driver)

        print(f"🔍 Scraping company: {company_url}")

        # Create Company object and scrape data (disable employee scraping to avoid timeout)
        company = Company(company_url, driver=driver, scrape=False)

        # Extract LinkedIn company ID from page source BEFORE scraping
        linkedin_company_id = None
        try:
            import re

            page_source = driver.page_source

            # Method 1: Look for "company":{"entityUrn":"urn:li:fsd_company:XXXXX"
            id_match = re.search(r'"entityUrn":"urn:li:fsd_company:(\d+)"', page_source)
            if id_match:
                linkedin_company_id = id_match.group(1)
                print(f"✅ Found company ID (method 1): {linkedin_company_id}")
            else:
                # Method 2: Look for company ID in other patterns
                id_match = re.search(r'"companyId":(\d+)', page_source)
                if id_match:
                    linkedin_company_id = id_match.group(1)
                    print(f"✅ Found company ID (method 2): {linkedin_company_id}")
                else:
                    # Method 3: Look for companyUrn patterns
                    id_match = re.search(
                        r'"companyUrn":"urn:li:company:(\d+)"', page_source
                    )
                    if id_match:
                        linkedin_company_id = id_match.group(1)
                        print(f"✅ Found company ID (method 3): {linkedin_company_id}")
                    else:
                        # Method 4: Look for organization ID
                        id_match = re.search(r'"organizationId":(\d+)', page_source)
                        if id_match:
                            linkedin_company_id = id_match.group(1)
                            print(
                                f"✅ Found company ID (method 4): {linkedin_company_id}"
                            )
                        else:
                            print("⚠️  Company ID not found in page source")
        except Exception as e:
            print(f"⚠️  Could not extract company ID: {e}")

        # Now scrape the company data
        company.scrape(get_employees=False)

        # Extract company information
        company_data = {
            "name": getattr(company, "name", None),
            "about_us": getattr(company, "about_us", None),
            "website": getattr(company, "website", None),
            "industry": getattr(company, "industry", None),
            "company_size": getattr(company, "company_size", None),
            "headquarters": getattr(company, "headquarters", None),
            "founded": getattr(company, "founded", None),
            "specialties": getattr(company, "specialties", []),
            "company_type": getattr(company, "company_type", None),
            "linkedin_url": company_url,
            "linkedin_company_id": linkedin_company_id,
            "scraped_at": datetime.now().isoformat(),
        }

        # Debug: Print key information
        print(f"✅ Successfully scraped: {company_data['name']}")
        print(f"   LinkedIn ID: {linkedin_company_id}")
        print(f"   Industry: {company_data['industry']}")
        print(f"   Size: {company_data['company_size']}")

        return company_data

    except Exception as e:
        print(f"❌ Error scraping {company_url}: {str(e)}")
        print(f"   Error type: {type(e)}")
        import traceback

        print(f"   Full traceback: {traceback.format_exc()}")
        return None

    finally:
        # Only close driver if we created it (for standalone usage)
        if driver_created and driver:
            driver.quit()


def scrape_multiple_companies(
    company_urls: list, delay_range=(2, 5), mode="single_session"
):
    """
    Scrape multiple companies with different session modes.

    Args:
        company_urls: List of LinkedIn company URLs to scrape
        delay_range: Tuple of min/max seconds to wait between requests
        mode: Either "single_session" or "per_company"
    """
    results = []

    if mode == "per_company":
        return scrape_multiple_companies_per_session(company_urls, delay_range)

    # Single session mode with recovery
    driver = None

    try:
        # Create a single driver instance for all companies
        print("🚀 Creating driver and logging in...")
        driver = make_driver(headless=False)
        maybe_login(driver)
        print("✅ Login successful, starting batch scraping...")

        for i, url in enumerate(company_urls):
            print(f"\nProcessing company {i+1}/{len(company_urls)}: {url}")

            try:
                # Check if driver session is still valid before scraping
                try:
                    # Test the session by checking current URL
                    current_url = driver.current_url
                    print(f"   ✅ Session active: {current_url[:50]}...")
                except Exception as session_error:
                    print(f"⚠️  Session invalid, creating new driver: {session_error}")
                    # Close the old driver and create a new one
                    try:
                        driver.quit()
                    except:
                        pass

                    # Create new driver and login
                    print("🔄 Creating new driver and logging in...")
                    driver = make_driver(headless=False)
                    maybe_login(driver)
                    print("✅ New session established")

                # Use the existing/new driver for scraping
                company_data = scrape_company(url, driver)

                if company_data:
                    results.append(company_data)
                    print(f"✅ Successfully scraped: {company_data.get('name', 'Unknown')}")
                else:
                    print(f"❌ Failed to scrape data for {url}")

            except Exception as e:
                print(f"❌ Error processing {url}: {str(e)}")
                # Try to recover by creating a new driver for next iteration
                try:
                    driver.quit()
                except:
                    pass
                driver = None
                continue

            # Add random delay between requests (except for last item)
            if i < len(company_urls) - 1:
                delay = random.uniform(*delay_range)
                print(f"⏳ Waiting {delay:.1f} seconds before next request...")
                time.sleep(delay)

    except Exception as e:
        print(f"❌ Critical error in batch scraping: {str(e)}")

    finally:
        # Close the driver only once at the end
        if driver:
            try:
                print("🔄 Closing driver...")
                driver.quit()
            except Exception as e:
                print(f"⚠️  Error closing driver: {e}")

    return results


def scrape_multiple_companies_per_session(company_urls: list, delay_range=(2, 5)):
    """Scrape multiple companies with a new driver session for each company (legacy mode)."""
    results = []

    for i, url in enumerate(company_urls):
        print(f"Processing company {i+1}/{len(company_urls)}")

        # Create a fresh driver for each company to avoid session issues
        driver = make_driver(headless=False)

        try:
            maybe_login(driver)
            company_data = scrape_company(url, driver)

            if company_data:
                results.append(company_data)
                print(f"✅ Successfully scraped: {company_data.get('name', 'Unknown')}")

        finally:
            # Always close the driver after each company
            try:
                driver.quit()
            except:
                pass

        # Add random delay between requests (except for last item)
        if i < len(company_urls) - 1:
            delay = random.uniform(*delay_range)
            print(f"Waiting {delay:.1f} seconds before next request...")
            time.sleep(delay)

    return results


def save_to_json(data, filename="companies_data.json"):
    """Save scraped data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Data saved to {filename}")


def company_name_to_linkedin_url(company_name):
    """Convert a company name to LinkedIn company URL format."""
    # Convert company name to LinkedIn URL format
    # LinkedIn URLs use lowercase, replace spaces with dashes, remove special characters
    url_name = company_name.lower()

    # Handle special cases for known companies
    special_cases = {
        "meta": "meta",
        "alphabet": "google",
        "microsoft": "microsoft",
        "alibaba group": "alibaba",
        "hp inc.": "hp",
        "general motors": "general-motors",
        "mckinsey & company": "mckinsey-and-company",
        "samsung electronics": "samsung-electronics",
        "volkswagen group": "volkswagen-group",
        "unity technologies": "unity-technologies-sf",
        "fisker inc.": "fisker-automotive",
        "anduril industries": "anduril",
        "coupa software": "coupa-software",
        "scale ai": "scaleapi",
        "hugging face": "huggingface",
    }

    if url_name in special_cases:
        url_name = special_cases[url_name]
    else:
        # General conversion rules
        url_name = re.sub(r"[&]", "and", url_name)  # Replace & with and
        url_name = re.sub(
            r"[^\w\s-]", "", url_name
        )  # Remove special characters except spaces and dashes
        url_name = re.sub(r"\s+", "-", url_name)  # Replace spaces with dashes
        url_name = re.sub(
            r"-+", "-", url_name
        )  # Replace multiple dashes with single dash
        url_name = url_name.strip("-")  # Remove leading/trailing dashes

    return f"https://www.linkedin.com/company/{url_name}"


def read_companies_from_file(filename):
    """Read company names from a text file and convert to LinkedIn URLs."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            companies = []
            for line in file:
                company_name = line.strip()
                if company_name:  # Skip empty lines
                    linkedin_url = company_name_to_linkedin_url(company_name)
                    companies.append({"name": company_name, "url": linkedin_url})
            return companies
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return []
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []


def scrape_companies_from_file(filename, max_companies=None, delay_range=(3, 7)):
    """Scrape companies from a file with company names."""
    companies = read_companies_from_file(filename)

    if not companies:
        print("No companies found in file")
        return []

    print(f"Found {len(companies)} companies in {filename}")

    # Limit number of companies if specified
    if max_companies:
        companies = companies[:max_companies]
        print(f"Limiting to first {max_companies} companies")

    # Extract just the URLs for scraping
    company_urls = [company["url"] for company in companies]

    # Print the URLs that will be scraped
    print("\n=== URLS TO SCRAPE ===")
    for i, company in enumerate(companies):
        print(f"{i+1:2d}. {company['name']} -> {company['url']}")

    print(f"\nStarting to scrape {len(company_urls)} companies...")

    # Use existing scraping function with longer delays for large batches
    return scrape_multiple_companies(company_urls, delay_range)


def verify_linkedin_url_with_gemini(company_name):
    """Use Gemini with Google Search to verify/find the correct LinkedIn URL"""
    try:
        from google import genai
        from google.genai import types

        # Configure the client
        client = genai.Client()

        # Define the grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        # Configure generation settings
        config = types.GenerateContentConfig(tools=[grounding_tool])

        prompt = f"""Find the official LinkedIn company page for "{company_name}".
        
Return only the exact LinkedIn URL in this format: https://www.linkedin.com/company/[slug]
If not found, return: NOT_FOUND"""

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=config,
        )

        response_text = response.text.strip()

        # Extract LinkedIn URL
        import re

        linkedin_pattern = r"https://www\.linkedin\.com/company/[a-zA-Z0-9\-_]+"
        urls = re.findall(linkedin_pattern, response_text)

        if urls:
            return urls[0]
        elif "NOT_FOUND" in response_text.upper():
            return None
        else:
            return None

    except ImportError:
        print(f"⚠️  Gemini not available for {company_name}, using generated URL")
        return None
    except Exception as e:
        print(f"⚠️  Gemini error for {company_name}: {e}")
        return None


def read_companies_with_verification(filename, use_gemini=True, max_companies=None):
    """Read companies and optionally verify URLs with Gemini"""
    companies = read_companies_from_file(filename)

    if not companies:
        return []

    if max_companies:
        companies = companies[:max_companies]

    print(f"📋 Processing {len(companies)} companies...")

    verified_companies = []

    for i, company_name in enumerate(companies):
        print(f"{i+1:2d}/{len(companies)} Processing: {company_name}")

        # Generate default URL
        default_url = company_name_to_linkedin_url(company_name)

        if use_gemini:
            # Try to verify with Gemini
            print(f"    🔍 Verifying with Gemini...")
            verified_url = verify_linkedin_url_with_gemini(company_name)

            if verified_url:
                print(f"    ✅ Verified: {verified_url}")
                final_url = verified_url
            else:
                print(f"    ⚠️  Using generated: {default_url}")
                final_url = default_url

            # Add delay to respect rate limits
            if i < len(companies) - 1:
                time.sleep(2)  # 2 second delay between Gemini requests
        else:
            final_url = default_url
            print(f"    📎 Generated: {final_url}")

        verified_companies.append(
            {
                "name": company_name,
                "url": final_url,
                "verified": use_gemini and verified_url is not None,
            }
        )

    return verified_companies


def scrape_companies_with_gemini_verification(
    filename, max_companies=None, use_gemini=True
):
    """Enhanced scraping with optional Gemini verification using single driver session"""

    print("🚀 LinkedIn Scraper with Gemini Verification")
    print("=" * 50)

    # Get companies with verification
    companies = read_companies_with_verification(filename, use_gemini, max_companies)

    if not companies:
        print("❌ No companies to process")
        return []

    # Show summary
    verified_count = sum(1 for c in companies if c.get("verified", False))
    print(f"\n📊 Summary:")
    print(f"   Total companies: {len(companies)}")
    if use_gemini:
        print(f"   Gemini verified: {verified_count}")
        print(f"   Generated URLs: {len(companies) - verified_count}")

    # Extract URLs for scraping
    company_urls = [company["url"] for company in companies]

    print(f"\n🎯 URLs to scrape:")
    for i, company in enumerate(companies):
        status = "✅" if company.get("verified") else "📎"
        print(f"  {i+1:2d}. {status} {company['name']} -> {company['url']}")

    # Proceed with scraping using single driver session
    print(f"\n🚀 Starting scraper with single session...")
    results = scrape_multiple_companies(company_urls, delay_range=(4, 8))

    return results


def main():
    """Main function to demonstrate company scraping."""
    import argparse

    # Set up argument parser
    parser = argparse.ArgumentParser(description="LinkedIn Company Scraper")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=3,
        help="Number of companies to process (default: 3)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        help="Delay between requests in seconds (default: 5)",
    )
    parser.add_argument(
        "--use-gemini", action="store_true", help="Use Gemini for URL verification"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="company-list.txt",
        help="Input file with company names",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["single_session", "per_company"],
        default="single_session",
        help="Session mode: single_session (reuse driver) or per_company (new driver each time)",
    )

    args = parser.parse_args()

    print("LinkedIn Company Scraper")
    print("=" * 50)

    filename = args.file
    batch_size = args.batch_size
    use_gemini = args.use_gemini
    mode = args.mode

    print(f"Session mode: {mode}")

    try:
        # Read companies from file
        companies = read_companies_from_file(filename)
        if not companies:
            print("No companies found in file")
            return

        print(f"Found {len(companies)} companies in {filename}")

        # Use specified batch size
        test_companies = companies[:batch_size]
        company_urls = [company["url"] for company in test_companies]

        print(f"\nTesting with first {batch_size} companies:")
        for i, company in enumerate(companies[:batch_size]):
            print(f"{i+1}. {company['name']} -> {company['url']}")

        print(f"\nStarting to scrape {len(company_urls)} companies in {mode} mode...")

        # Scrape companies with user-specified delays and mode
        results = scrape_multiple_companies(
            company_urls, delay_range=(args.delay, args.delay + 2), mode=mode
        )

    except Exception as e:
        print(f"Error: {e}")
        return

    # Process results
    if results:
        # Save results to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/companies/companies_data_{timestamp}.json"
        save_to_json(results, filename)

        print(f"\n✅ Scraping completed! Processed {len(results)} companies.")
        print(f"📁 Data saved to: {filename}")

        # Print company IDs summary
        print("\n=== SCRAPED COMPANY SUMMARY ===")
        company_ids = []
        successful_companies = []

        for company in results:
            name = company.get("name", "Unknown")
            company_id = company.get("linkedin_company_id", "NOT FOUND")
            industry = company.get("industry", "Unknown")
            size = company.get("company_size", "Unknown")

            print(f"{name:25s}: {company_id}")
            print(f"{'':25s}  Industry: {industry}")
            print(f"{'':25s}  Size: {size}")
            print()

            if company_id and company_id != "NOT FOUND":
                company_ids.append(company_id)
                successful_companies.append(name)

        # Summary for integration with job search tools
        if company_ids:
            print(f"✅ Successfully extracted {len(company_ids)} company IDs")
            print(f"🔗 Company IDs: {', '.join(company_ids)}")
            print(f"� These IDs can be used with job search tools")
        else:
            print(
                "❌ No company IDs found. Check the company URLs or LinkedIn page structure."
            )
    else:
        print("\n❌ No companies were successfully scraped.")

    print(
        f"\n💡 To scrape more companies, use --batch-size parameter (e.g., --batch-size 10 or --batch-size 20)"
    )


if __name__ == "__main__":
    main()
