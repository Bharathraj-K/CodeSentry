import subprocess
import json
import tempfile
import os
from pathlib import Path

class StaticAnalyzer:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ai_code_review_")
    
    def _detect_language(self, filename):
        """Detect programming language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.cs': 'csharp',
            '.rs': 'rust',
            '.kt': 'kotlin',
            '.swift': 'swift'
        }
        ext = os.path.splitext(filename)[1].lower()
        return ext_map.get(ext, None)
    
    def analyze_file(self, filename, code_content):
        """
        Run static analysis on a single file (multi-language support)
        
        Args:
            filename: Name of the file (e.g., 'main.py', 'app.js')
            code_content: Full content of the file
            
        Returns:
            dict: {
                'language': 'python',
                'bandit_issues': [...],
                'semgrep_issues': [...],
                'summary': 'X issues found'
            }
        """
        language = self._detect_language(filename)
        
        results = {
            'language': language,
            'bandit_issues': [],
            'semgrep_issues': [],
            'summary': ''
        }
        
        # Skip unsupported file types
        if not language:
            results['summary'] = f"⚠️ Unsupported file type: {filename}"
            return results
        
        # Write to temp file
        temp_file = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        # Run Bandit for Python only
        if language == 'python':
            results['bandit_issues'] = self._run_bandit(temp_file)
        
        # Run Semgrep for all languages
        results['semgrep_issues'] = self._run_semgrep(temp_file, language)
        
        # Generate summary
        total = len(results['bandit_issues']) + len(results['semgrep_issues'])
        
        if total > 0:
            results['summary'] = f"⚠️ {total} issues detected by static analysis ({language})"
        else:
            results['summary'] = f"✅ No issues detected by static analysis ({language})"
        
        return results
    
    def _run_bandit(self, filepath):
        """Run Bandit security scanner (Python only)"""
        issues = []
        try:
            result = subprocess.run(
                ['bandit', '-f', 'json', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    issues.append({
                        'tool': 'Bandit',
                        'severity': issue['issue_severity'],
                        'confidence': issue['issue_confidence'],
                        'line': issue['line_number'],
                        'code': issue['issue_text'],
                        'description': f"{issue['issue_text']} (CWE-{issue.get('issue_cwe', {}).get('id', 'N/A')})"
                    })
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Bandit error: {e}")
        
        return issues
    
    def _run_semgrep(self, filepath, language):
        """Run Semgrep pattern matching (all languages)"""
        issues = []
        try:
            # Use auto-config which detects language and applies appropriate rules
            result = subprocess.run(
                [
                    'semgrep',
                    '--config', 'auto',  # Auto-detect rules based on language
                    '--json',
                    '--quiet',
                    filepath
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.stdout:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    issues.append({
                        'tool': 'Semgrep',
                        'severity': issue.get('extra', {}).get('severity', 'INFO'),
                        'line': issue['start']['line'],
                        'code': issue['check_id'],
                        'description': issue['extra']['message']
                    })
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            print(f"⚠️ Semgrep error: {e}")
        
        return issues
    
    def format_issues_for_llm(self, issues):
        """
        Format static analysis issues for LLM context (multi-language)
        
        Args:
            issues: Results from analyze_file()
            
        Returns:
            str: Formatted issues for LLM prompt
        """
        if not issues['bandit_issues'] and not issues['semgrep_issues']:
            return f"No security or pattern issues detected by static analysis ({issues.get('language', 'unknown')})."
        
        formatted = f"## Static Analysis Findings ({issues.get('language', 'unknown').upper()}):\n\n"
        
        # Bandit issues (Python only)
        if issues['bandit_issues']:
            formatted += "### Security Issues (Bandit):\n"
            for issue in issues['bandit_issues']:
                formatted += f"- **Line {issue['line']}** [{issue['severity']}/{issue['confidence']}]: {issue['description']}\n"
            formatted += "\n"
        
        # Semgrep issues (all languages)
        if issues['semgrep_issues']:
            formatted += "### Code Patterns (Semgrep):\n"
            for issue in issues['semgrep_issues']:
                formatted += f"- **Line {issue['line']}** [{issue['severity']}]: {issue['description']}\n"
            formatted += "\n"
        
        return formatted
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Cleanup error: {e}")
