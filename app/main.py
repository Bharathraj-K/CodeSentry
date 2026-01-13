from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
import hmac
import hashlib
from .github_api import GitHubAPI
from .llm_analyzer_lmstudio import CodeAnalyzer
from .static_analyzer import StaticAnalyzer
from .config import WEBHOOK_SECRET

app = FastAPI(title="AI Code Reviewer")
github_api = GitHubAPI()
analyzer = CodeAnalyzer()
static_analyzer = StaticAnalyzer()

@app.get("/")
def read_root():
    return {"message": "AI Code Reviewer is running!", "version": "1.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

async def process_review(repo, pr_number, head_sha):
    """Process PR review in background"""
    try:
        print(f"Starting review for PR #{pr_number} in {repo}...")
        
        # Get changed files
        files = github_api.get_pr_files(repo, pr_number)
        print(f"Found {len(files)} changed files---")
        
        # Analyze each file
        reviews = {}
        for file in files[:5]:  # Limit to 5 files
            filename = file["filename"]
            patch = file.get("patch", "")
            
            if patch:
                print(f"Analyzing {filename}...")
                
                # Get full file content for static analysis
                try:
                    file_content_data = github_api.get_file_contents(repo, filename, ref=head_sha)
                    import base64
                    file_content = base64.b64decode(file_content_data['content']).decode('utf-8')
                    
                    # Run static analysis
                    print(f"Running static analysis on {filename}...")
                    static_results = static_analyzer.analyze_file(filename, file_content)
                    print(f"   {static_results['summary']}")
                    
                    # Format static issues for LLM
                    static_context = static_analyzer.format_issues_for_llm(static_results)
                    
                    # LLM review with static analysis context
                    review = analyzer.analyze_code(patch, filename, static_context)
                    reviews[filename] = review
                    
                except Exception as e:
                    print(f"⚠️ Could not get file content for {filename}: {e}")
                    # Fallback: LLM review without static analysis
                    review = analyzer.analyze_code(patch, filename)
                    reviews[filename] = review
        
        # Post review
        if reviews:
            print(f"Posting review with {len(reviews)} files...")
            comment = analyzer.format_review(reviews)
            github_api.post_comment(repo, pr_number, comment)
            print("Review posted successfully!")
        else:
            print("No files to review")
        
        # Cleanup
        static_analyzer.cleanup()
            
    except Exception as e:
        print(f"❌ Error processing review: {e}")

@app.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handle GitHub webhook events"""
    
    body = await request.body()
    
    # Verify webhook signature (security)
    signature = request.headers.get("X-Hub-Signature-256")
    if not verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Parse JSON from the already-read body
    import json
    payload = json.loads(body)
    
    # Handle ping event (GitHub webhook test)
    if "zen" in payload:
        return {"message": "pong", "status": "healthy"}
    
    # Only handle PR events
    if "pull_request" not in payload:
        return {"message": "Event ignored"}
    
    pr = payload["pull_request"]
    action = payload["action"]
    
    # Only review when PR is opened or synchronized (new commits)
    if action not in ["opened", "synchronize"]:
        return {"message": "Action ignored"}
    
    # Extract details
    repo = payload["repository"]["full_name"]
    pr_number = pr["number"]
    head_sha = pr["head"]["sha"]  # Get the commit SHA from the PR head
    
    # Process review in background (don't block webhook response)
    background_tasks.add_task(process_review, repo, pr_number, head_sha)
    
    # Return immediately (GitHub won't timeout!)
    return {"message": "Review queued", "pr": pr_number, "repo": repo}

def verify_signature(payload_body, signature_header):
    """Verify GitHub webhook signature"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)