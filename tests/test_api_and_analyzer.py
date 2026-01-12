from app.llm_analyzer_lmstudio import CodeAnalyzer
from app.github_api import GitHubAPI

analyzer =  CodeAnalyzer()
api = GitHubAPI()

repo = "Bharathraj-K/Ai-Code-Review-Test-Repo"

pr_number = 1

files = api.get_pr_files(repo, pr_number)
print(files)

reviews = {}

for file in files:
    review = analyzer.analyze_code(file.get("patch", ""), file["filename"])
    reviews[file["filename"]] = review

comment = analyzer.format_review(reviews)

print(comment)