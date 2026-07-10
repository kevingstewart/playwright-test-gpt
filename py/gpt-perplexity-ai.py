import os
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def gpt_perplexity_ai(page, prompt: str, observe: str, _timeout: int):
    # Locate the input field
    input_selector = page.locator('#ask-input')
    await input_selector.wait_for(state='visible', timeout=15000)
    await input_selector.click()
    
    # Type the prompt with a delay and press Enter
    await page.keyboard.type(prompt, delay=20)
    await page.keyboard.press('Enter')
    await asyncio.sleep(3)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        # print("attempts:", attempts, "response_text length:", len(response_text))
        # Check if the page is closed
        if page.is_closed():
            break
            
        await asyncio.sleep(3)
        
        # Target the last matching container element
        response_container = page.locator(
            'article, div[data-testid="answer"], div[role="article"], div[class*="answer"], div[class*="response"], div[class*="prose"]'
        ).last
        
        # Safely extract inner text
        try:
            response_text = await response_container.inner_text()
        except Exception:
            response_text = ''
            
        # Check for the expected text block
        if observe.lower() in response_text.lower():
            print("Expected text found!")
            break
            
        attempts += 1
        
    # Return final execution status
    if observe.lower() in response_text.lower():
        return {
            "value": response_text, 
            "status": "success"
        }
    else:
        return {
            "value": "none", 
            "status": f"failure: {response_text[:120]} ... (response did not contain expected text)"
        }
    

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
        await page.goto("https://perplexity.ai/", timeout=60000)

        result = await gpt_perplexity_ai(
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