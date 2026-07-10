import os
import re
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def gpt_quillbot_com(page: Page, prompt: str, observe: str, _timeout: int):
    # Locate the omnibox input field
    # input_selector = page.locator('textarea[name="omnibox-input"]').first
    input_selector = page.locator(
        'div[class*="MuiInputBase-root"] textarea[name="omnibox-input"]'
    )
    
    # <div class="MuiInputBase-root MuiInputBase-colorPrimary MuiInputBase-fullWidth MuiInputBase-multiline css-drnxf2"><textarea name="omnibox-input" placeholder="" class="MuiInputBase-input MuiInputBase-inputMultiline css-nam8hl" style="height: 46px; min-height: 48px;"></textarea><textarea aria-hidden="true" class="MuiInputBase-input MuiInputBase-inputMultiline css-nam8hl" readonly="" tabindex="-1" style="visibility: hidden; position: absolute; overflow: hidden; height: 0px; top: 0px; left: 0px; transform: translateZ(0px); padding-top: 0px; padding-bottom: 0px; width: 890px;"></textarea></div>
    
    await input_selector.wait_for(state='visible', timeout=15000)
    await input_selector.fill(prompt)
    await input_selector.press('Enter')
    
    # Wait for URL redirection using a compiled regex pattern
    try:
        await page.wait_for_url(re.compile(r'ai-chat'), timeout=15000)
    except Exception:
        pass
        
    await asyncio.sleep(10)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        await asyncio.sleep(3)
        
        # Target the last rendered AI chat response test ID
        response_container = page.locator('[data-testid="ai-chat-response"]').last
        try:
            response_text = await response_container.inner_text()
        except Exception:
            response_text = ''
            
        if observe.lower() in response_text.lower():
            break
            
        attempts += 1
        
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
        await page.goto("https://quillbot.com/", timeout=60000)

        result = await gpt_quillbot_com(
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