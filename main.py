import re
import subprocess
import argparse
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    "URL": r"https?://[^\s\"'<>]+",

    "Email": r"[a-zA-Z0-9._%+\-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,63}(?=\s|$|[^\w@.-])",

    "Domain": r"\b(?:(?!-)[a-zA-Z0-9-]{1,63}(?<!-)\.)+(?:com|net|org|io|dev|gov|edu|co|uk|me|app|xyz|cn|ru|top|club|info|biz)\b",

    "IPv4": r"\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}"
            r"(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b",

    "IPv6": r"\b(?:"
            r"(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,7}:|"
            r"(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|"
            r"(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|"
            r"[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|"
            r":(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)"
            r")\b",

    "Discord Webhook": r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/[0-9]{17,20}/[A-Za-z0-9_\-]{60,}",
}

COMPILED = {k: re.compile(v) for k, v in PATTERNS.items()}

RESET='\033[0m'
DIM='\033[2m'
BOLD='\033[1m'

COLORS = {
    "URL": '\033[36m',
    "Email": '\033[33m',
    "Domain": '\033[32m',
    "IPv4": '\033[35m',
    "IPv6": '\033[34m',
    "Discord Webhook": '\033[31m',
}

def colored(color, text):
    return f"{color}{text}{RESET}"

def is_binary(path):
    with open(path, "rb") as f:
        chunk = f.read(1024)
    text_chars = bytearray({7,8,9,10,12,13,27} | set(range(32,127)))
    return bool(chunk.translate(None, text_chars))

def get_text(path):
    if is_binary(path):
        return subprocess.run(["strings", path], capture_output=True, text=True).stdout
    with open(path, "r", errors="ignore") as f:
        return f.read()

def scan(text):
    results = defaultdict(set)
    for label, pattern in COMPILED.items():
        for m in pattern.finditer(text):
            results[label].add(m.group(0).strip())
    return results

def main():
    parser = argparse.ArgumentParser(description="Regex IOC extractor")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    text = get_text(args.file)
    results = scan(text)

    if not any(results.values()):
        print(colored("\033[31m", "nothing found."))
        return

    for label, matches in results.items():
        if not matches:
            continue
        color = COLORS.get(label, "")
        print(colored(BOLD + color, f"{label}") + colored(DIM, f" ({len(matches)} matches found)"))
        for m in sorted(matches):
            print(" ", colored(color, m))

if __name__ == "__main__":
    main()