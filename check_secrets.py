"""
GitHubアップロード前 セキュリティスキャンスクリプト
APIキー・トークン・パスワード等の漏洩を検出する
"""
import re
import os
import sys

# 検出対象パターン
PATTERNS = [
    (r'api[_-]?key\s*[:=]\s*["\'][\w-]{10,}', "API Key"),
    (r'token\s*[:=]\s*["\'][\w-]{10,}', "Token"),
    (r'password\s*[:=]\s*["\'][^"\']{6,}', "Password"),
    (r'Bearer\s+[\w-]{20,}', "Bearer Token"),
    (r'secret\s*[:=]\s*["\'][\w-]{10,}', "Secret"),
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key"),
    (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
    (r'ghp_[0-9a-zA-Z]{36}', "GitHub Personal Access Token"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
]

# スキャン除外ファイル・フォルダ
EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', '.venv'}
EXCLUDE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf',
                '.zip', '.exe', '.dll', '.pyc'}

def scan_file(filepath):
    """1ファイルをスキャンして検出結果を返す"""
    findings = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                for pattern, label in PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append((lineno, label))
    except Exception:
        pass
    return findings

def scan_directory(target_dir):
    """ディレクトリ全体をスキャン"""
    all_findings = {}
    for root, dirs, files in os.walk(target_dir):
        # 除外フォルダをスキップ
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXCLUDE_EXTS:
                continue
            fpath = os.path.join(root, fname)
            findings = scan_file(fpath)
            if findings:
                all_findings[fpath] = findings
    return all_findings

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else '.'
    print(f"\n🔍 セキュリティスキャン開始: {os.path.abspath(target)}")
    print("-" * 50)

    findings = scan_directory(target)

    if not findings:
        print("✅ 問題なし：APIキー・トークン等は検出されませんでした")
        print("-" * 50)
        sys.exit(0)
    else:
        print(f"⚠️  警告：{len(findings)}ファイルで機密情報の可能性を検出しました\n")
        for fpath, items in findings.items():
            print(f"  📄 {fpath}")
            for lineno, label in items:
                print(f"     → 行{lineno}: {label} の可能性")
        print("-" * 50)
        print("❌ GitHubへのアップロードを中止してください")
        print("   上記のファイルを確認し、機密情報を除去してから再実行してください")
        sys.exit(1)

if __name__ == '__main__':
    main()
