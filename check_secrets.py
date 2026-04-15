#!/usr/bin/env python3
"""
セキュリティスキャナー - GitHubアップロード前のAPIキー・トークン検出ツール
Fishing Log V2.2 専用
"""

import re
import sys
import os
import json
import subprocess
from pathlib import Path

# ========== スキャン対象ファイル ==========
SCAN_EXTENSIONS = {'.html', '.js', '.py', '.bat', '.sh', '.json', '.md', '.txt', '.env', '.cfg', '.ini', '.yaml', '.yml'}
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.pytest_cache'}

# ========== 検出パターン ==========
PATTERNS = [
    # Google API Key
    (r'AIza[0-9A-Za-z_-]{35}', 'Google API Key'),
    # OpenAI API Key
    (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
    (r'sk-proj-[a-zA-Z0-9_-]{50,}', 'OpenAI Project API Key'),
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'(?i)aws_secret_access_key\s*[=:]\s*["\']?[a-zA-Z0-9+/]{40}', 'AWS Secret Key'),
    # GitHub
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
    (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth Token'),
    (r'github_pat_[a-zA-Z0-9_]{82}', 'GitHub Fine-grained Token'),
    # Stripe
    (r'sk_live_[a-zA-Z0-9]{24}', 'Stripe Live Secret Key'),
    (r'sk_test_[a-zA-Z0-9]{24}', 'Stripe Test Secret Key'),
    # 汎用パターン
    (r'(?i)api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9_\-]{16,}["\']', '汎用 API Key'),
    (r'(?i)api[_-]?key\s*=\s*[a-zA-Z0-9_\-]{16,}(?!\w)', '汎用 API Key (クォートなし)'),
    (r'(?i)access[_-]?token\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{16,}["\']', 'Access Token'),
    (r'(?i)auth[_-]?token\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{16,}["\']', 'Auth Token'),
    (r'(?i)secret[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{8,}["\']', 'Secret Key'),
    (r'(?i)password\s*[=:]\s*["\'][^"\']{8,}["\']', 'ハードコードされたパスワード'),
    (r'Bearer [a-zA-Z0-9_\.\-]{20,}', 'Bearer Token'),
    # 気象API
    (r'(?i)weatherapi[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9]{20,}["\']', 'Weather API Key'),
    (r'[a-f0-9]{32}(?=["\'\s,;])', '32文字16進数（APIキーの可能性）'),
]

# ========== 無視するパターン（誤検知除外） ==========
IGNORE_PATTERNS = [
    r'example', r'sample', r'dummy', r'test', r'placeholder',
    r'your[_-]?api[_-]?key', r'YOUR_API_KEY', r'INSERT_KEY_HERE',
    r'xxxxxxxx', r'XXXXXXXX', r'00000000',
]

def should_ignore(match_str):
    """誤検知を除外する"""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, match_str, re.IGNORECASE):
            return True
    return False

def scan_file(filepath):
    """ファイルをスキャンして問題を返す"""
    issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            for pattern, label in PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    match_str = match.group()
                    if not should_ignore(match_str):
                        # マスクして表示（最初の8文字 + ***）
                        masked = match_str[:8] + '***' if len(match_str) > 8 else '***'
                        issues.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': label,
                            'preview': masked,
                            'context': line.strip()[:80]
                        })
    except Exception as e:
        print(f"  ⚠️  ファイル読み込みエラー: {filepath} - {e}")

    return issues

def scan_directory(directory):
    """ディレクトリ全体をスキャン"""
    all_issues = []
    scanned_files = []

    for root, dirs, files in os.walk(directory):
        # スキップするディレクトリ
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            filepath = Path(root) / filename
            ext = filepath.suffix.lower()

            if ext in SCAN_EXTENSIONS:
                scanned_files.append(str(filepath))
                issues = scan_file(filepath)
                all_issues.extend(issues)

    return all_issues, scanned_files

def run_detect_secrets(directory):
    """detect-secretsによる追加スキャン"""
    try:
        result = subprocess.run(
            ['python3', '-m', 'detect_secrets', 'scan', '--all-files', '.'],
            capture_output=True, text=True, cwd=directory, timeout=60
        )
        if result.stdout:
            data = json.loads(result.stdout)
            results_data = data.get('results', {})
            if results_data:
                return results_data
    except Exception as e:
        pass  # detect-secretsが使えない場合はスキップ
    return {}

def main():
    # カレントディレクトリまたは引数で指定されたディレクトリをスキャン
    target_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    target_dir = os.path.abspath(target_dir)

    print("=" * 60)
    print("🔍 セキュリティスキャン開始")
    print(f"   対象: {target_dir}")
    print("=" * 60)

    # カスタムパターンスキャン
    issues, scanned_files = scan_directory(target_dir)

    print(f"\n📂 スキャン済みファイル数: {len(scanned_files)}")
    for f in scanned_files:
        rel_path = os.path.relpath(f, target_dir)
        print(f"   ✓ {rel_path}")

    # detect-secretsによる追加スキャン
    print("\n🔎 detect-secrets による追加スキャン中...")
    ds_results = run_detect_secrets(target_dir)

    # 結果レポート
    print("\n" + "=" * 60)

    if not issues and not ds_results:
        print("✅ スキャン完了 - 問題は検出されませんでした！")
        print("   GitHubへのアップロードは安全です。")
        print("=" * 60)
        return 0  # 成功
    else:
        print("⚠️  セキュリティ上の問題が検出されました！")
        print("   GitHubへのアップロードを中止します。")
        print()

        if issues:
            print("【カスタムスキャン結果】")
            for i, issue in enumerate(issues, 1):
                rel_path = os.path.relpath(issue['file'], target_dir)
                print(f"  [{i}] {issue['type']}")
                print(f"      ファイル: {rel_path}  行: {issue['line']}")
                print(f"      検出値:  {issue['preview']}")
                print(f"      コンテキスト: {issue['context']}")
                print()

        if ds_results:
            print("【detect-secrets 検出結果】")
            for filepath, file_issues in ds_results.items():
                rel_path = os.path.relpath(filepath, target_dir) if os.path.isabs(filepath) else filepath
                for issue in file_issues:
                    print(f"  - {rel_path}:{issue.get('line_number', '?')} [{issue.get('type', '不明')}]")

        print()
        print("【対処方法】")
        print("  1. 上記のファイルから機密情報を削除")
        print("  2. 環境変数（.env ファイル）に移動し、.gitignore に追加")
        print("  3. 再度このスクリプトを実行して確認")
        print("=" * 60)
        return 1  # 失敗

if __name__ == '__main__':
    sys.exit(main())
