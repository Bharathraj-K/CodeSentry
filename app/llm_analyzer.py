# Version 1: Hugging Face Transformers backend


from transformers import AutoTokenizer, AutoModelForCausalLM
import torch 


class CodeAnalyzer:
    def __init__(self, model_name="deepseek-ai/deepseek-coder-6.7b-instruct"):
        print(f"Loading model: {model_name}...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("Model loaded successfully!")
    
    def analyze_code(self, code_diff, filename, static_issues=None):
        """Analyze code changes and return concise review"""
        
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

        # Add static analysis context if available
        static_context = ""
        if static_issues:
            static_context = f"\n\n## Static Analysis Tools Found:\n{static_issues}\n\nreview these findings and provide additional context or explanation."

        prompt = f"""{system_prompt}

File: `{filename}`

Diff:
----------------
{code_diff}
----------------
{static_context}

Review the changes above."""

        inputs = self.tokenizer(
            prompt, 
            return_tensors="pt", 
            max_length=350,
            truncation=True
        )
        
        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Generate review 
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.3,  
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.2,  
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract analysis  
        review = full_text.replace(prompt, "").strip()  
        
        return review

    def format_review(self, reviews):
        formatted = "## AI Code Review\n\n"
        for filename, review in reviews.items():
            formatted += f"### `{filename}`\n\n{review}\n\n"
        formatted += "---\n*Powered by AI Code Reviewer*"
        return formatted