# 🤖 AI Code Reviewer

An intelligent, automated code review system that analyzes GitHub pull requests using Large Language Models and static analysis tools. Provides comprehensive code reviews with security scanning, bug detection, and best practice recommendations.

## ✨ Features

- **🔍 Multi-Language Support** - Analyzes Python, JavaScript, TypeScript, Java, Go, Ruby, PHP, C/C++, C#, Rust, Kotlin, and Swift
- **🧠 Dual LLM Backends** - Choose between LM Studio API (local, AMD-optimized) or Hugging Face Transformers
- **🔒 Security Scanning** - Integrated Bandit (Python) and Semgrep (all languages) for vulnerability detection
- **⚡ Real-time Reviews** - Automatic PR review via GitHub webhooks
- **📊 Comprehensive Reports** - Detailed feedback on bugs, code quality, best practices, and security
- **🚀 Background Processing** - Non-blocking webhook handling for fast response times
- **🎯 Flexible Deployment** - Works with local or cloud-hosted LLMs

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   GitHub    │────────>│   FastAPI    │────────>│  LLM Backend    │
│   Webhook   │         │   Server     │         │ (LM Studio/HF)  │
└─────────────┘         └──────────────┘         └─────────────────┘
                               │
                               ├────────> Bandit (Python Security)
                               │
                               └────────> Semgrep (Multi-language)
```

## 📸 Screenshots

### 🧠 AI Code Review Comment
![AI Code Review Comment]<img width="917" height="894" alt="Screenshot 2026-01-13 185945" src="https://github.com/user-attachments/assets/be14455c-880d-4222-b2c5-290d11844c03" />


*Example of an AI-generated code review posted on a GitHub pull request.*

---

### 🖥️ Terminal Output
![Terminal Output](https://github.com/user-attachments/assets/964ff81f-0a1c-4cd5-89a2-e9cc22889428)

*Real-time processing logs showing the analysis pipeline running.*

---

### 🔗 GitHub Webhook Log
![GitHub Webhook Log](https://github.com/user-attachments/assets/6e302f39-535a-4b0e-9611-dc7536817a05)

*Webhook delivery and response status from GitHub.*


## 🚀 Setup

### Prerequisites

- Python 3.10+
- GitHub Personal Access Token
- **Choose ONE of the following LLM backends:**
  - **Option A:** [LM Studio](https://lmstudio.ai/) - Local inference (recommended for AMD GPUs, uses DirectML)
  - **Option B:** NVIDIA GPU with CUDA support (for Hugging Face Transformers backend)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/AI_CODE_REVIEWER.git
cd AI_CODE_REVIEWER
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

> **Note:** All dependencies including FastAPI, Bandit, Semgrep, and other required packages are in `requirements.txt`

4. **Configure environment variables**

Create a `.env` file in the root directory:
```env
GITHUB_TOKEN=your_github_personal_access_token
HUGGING_FACE_TOKEN=your_hf_token
WEBHOOK_SECRET=your_webhook_secret_key
```

### Choosing Your LLM Backend

#### Option A: LM Studio (Recommended for AMD/CPU)

**Advantages:**
- ✅ Optimized for AMD GPUs via DirectML
- ✅ Works on CPU-only systems
- ✅ Easy-to-use GUI for model management
- ✅ OpenAI-compatible API

**Setup:**
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Launch LM Studio and download a code model (e.g., CodeLlama, DeepSeek Coder, Qwen Coder)
3. Click "Start Server" in LM Studio (default: `http://localhost:1234`)
4. In `app/main.py`, ensure you're importing:
```python
from .llm_analyzer_lmstudio import CodeAnalyzer
```

#### Option B: Hugging Face Transformers (For NVIDIA GPUs)

**Advantages:**
- ✅ Direct model loading without external server
- ✅ Optimized for NVIDIA CUDA GPUs
- ✅ Full control over model parameters

**Setup:**
1. Ensure you have NVIDIA GPU with CUDA installed
2. In `app/main.py`, change the import to:
```python
from .llm_analyzer import CodeAnalyzer
```
3. The default model is `deepseek-ai/deepseek-coder-6.7b-instruct` (downloads automatically on first run)
4. Modify the model in `llm_analyzer.py` if needed

### Switching Between LLM Backends

In `app/main.py`, change the import line:

**For LM Studio:**
```python
from .llm_analyzer_lmstudio import CodeAnalyzer
```

**For Hugging Face Transformers:**
```python
from .llm_analyzer import CodeAnalyzer
```

### LM Studio Configuration

Edit in `app/llm_analyzer_lmstudio.py`:
```python
analyzer = CodeAnalyzer(
    base_url="http://localhost:1234/v1",  # LM Studio API endpoint
    model="local-model"                    # Model identifier
)
```

### Hugging Face Configuration

Edit in `app/llm_analyzer.py`:
```python
analyzer = CodeAnalyzer(
    model_name="deepseek-ai/deepseek-coder-6.7b-instruct"  # Any HF model or your own fine tuned model
)
```

### Analysis Parameters

Temperature, max tokens, and other generation parameters can be adjusted in the respective analyzer files.

### Running the Application

Start the API server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Useful endpoints:

- `GET /` - Basic status
- `GET /health` - Health check
- `POST /webhook` - GitHub webhook receiver

### GitHub Webhook Setup

1. In your GitHub repo: **Settings** → **Webhooks** → **Add webhook**
2. Payload URL: `http://your-server:8000/webhook` (Example: ngrok http 8000 -> http://abc.ngrok.io:8000/webhook)
3. Content type: `application/json`
4. Secret: your `WEBHOOK_SECRET` from `.env`
5. Events: select **Pull requests** (or “Let me select individual events” → **Pull requests**)
6. Click **Add webhook**

## 📖 Usage

Once configured, the bot automatically reviews pull requests:

1. **Open a PR** in your configured repository
2. **Webhook triggers** the review process
3. **AI analyzes** code changes with static analysis
4. **Review posted** as a comment on the PR


## 🛠️ Configuration

### LM Studio Settings

Edit in `app/llm_analyzer_lmstudio.py`:
```python
analyzer = CodeAnalyzer(
    base_url="http://localhost:1234/v1",  # LM Studio API endpoint
    model="local-model"                    # Model identifier
)
```

### Analysis Parameters

Temperature, tokens, and other settings can be adjusted in the analyzer files.

## 📁 Project Structure

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── github_api.py
│   ├── llm_analyzer.py
│   ├── llm_analyzer_lmstudio.py
│   ├── main.py
│   └── static_analyzer.py
│
├── Dockerfile
├── PROJECT_ROADMAP.md
├── README.md
└── requirements.txt
```

## 🔧 Technologies Used

- **FastAPI** - High-performance web framework
- **LM Studio** - Local LLM inference via OpenAI-compatible API
- **Hugging Face Transformers** - Direct model loading backend
- **Bandit** - Python security vulnerability scanner
- **Semgrep** - Multi-language static analysis engine
- **Requests** - HTTP client library

## 🎯 Review Categories

The AI analyzes code across five dimensions:

1. **🐛 Bugs** - Logic errors, edge cases, runtime issues
2. **📝 Code Quality** - Readability, naming, structure
3. **⭐ Best Practices** - Language idioms, performance patterns
4. **🔒 Security** - Vulnerabilities, injection risks, unsafe operations
5. **💡 Suggested Fixes** - Concrete code improvements

## 🔐 Security

- Webhook signature verification via HMAC-SHA256
- Secure token storage in environment variables
- Local LLM execution option (no code sent to external LLM providers when using LM Studio locally)
- [Hugging Face](https://huggingface.co/) for the Transformers library and model hub
- [Semgrep](https://semgrep.dev/) for multi-language static analysis
- [Bandit](https://bandit.readthedocs.io/) for Python security scanning
- All open-source LLM projects that make this possible

---

**Built with ❤️ • Supports both AMD (LM Studio) and NVIDIA (Transformers) hardware**

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) for local LLM inference
- [Semgrep](https://semgrep.dev/) for multi-language static analysis
- [Bandit](https://bandit.readthedocs.io/) for Python security scanning

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using AMD hardware optimization through LM Studio**
