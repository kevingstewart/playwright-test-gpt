import os
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def gpt_chattide_ai(page, prompt: str, observe: str, _timeout: int):
    # Locate the first textarea matching the specific slot attribute
    input_selector = page.locator('textarea[data-slot="textarea"]').first
    await input_selector.wait_for(state='visible', timeout=15000)
    
    # Fill the input and press Enter to submit
    await input_selector.fill(prompt)
    await input_selector.press('Enter')
    await asyncio.sleep(3)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        await asyncio.sleep(3)
        
        # Target the last rendered react-markdown element
        response_container = page.locator('.react-markdown').last
        
        try:
            response_text = await response_container.inner_text()
        except Exception:
            response_text = ''
            
        if observe.lower() in response_text.lower():
            break
            
        attempts += 1
        
    if observe.lower() in response_text.lower():
        return {"value": response_text, "status": "success"}
    else:
        return {"value": "none", "status": f"failure: {response_text[:120]} ... (response did not contain expected text)"}
    

async def main():
    settings_path = Path(".vscode/settings.json")
    if not settings_path.exists():
        print(f"Error: {settings_path} not found. Please create the file first.")
        return
        
    with open(settings_path, "r") as file:
        try:
            config = json.load(file)
            prompt = config["prompt"]
            observe = config["observe"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON or missing keys: {e}")
            return

    async with InvisiblePlaywright() as browser:
        page = await browser.new_page()
        await page.goto("https://chattide.ai/", timeout=60000)

        result = await gpt_chattide_ai(
            page=page, 
            prompt=prompt,
            observe=observe,
            _timeout=3000
        )
        
        print("\n--- Execution Result ---")
        print(f"Status: {result['status']}")
        print(f"Response Snippet: {result['value'][:300]}")
        
        # Close the browser session
        await browser.close()


if __name__ == "__main__":
    # Run the async loop
    asyncio.run(main())