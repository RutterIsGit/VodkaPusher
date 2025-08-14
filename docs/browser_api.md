Introduction to Browser API
Learn how Bright Data’s Browser API simplifies multi-step data collection with robust proxy networks, browser automation, and full unblocking capabilities.

Browser API is part of our unlocker scraping suite and is designed to simplify your multi-step data collection from browsers.

Your scraping code runs seamlessly on our dedicated browsers, leveraging multiple proxy networks (including residential IPs) and managing the full unblocking of every page including custom headers, fingerprinting, CAPTCHA solving, and more.

Effortlessly access and navigate your target websites via standard browsing libraries like puppeteer, playwright, and selenium (see our full list here), to extract the precise data you need at unlimited scale and unlimited concurrent sessions.

​
Best for
Seamlessly navigating websites, filling out forms, clicking buttons, scrolling to load full pages, hovering, solving CAPTCHAs, and more interactive actions

Puppeteer, playwright, and selenium integration with the flexibility to scale the number of active browser sessions up or down as needed.

Teams without a reliable, scalable in-house browser unblocking infrastructure

Getting started
Install required library


pip3 install playwright
Run example script
Python, Playwright

CODE

import asyncio
from playwright.async_api import async_playwright

AUTH = 'brd-customer-hl_8b8cd293-zone-scraping_browser1:j31srxwlpvo5'
SBR_WS_CDP = f'wss://{AUTH}@brd.superproxy.io:9222'

async def run(pw):
    print('Connecting to Browser API...')
    browser = await pw.chromium.connect_over_cdp(SBR_WS_CDP)
    try:
        page = await browser.new_page()
        print('Connected! Navigating to webpage')
        await page.goto('https://www.example.com')
        await page.screenshot(path="page.png", full_page=True)
        print("Screenshot saved as 'page.png'")
        html = await page.content()
        print(html)
    finally:
        await browser.close()

async def main():
    async with async_playwright() as playwright:
        await run(playwright)

if __name__ == '__main__':

Get page HTML
Node.js, Puppeteer
CODE

const page = await browser.newPage();
await page.goto('https://example.com');
const html = await page.content();

Click on element
Node.js, Puppeteer
CODE

const page = await page.newPage();
await page.goto('https://example.com');
await page.click('a[href]');

Take screenshot
Node.js, Puppeteer
CODE

// More info at https://pptr.dev/api/puppeteer.page.screenshot
await page.screenshot({path: 'screenshot.png'});