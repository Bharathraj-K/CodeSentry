# Version 2: LM Studio backend (llama.cpp + DirectML)

import requests
import json

class CodeAnalyzer:
    def __init__(self, base_url="http://localhost:1234/v1", model="local-model"):
        """
        Initialize LM Studio API client
        
        Args:
            base_url: LM Studio API endpoint (default: http://localhost:1234/v1)
            model: Model identifier (default: "local-model")
        """
        self.base_url = base_url
        self.model = model
        self.chat_endpoint = f"{base_url}/chat/completions"
        print(f"LM Studio API initialized at {base_url}")
    
    def analyze_code(self, code_diff, filename):        
        # Instruction for critical analysis
        system_prompt = """
You are a senior software engineer performing an automated GitHub pull-request review.

You are given only a unified diff of code changes.
Review ONLY the lines shown. Do NOT assume anything about the rest of the file.

Your goal is to find real, concrete problems introduced by this change.

Rules:
- Never invent context that is not in the diff.
- Never guess what surrounding code looks like.
- If something cannot be determined, say: "Not enough context".
- Only mention security if the diff includes user input, file I/O, network calls, or database access.
- Do not give generic advice — every point must reference something in the diff.

Output exactly in this format:

### Bugs
- Real runtime errors, logic flaws, edge cases, or incorrect behavior introduced by this change.

### Code Quality
- Readability, naming, structure, duplication, or clarity issues in the diff.

### Best Practices
- Pythonic improvements, better patterns, or performance improvements that apply to the diff.

### Security
- If applicable; otherwise write exactly: "No security issues detected."

### Suggested Fix
- If a problem exists, show a corrected version of only the changed lines.
- If everything is fine, write exactly: "No changes needed."

Be concise, precise, and technically accurate.
"""

        user_prompt = f"""File: `{filename}`

Diff:
----------------
{code_diff}
----------------

Review the changes above."""

        # Prepare API request
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
            "top_p": 0.9,
            "stream": False
        }
        
        try:
            # Make API request to LM Studio
            response = requests.post(
                self.chat_endpoint,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            review = result['choices'][0]['message']['content'].strip()
            
            return review  # Max 600 chars
            
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to LM Studio. Make sure LM Studio is running at " + self.base_url
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be taking too long to respond."
        except requests.exceptions.RequestException as e:
            return f"Error calling LM Studio API: {str(e)}"
        except (KeyError, json.JSONDecodeError) as e:
            return f"Error parsing API response: {str(e)}"
        
    def format_review(self, reviews):
        formatted = "## 🤖 AI Code Review\n\n"
        for filename, review in reviews.items():
            formatted += f"### 📄 `{filename}`\n\n{review}\n\n"
        formatted += "---\n*Powered by AI Code Reviewer*"
        return formatted
        