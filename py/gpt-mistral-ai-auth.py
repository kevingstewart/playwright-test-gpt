import os
import re
import asyncio
import json
from pathlib import Path

# from invisible_playwright import InvisiblePlaywright
from invisible_playwright.async_api import InvisiblePlaywright

async def login(page, username: str, password: str):
    # chat.mistral.ai/work loads its shell first, then client-side redirects
    # to the auth login page a couple seconds later. Wait for that redirect
    # to settle before looking for form fields, otherwise interactions race
    # against the in-flight navigation.
    try:
        await page.wait_for_url(re.compile(r'auth\.mistral\.ai'), timeout=15000)
    except Exception:
        pass

    email_input = page.locator('input[name="email"]')
    
    # Custom visibility check with a 5000ms timeout
    is_email_visible = False
    try:
        is_email_visible = await email_input.is_visible()
    except Exception:
        pass

    if is_email_visible:
        await email_input.fill(username)
        await page.locator('button[type="submit"]', has_text='Continue').click()
        
        password_input = page.locator('input[name="password"]')
        await password_input.wait_for(state='visible', timeout=15000)
        await password_input.fill(password)
        
        await page.locator('button', has_text='Continue with password').click()
        await asyncio.sleep(5)

    # Handle Terms of Service dialog dismissal
    accept_tos_btn = page.locator('[role="dialog"] button', has_text='Accept and continue')
    try:
        if await accept_tos_btn.is_visible():
            await accept_tos_btn.click()
    except Exception:
        pass

    # Handle Banner notification dismissal
    close_banner_btn = page.locator('button[aria-label="Dismiss"]').first
    try:
        if await close_banner_btn.is_visible():
            await close_banner_btn.click()
    except Exception:
        pass

async def gpt_chat_mistral_ai_work(page, prompt: str, observe: str, _timeout: int, username: str, password: str):
    # Execute the complex multi-step authentication process
    await login(page, username, password)
    
    # Locate the rich-text ProseMirror input element
    input_selector = page.locator('.ProseMirror[contenteditable="true"]').first
    await input_selector.wait_for(state='visible', timeout=15000)
    await input_selector.fill(prompt)
    await input_selector.press('Enter')
    await asyncio.sleep(3)
    
    response_text = ''
    attempts = 0
    max_attempts = 20
    
    while attempts < max_attempts:
        await asyncio.sleep(3)
        
        # Target the last text response chunk based on Mistral attributes
        response_container = page.locator('[data-message-part-type="answer"]').last
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
        await page.goto("https://chat.mistral.ai/work", timeout=60000)

        result = await gpt_chat_mistral_ai_work(
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