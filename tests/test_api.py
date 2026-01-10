import requests
import dotenv
import os

dotenv.load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

url = "https://api.github.com/user/repos"
headers = {
    "authorization" : f"token {GITHUB_TOKEN}"
}

# response = requests.get(url, headers=headers)
# if(response.status_code == 200):
#     print(response.json())
# else:
#     print(f"Failed to fetch repositories: {response.status_code}")


repo = "Bharathraj-K/Ai-Code-Review-Test-Repo"
pr_number = 1
url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
response = requests.get(url, headers=headers)
print(response.json())