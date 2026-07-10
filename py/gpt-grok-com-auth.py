import os
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def login(page, username: str, password: str):
    # Locate cookie button using the has_text parameter
    cookie_btn = page.get_by_role("button", name="Sign in", exact=True)
    
    # Safely click if visible
    try:
        if await cookie_btn.is_visible():
            await cookie_btn.click()
    except Exception:
        pass

    # Click the "Continue with Email" button    
    await page.get_by_test_id("continue-with-email").click()

    # Safely fill in the email field if it is visible
    await page.locator('input[type="email"]').fill(username)
    await page.get_by_test_id("sign-in-submit").click()

    ## Safely fill in the password field if it is visible andzzz
    await page.get_by_test_id("password").fill(password)
    await page.get_by_test_id("sign-in-submit").click()

    await asyncio.sleep(5)

async def gpt_grok_com(page, prompt: str, observe: str, _timeout: int, username: str, password: str):
    # Perform authentication step
    await login(page, username, password)
    
    # Locate message input text area
    input_selector = page.get_by_role("textbox", name="Ask Grok anything").first
    await input_selector.wait_for(state='visible', timeout=15000)
    await input_selector.fill(prompt)
    await input_selector.press('Enter')
    await asyncio.sleep(10)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        await asyncio.sleep(3)
        
        # Target the last Grok assistant response block
        response_container = page.get_by_test_id("assistant-message")
        
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
            username = config["gptUsername"]
            password = config["gptPassword"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON or missing keys: {e}")
            return

    async with InvisiblePlaywright() as browser:
        page = await browser.new_page()
        await page.goto("https://grok.com/", timeout=60000)

        result = await gpt_grok_com(
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