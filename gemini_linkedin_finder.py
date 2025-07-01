#!/usr/bin/env python3
"""
LinkedIn URL finder using Gemini with Google Search
"""

from google import genai
from google.genai import types
import re
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def setup_gemini_client():
    """Setup Gemini client with Google Search capability"""
    try:
        # Configure the client
        client = genai.Client()
        
        # Define the grounding tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        # Configure generation settings
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        
        return client, config
    except Exception as e:
        print(f"Error setting up Gemini client: {e}")
        return None, None

def find_linkedin_url_with_gemini(company_name, client, config):
    """Use Gemini with Google Search to find the correct LinkedIn URL for a company"""
    
    prompt = f"""Find the official LinkedIn company page URL for "{company_name}". 
    
    Please search for the company's LinkedIn page and return ONLY the URL in this exact format:
    https://www.linkedin.com/company/[company-slug]
    
    If you find multiple results, return the main company page (not subsidiaries or regional offices).
    If no LinkedIn page is found, return "NOT_FOUND"
    
    Just return the URL, nothing else."""
    
    try:
        # Make the request
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=config,
        )
        
        # Extract LinkedIn URL from response
        response_text = response.text.strip()
        
        # Look for LinkedIn URL in the response
        linkedin_url_pattern = r'https://www\.linkedin\.com/company/[a-zA-Z0-9\-_]+'
        urls = re.findall(linkedin_url_pattern, response_text)
        
        if urls:
            return urls[0]  # Return the first valid LinkedIn URL found
        elif "NOT_FOUND" in response_text.upper():
            return None
        else:
            # If no URL pattern found, try to extract from text
            lines = response_text.split('\n')
            for line in lines:
                if 'linkedin.com/company/' in line.lower():
                    # Extract URL from line
                    match = re.search(linkedin_url_pattern, line)
                    if match:
                        return match.group(0)
            
            return None
            
    except Exception as e:
        print(f"Error with Gemini search for {company_name}: {e}")
        return None

def verify_and_find_linkedin_urls(company_names, max_requests_per_minute=10):
    """Verify LinkedIn URLs for a list of companies using Gemini"""
    
    client, config = setup_gemini_client()
    if not client:
        print("Failed to setup Gemini client")
        return {}
    
    results = {}
    delay = 60 / max_requests_per_minute  # Rate limiting
    
    print(f"Finding LinkedIn URLs for {len(company_names)} companies...")
    print(f"Rate limit: {max_requests_per_minute} requests per minute")
    print("=" * 60)
    
    for i, company_name in enumerate(company_names):
        print(f"{i+1:2d}/{len(company_names)} Searching: {company_name}")
        
        # Find LinkedIn URL
        linkedin_url = find_linkedin_url_with_gemini(company_name, client, config)
        
        if linkedin_url:
            results[company_name] = linkedin_url
            print(f"    ✅ Found: {linkedin_url}")
        else:
            results[company_name] = None
            print(f"    ❌ Not found")
        
        # Rate limiting
        if i < len(company_names) - 1:
            print(f"    Waiting {delay:.1f}s...")
            time.sleep(delay)
    
    return results

def save_verified_urls(results, filename="verified_linkedin_urls.txt"):
    """Save verified LinkedIn URLs to a file"""
    
    found_count = sum(1 for url in results.values() if url)
    not_found_count = len(results) - found_count
    
    print(f"\n📊 Results Summary:")
    print(f"✅ Found: {found_count}")
    print(f"❌ Not found: {not_found_count}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# LinkedIn URLs found using Gemini with Google Search\n")
        f.write(f"# Found: {found_count}/{len(results)} companies\n\n")
        
        f.write("# FOUND URLs:\n")
        for company, url in results.items():
            if url:
                f.write(f"{company} -> {url}\n")
        
        f.write(f"\n# NOT FOUND:\n")
        for company, url in results.items():
            if not url:
                f.write(f"{company} -> NOT_FOUND\n")
    
    print(f"📁 Results saved to: {filename}")
    return filename

def main():
    """Test the LinkedIn URL finder with sample companies"""
    
    # Test with a few companies first
    test_companies = [
        "Google",
        "Microsoft", 
        "Meta",
        "OpenAI",
        "Hugging Face",
        "DeepMind"
    ]
    
    print("Testing LinkedIn URL finder with Gemini...")
    
    # Find URLs
    results = verify_and_find_linkedin_urls(test_companies, max_requests_per_minute=6)
    
    # Save results
    save_verified_urls(results, "test_linkedin_urls.txt")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    main()
