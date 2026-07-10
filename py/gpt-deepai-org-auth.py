import os
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def login(page, username: str, password: str):
    # Execute sequential click and fill actions for the login modal
    await page.locator('#headerLoginButton').click()
    await page.locator('#switch-to-email').click()
    await page.locator('#user-email').fill(username)
    await page.locator('#user-password').fill(password)
    await page.locator('#login-via-email-id').click()
    await asyncio.sleep(5)
    
    # Handle optional subscription pop-up dismissal
    close_sub = page.locator('#close-sub')
    try:
        if await close_sub.is_visible():
            await close_sub.click()
    except Exception:
        pass

async def gpt_deepai_org(page, prompt: str, observe: str, _timeout: int, username: str, password: str):
    # Perform authentication step
    await login(page, username, password)
    
    # Target either textarea or standard text input elements
    input_selector = page.locator('textarea, input[type="text"]').first
    await input_selector.wait_for(state='visible', timeout=15000)
    await input_selector.fill(prompt)
    # await input_selector.press('Enter')
    await page.locator('#mainSubmitButton').click()
    await asyncio.sleep(3)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        await asyncio.sleep(3)
        
        # Extract response text from the last rendered markdown container
        response_container = page.locator('.markdownContainer').last
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
            username = config["gptUsername"]
            password = config["gptPassword"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON or missing keys: {e}")
            return

    async with InvisiblePlaywright() as browser:
        page = await browser.new_page()
        await page.goto("https://deepai.org/", timeout=60000)

        result = await gpt_deepai_org(
            page=page, 
            prompt=prompt,
            observe=observe,
            _timeout=3000,
            username=username,
            password=password
        )
        
        print("\n--- Execution Result ---")
        print(f"Status: {result['status']}")
        print(f"Response Snippet: {result['value'][:300]}")
        
        # Close the browser session
        await browser.close()


if __name__ == "__main__":
    # Run the async loop
    asyncio.run(main())