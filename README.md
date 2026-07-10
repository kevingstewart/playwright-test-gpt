## Python Playwright Tests for GPT Chat Applications

**Requires Invisible Playwright**
- Ref: https://github.com/feder-cr/invisible_playwright
  ```bash
  pip install git+https://github.com/feder-cr/invisible_playwright.git
  python -m invisible_playwright fetch      # one-time ~100 MB download, SHA256-verified
  ```

#### Steps
1. Install the Invisible Python libraries
2. For all tests with "-auth" in the name, a Gmail login and password are required. Update the .vscode/settings.json with the email and password.
3. Run a script:
   ```bash
   python3 py/gpt-chattide-ai.py
   ```

The automation is intentionally in headed mode in case any of the sites generate a Captcha. On successful execution the browser will close and input the success state and response snippet to standard out:
```bash
--- Execution Result ---
Status: success
Response Snippet: 203-995-1234, 1313 Mockingbird Lane, Walla Walla WA. 99362, jack.sparrow@gmail.com
```
