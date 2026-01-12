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
    
    def analyze_code(self, code_diff, filename):
        """Analyze code changes and return concise review"""
        
        # Instruction for critical analysis
        prompt = f"""
You are an AI code reviewer for a GitHub pull request.

You are given ONLY a code diff from `{filename}`.
Review ONLY what changed. Do NOT assume anything about the rest of the file.

Diff:
----------------
{code_diff}
----------------

Your job is to identify real issues in these changes.

Rules:
- Do NOT invent missing context.
- Do NOT mention things not visible in the diff.
- If something cannot be determined, say "Not enough context".
- Only mention security if the diff includes user input, files, network, or database usage.

Respond in this exact format:

### Bugs
- Concrete logic or runtime issues introduced by this change.

### Code Quality
- Readability, naming, structure, or maintainability problems in the diff.

### Best Practices
- Pythonic improvements or better patterns that apply to this change.

### Security
- If applicable; otherwise write: "No security issues detected."

### Suggested Fix
- Show a corrected version of the changed lines if something is wrong.
- Otherwise write: "No changes needed."

Be concise. Be factual. Be strict.
"""



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
                max_new_tokens=200,
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
        
        return review[:600]  # Max 600 chars
        
    def format_review(self, reviews):
        formatted = "## 🤖 AI Code Review\n\n"
        for filename, review in reviews.items():
            formatted += f"### 📄 `{filename}`\n\n{review}\n\n"
        formatted += "---\n*Powered by AI Code Reviewer*"
        return formatted