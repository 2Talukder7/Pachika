import os
import re

patterns = [
    r"AIza[0-9A-Za-z-_]{35}",
    r"sk-[0-9A-Za-z]{20,}",
    r"(?i)api[_-]?key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
]

found = []
for root, dirs, files in os.walk("."):
    if ".git" in root or "__pycache__" in root or "venv" in root:
        continue
    for f in files:
        if f.endswith((".py", ".html", ".js", ".css", ".json", ".env", ".example", ".txt", ".bat", ".sh")):
            p = os.path.join(root, f)
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read()
                for pat in patterns:
                    for match in re.findall(pat, content):
                        if "your_" not in match.lower() and "placeholder" not in match.lower():
                            found.append((p, match))
            except Exception as e:
                pass

if found:
    print(f"FAILED: Found {len(found)} potential secrets:")
    for path, sec in found:
        print(f" - {path}: {sec}")
else:
    print("PASS: Zero hardcoded API keys or credentials detected across all repository files.")
