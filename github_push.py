#!/usr/bin/env python3
"""
GitHubセキュリティチェック付き自動プッシュスクリプト
Fishing Log V2.2 専用

使い方:
  python3 github_push.py "コミットメッセージ"
  python3 github_push.py "dashboard.html: グラフ表示を改善"

Dispatchからの指示例:
  "修正完了後、github_push.py を実行してGitHubにアップしてください"
"""

import sys
import os
import subprocess
from datetime import datetime

# ========== 設定 ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_SCRIPT = os.path.join(SCRIPT_DIR, 'check_secrets.py')

def run_command(cmd, cwd=None, capture=True):
    """コマンドを実行して結果を返す"""
    result = subprocess.run(
        cmd, shell=True, capture_output=capture, text=True, cwd=cwd or SCRIPT_DIR
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def check_git_config():
    """git の設定確認"""
    code, name, _ = run_command('git config user.name')
    code2, email, _ = run_command('git config user.email')
    if not name or not email:
        print("❌ git の設定が不完全です。")
        print("   以下のコマンドで設定してください：")
        print('   git config --global user.name "あなたの名前"')
        print('   git config --global user.email "your@email.com"')
        return False
    print(f"✅ git ユーザー: {name} <{email}>")
    return True

def check_remote():
    """リモートリポジトリの確認"""
    code, remote, _ = run_command('git remote get-url origin')
    if code != 0 or not remote:
        print("❌ GitHubリポジトリが設定されていません。")
        print("   以下のコマンドで設定してください：")
        print('   git remote add origin https://github.com/あなたのユーザー名/リポジトリ名.git')
        return False
    print(f"✅ リモートリポジトリ: {remote}")
    return True

def main():
    print("=" * 60)
    print("🚀 GitHub セキュリティチェック付き自動プッシュ")
    print(f"   実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # コミットメッセージ
    if len(sys.argv) > 1:
        commit_msg = ' '.join(sys.argv[1:])
    else:
        commit_msg = f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    print(f"\n📝 コミットメッセージ: {commit_msg}")

    # ── STEP 1: git 設定確認 ──
    print("\n【STEP 1】git 設定確認")
    if not check_git_config():
        sys.exit(1)

    # ── STEP 2: リモートリポジトリ確認 ──
    print("\n【STEP 2】リモートリポジトリ確認")
    if not check_remote():
        sys.exit(1)

    # ── STEP 3: セキュリティスキャン ──
    print("\n【STEP 3】セキュリティスキャン実行中...")
    code, stdout, stderr = run_command(f'python3 "{CHECK_SCRIPT}" "{SCRIPT_DIR}"', capture=False)

    if code != 0:
        print("\n❌ セキュリティチェック失敗 - プッシュを中止しました。")
        print("   上記の問題を修正してから再度実行してください。")
        sys.exit(1)

    print("\n✅ セキュリティチェック通過！")

    # ── STEP 4: ステージング ──
    print("\n【STEP 4】ファイルをステージング中...")

    # 変更されたファイルを確認
    code, status, _ = run_command('git status --short')
    if not status:
        print("  ℹ️  変更されたファイルはありません。プッシュをスキップします。")
        sys.exit(0)

    print(f"  変更ファイル:\n{status}")

    code, out, err = run_command('git add -A')
    if code != 0:
        print(f"❌ git add 失敗: {err}")
        sys.exit(1)
    print("  ✅ ステージング完了")

    # ── STEP 5: コミット ──
    print("\n【STEP 5】コミット中...")
    code, out, err = run_command(f'git commit -m "{commit_msg}"')
    if code != 0:
        if 'nothing to commit' in out or 'nothing to commit' in err:
            print("  ℹ️  コミットするものがありません。")
            sys.exit(0)
        print(f"❌ git commit 失敗: {err}")
        sys.exit(1)
    print(f"  ✅ コミット完了")

    # ── STEP 6: プッシュ ──
    print("\n【STEP 6】GitHubへプッシュ中...")
    code, out, err = run_command('git push origin main', capture=False)
    if code != 0:
        # mainブランチがなければmasterを試す
        code2, out2, err2 = run_command('git push origin master', capture=False)
        if code2 != 0:
            # 初回プッシュの場合
            code3, out3, err3 = run_command('git push -u origin HEAD', capture=False)
            if code3 != 0:
                print(f"\n❌ プッシュ失敗。認証を確認してください。")
                print("   Personal Access Token が設定されているか確認してください。")
                sys.exit(1)

    print("\n" + "=" * 60)
    print("🎉 GitHubへのアップロード完了！")

    # リモートURLからGitHub PagesのURLを推測
    code, remote_url, _ = run_command('git remote get-url origin')
    if 'github.com' in remote_url:
        # https://github.com/user/repo.git → https://user.github.io/repo/
        parts = remote_url.replace('.git', '').replace('https://github.com/', '').split('/')
        if len(parts) >= 2:
            pages_url = f"https://{parts[0]}.github.io/{parts[1]}/"
            print(f"🌐 GitHub Pages URL: {pages_url}")
            print(f"   ※ GitHub Pages が有効な場合、数分後に更新されます")
    print("=" * 60)

if __name__ == '__main__':
    main()
