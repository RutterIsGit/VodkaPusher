"""
BrightData Client with Browser API (Primary) and Web Unlocker API (Fallback).
Implements two-tier approach for maximum reliability.
"""

import os
import asyncio
import requests
import time
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from dotenv import load_dotenv

# Check if playwright is installed
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

load_dotenv()


class BrightDataClient:
    """Unified BrightData client with Browser API and Web Unlocker fallback."""
    
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv('BRIGHTDATA_API_KEY')
        if not self.api_key:
            raise ValueError("BRIGHTDATA_API_KEY not found in environment variables")
        
        # Browser API credentials from documentation
        self.browser_auth = 'brd-customer-hl_8b8cd293-zone-scraping_browser1:j31srxwlpvo5'
            
        # Web Unlocker API endpoint
        self.unlocker_url = "https://api.brightdata.com/request"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0
        
    def _rate_limit(self):
        """Ensure rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    async def scrape_with_browser(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Scrape using Browser API (Playwright with BrightData proxy).
        Best for dynamic sites requiring JavaScript rendering.
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("    Warning: playwright not installed. Browser API not available.")
            return None
            
        if not self.browser_auth:
            print("Browser API credentials not available")
            return None
            
        try:
            # Build WebSocket URL
            ws_url = f'wss://{self.browser_auth}@brd.superproxy.io:9222'
            
            async with async_playwright() as pw:
                print(f"    Connecting to BrightData Browser API...")
                browser = await pw.chromium.connect_over_cdp(ws_url)
                
                try:
                    page = await browser.new_page()
                    print(f"    Navigating to {url}")
                    
                    # Set timeout and navigate
                    page.set_default_timeout(timeout * 1000)
                    await page.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
                    
                    # Wait a bit for dynamic content
                    await page.wait_for_timeout(2000)
                    
                    # Get the HTML content
                    html = await page.content()
                    print(f"    Successfully retrieved {len(html)} characters via Browser API")
                    
                    return html
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            print(f"    Browser API error: {str(e)}")
            return None
    
    def scrape_with_unlocker(self, url: str, timeout: int = 30) -> Optional[str]:
        """
        Scrape using Web Unlocker API (Direct HTTP).
        Fallback method that still handles anti-bot measures.
        """
        self._rate_limit()
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "zone": "mcp_unlocker",
            "url": url,
            "format": "raw"
        }
        
        try:
            print(f"    Using Web Unlocker API...")
            response = requests.post(
                self.unlocker_url,
                json=data,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                print(f"    Successfully retrieved {len(response.text)} characters via Web Unlocker")
                return response.text
            else:
                print(f"    Web Unlocker error: {response.status_code}")
                print(f"    Response: {response.text[:200]}...")
                return None
                
        except requests.exceptions.Timeout:
            print(f"    Request timeout after {timeout} seconds")
            return None
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {e}")
            return None
    
    def scrape_url(self, url: str, timeout: int = 45) -> Optional[str]:
        """
        Main scraping method that always tries Browser API first, then Web Unlocker.
        Returns HTML content or None if both methods fail.
        """
        if not url or not isinstance(url, str) or not url.strip():
            print("    Error: Empty or invalid URL provided")
            return None
            
        url = url.strip()
        print(f"\n  Scraping: {url}")
        
        # Always try Browser API first if available
        if PLAYWRIGHT_AVAILABLE:
            print(f"  Trying Browser API first...")
            
            # Run async function in sync context
            try:
                html = asyncio.run(self.scrape_with_browser(url, timeout))
                if html:
                    return html
            except Exception as e:
                print(f"    Browser API failed: {e}")
        
        # Fallback to Web Unlocker
        print(f"  Trying Web Unlocker API as fallback...")
        return self.scrape_with_unlocker(url, timeout)
    
    def classify_url(self, url: str) -> str:
        """
        Classify URL to help determine scraping strategy.
        Returns: 'facebook', 'tripadvisor', 'dynamic', or 'static'
        """
        domain = urlparse(url).netloc.lower()
        
        if 'facebook.com' in domain:
            return 'facebook'
        elif 'tripadvisor' in domain:
            return 'tripadvisor'
        elif any(site in domain for site in ['yelp.com', 'instagram.com', 'twitter.com']):
            return 'dynamic'
        else:
            return 'static'


# Test function
if __name__ == "__main__":
    # Test the client
    test_urls = [
        "https://httpbin.org/html",
        "https://www.tripadvisor.com/Restaurant_Review-g1022655-d7316778-Reviews-The_Chequers-Billericay_Essex_England.html",
        "https://www.facebook.com/TheBillericayConstitutionalClub/"
    ]
    
    try:
        client = BrightDataClient()
        print("BrightData client initialized successfully")
        
        for url in test_urls[:1]:  # Test first URL only
            html = client.scrape_url(url)
            if html:
                print(f"✓ Success! Retrieved content from {url}")
            else:
                print(f"✗ Failed to retrieve {url}")
                
    except Exception as e:
        print(f"Error: {e}")