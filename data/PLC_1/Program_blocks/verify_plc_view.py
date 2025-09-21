import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    """
    Navigates to the local HTML file and takes a screenshot of the rendered PLC logic.
    """
    # Get the absolute path to the index.html file
    html_file_path = os.path.abspath('data/PLC_1/Program_blocks/index.html')

    # Check if the file exists
    if not os.path.exists(html_file_path):
        print(f"Error: HTML file not found at {html_file_path}")
        return

    # Use a file:// URL to open the local file
    url = f'file://{html_file_path}'

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            print(f"Navigating to {url}...")
            await page.goto(url)

            # Wait for the network container to be visible and populated
            await page.wait_for_selector('.networks-container svg', timeout=5000)
            print("SVG container found. Taking screenshot...")

            # Locate the main container element to screenshot
            container_element = await page.query_selector('.container')

            if container_element:
                # Define the output path for the screenshot
                screenshot_path = 'data/PLC_1/Program_blocks/output.png'
                await container_element.screenshot(path=screenshot_path)
                print(f"Screenshot saved successfully to {screenshot_path}")
            else:
                print("Error: Could not find the '.container' element to screenshot.")

        except Exception as e:
            print(f"An error occurred during Playwright execution: {e}")
            # Take a screenshot of the full page for debugging purposes
            await page.screenshot(path='data/PLC_1/Program_blocks/error_screenshot.png')
            print("Saved an error screenshot to error_screenshot.png")

        finally:
            await browser.close()
            print("Browser closed.")

if __name__ == '__main__':
    asyncio.run(main())
