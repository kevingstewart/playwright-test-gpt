import os
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def login(page, username: str, password: str):
    # Locate cookie button using the has_text parameter
    cookie_btn = page.locator('div[role="button"]', has_text='Necessary cookies only')
    
    # Safely click if visible
    try:
        if await cookie_btn.is_visible():
            await cookie_btn.click()
    except Exception:
        pass
        
    # Fill login credentials
    await page.locator('input[placeholder="Phone number / email address"]').fill(username)
    await page.locator('input[placeholder="Password"]').fill(password)
    
    # Click button matching specific role name
    await page.get_by_role('button', name='Log in', exact=True).click()
    await asyncio.sleep(5)

async def gpt_chat_deepseek_com(page, prompt: str, observe: str, _timeout: int, username: str, password: str):
    # Perform authentication step
    await login(page, username, password)
    
    # Locate message input text area
    input_selector = page.locator('textarea[placeholder="Message DeepSeek"]').first
    await input_selector.wait_for(state='visible', timeout=15000)
    await input_selector.fill(prompt)
    await input_selector.press('Enter')
    await asyncio.sleep(10)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        await asyncio.sleep(3)
        
        # Target the last DeepSeek assistant response block
        response_container = page.locator('.ds-markdown.ds-assistant-message-main-content').last
        
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
        await page.goto("https://chat.deepseek.com/", timeout=60000)

        result = await gpt_chat_deepseek_com(
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