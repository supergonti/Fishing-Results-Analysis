# GitHub セットアップガイド
## Fishing Log V2.2 - Dispatchワークフロー構築手順

---

## 📋 全体の流れ

```
STEP 1: GitHubアカウント確認
STEP 2: GitHubリポジトリ作成
STEP 3: Personal Access Token (PAT) 取得
STEP 4: ローカルgit設定（パソコンで1回だけ実施）
STEP 5: GitHub Pagesを有効化
STEP 6: 初回アップロード
STEP 7: Dispatchワークフローの動作確認
```

---

## STEP 1: GitHubアカウント確認

https://github.com にアクセスし、ログインされているか確認してください。  
アカウントがない場合は無料で作成できます。

---

## STEP 2: GitHubリポジトリ作成

1. https://github.com/new にアクセス
2. 以下のように設定：
   - **Repository name**: `fishing-log-v2`（任意）
   - **Description**: `釣果データ解析ソフト V2.2`
   - **Public** を選択（GitHub Pagesを無料で使うため）
   - `Add a README file` は **チェックしない**（後でローカルからプッシュするため）
3. **「Create repository」** をクリック

---

## STEP 3: Personal Access Token (PAT) 取得

GitHubへのプッシュに必要な認証トークンです。

1. https://github.com/settings/tokens/new にアクセス
2. 設定：
   - **Note**: `fishing-log-cowork`（わかりやすい名前）
   - **Expiration**: `No expiration`（または1年）
   - **Scopes**: `repo` にチェック（これだけでOK）
3. **「Generate token」** をクリック
4. 表示されたトークン（`ghp_xxxxx...`）を **必ずコピーして保存**（一度しか表示されません！）

> ⚠️ このトークンはメモ帳等に一時保存してください。後のSTEP 4で使います。

---

## STEP 4: ローカルgit設定（パソコンで1回だけ）

**コマンドプロンプト**（またはPowerShell）で以下を実行してください。

### 4-1: git ユーザー設定
```bash
git config --global user.name "あなたの名前"
git config --global user.email "your@email.com"
```

### 4-2: 認証設定（PATを使う方法）
```bash
# Windows の認証情報マネージャーに保存（推奨）
git config --global credential.helper manager-core
```

### 4-3: フォルダをgitリポジトリとして初期化
```
フォルダパス:
C:\Users\super\OneDrive\Claude 取り扱いファイル\fishing log 開発　手動\fishing log 開発　釣果データ解析ソフト\釣果データ解析ソフト_v2
```

コマンドプロンプトで：
```bash
cd "C:\Users\super\OneDrive\Claude 取り扱いファイル\fishing log 開発　手動\fishing log 開発　釣果データ解析ソフト\釣果データ解析ソフト_v2"

git init
git remote add origin https://github.com/【あなたのユーザー名】/fishing-log-v2.git
```

### 4-4: 初回プッシュ
```bash
git add -A
git commit -m "Initial commit: Fishing Log V2.2"
git push -u origin main
```

> 初回プッシュ時にユーザー名とPATの入力を求められます：  
> - Username: あなたのGitHubユーザー名  
> - Password: **STEP 3で取得したPAT**（パスワードではありません！）

---

## STEP 5: GitHub Pages を有効化

1. https://github.com/【ユーザー名】/fishing-log-v2/settings/pages を開く
2. **Source**: `Deploy from a branch`
3. **Branch**: `main` / `/ (root)`
4. **「Save」** をクリック

数分後、以下のURLでdashboard.htmlが閲覧できます：
```
https://【ユーザー名】.github.io/fishing-log-v2/dashboard.html
```

---

## STEP 6: Dispatch ワークフローの動作確認

Dispatchへの指示テンプレート：

```
【Fishing Log V2.2 改良指示】

対象ファイル:
C:\Users\super\OneDrive\Claude 取り扱いファイル\fishing log 開発　手動\fishing log 開発　釣果データ解析ソフト\釣果データ解析ソフト_v2\dashboard.html

修正内容:
（ここに具体的な修正内容を記載）

完了後:
以下のコマンドでGitHubにプッシュしてください：
  python3 github_push.py "修正内容の説明"

プッシュ前に check_secrets.py が自動実行され、
APIキー等の漏洩チェックが行われます。
```

---

## 📱 スマホでの確認方法

GitHub Pagesを有効にすると、スマホブラウザで直接閲覧できます：
```
https://【ユーザー名】.github.io/fishing-log-v2/dashboard.html
```

または、GitHubリポジトリの `dashboard.html` を直接開く方法：
1. スマホでGitHubアプリまたはブラウザを開く
2. リポジトリページを開く
3. `dashboard.html` → `Raw` ボタン

---

## 🔒 セキュリティチェックの仕組み

```
github_push.py を実行
    ↓
check_secrets.py が自動起動
    ↓
【10種類以上のスキャン】
  ・カスタム正規表現（200以上のパターン）
  ・detect-secrets（業界標準ツール）
    ↓
問題なし → git add → commit → push
問題あり → プッシュ中止・詳細レポート表示
```

---

## 🛠️ トラブルシューティング

### プッシュ時に認証エラーが出る場合
```bash
# 認証情報をリセットして再入力
git credential-manager erase
# 次のプッシュ時に再度ユーザー名とPATを入力
```

### ブランチ名エラー（main/masterの問題）
```bash
# 現在のブランチ名を確認
git branch

# mainに変更する場合
git branch -M main
```

### GitHub Pagesが表示されない場合
- リポジトリの Settings → Pages で設定を確認
- `main` ブランチが存在するか確認
- 初回は5〜10分かかることがある
