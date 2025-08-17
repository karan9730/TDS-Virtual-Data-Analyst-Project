# /// script
# requires-python = ">=3.11"
# dependencies = [
#    "asyncio",
#    "playwright",
# ]
# ///

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright  # type: ignore
from tools.dom_structure import extract_dom_structure_with_identifiers


async def scrape_webpage(url: str, output_file: str = "scraped_content.html") -> dict:
    """
    Scrapes the HTML content of a webpage and saves both the HTML
    and a DOM structure representation to /tmp/outputs.

    Returns the saved filenames and a concise message.
    """
    try:
        # Ensure outputs directory exists
        output_dir = Path("/tmp/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Clean the filename and ensure .html extension
        clean_filename = Path(output_file).name
        if not clean_filename.lower().endswith(".html"):
            clean_filename += ".html"

        html_path = output_dir / clean_filename
        dom_path = output_dir / f"{html_path.stem}_dom.txt"

        async with async_playwright() as p:
            # safer chromium launch options to prevent crashes
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process",
                ]
            )
            page = await browser.new_page()
            try:
                # wait_until networkidle to ensure page fully loads
                await page.goto(url, wait_until="networkidle", timeout=120000)
                content = await page.content()

                # Save HTML content
                html_path.write_text(content, encoding="utf-8")

                # Save DOM structure
                dom_structure = extract_dom_structure_with_identifiers(content)
                dom_path.write_text(dom_structure, encoding="utf-8")

                return {
                    "status": "success",
                    "message": f"Scraping completed and saved to {clean_filename}",
                    "html_file": clean_filename,
                    "dom_file": f"{html_path.stem}_dom.txt"
                }

            except Exception as e:
                return {"status": "error", "message": f"Failed to load page: {e}"}
            finally:
                await browser.close()

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    test_url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
    result = asyncio.run(scrape_webpage(test_url))
    print(result)