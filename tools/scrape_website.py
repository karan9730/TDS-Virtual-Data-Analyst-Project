# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "asyncio",
#    "playwright",
# ]
# ///

import asyncio
import os
from playwright.async_api import async_playwright  # type: ignore
from tools.dom_structure import extract_dom_structure_with_identifiers

async def scrape_website(url: str, output_file: str = "scraped_content.html"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            content = await page.content()

            # Clean the output filename to avoid duplicate 'outputs/' nesting
            clean_filename = output_file.replace("outputs/", "").lstrip("/")
            output_path = os.path.join("outputs", clean_filename)

            # Save the HTML content
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(content)

            # Save DOM structure
            dom_structure = extract_dom_structure_with_identifiers(content)
            dom_path = os.path.join("outputs", "dom_structure.txt")
            with open(dom_path, "w", encoding="utf-8") as f:
                f.write(dom_structure)

        except Exception as e:
            print(f"Failed to load page: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"  # Replace with the URL you want to scrape
    asyncio.run(scrape_website(url))
    print("Scraping completed and content saved to scraped_content.html")