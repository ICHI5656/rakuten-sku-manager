# Supabase セットアップガイド

## 新しいPCでSupabaseを使用するための設定手順

### 1. 必要なファイルの確認

別のPCでシステムを動かす場合、以下のファイルが必要です：

#### 1.1 `.env`ファイルの作成
`backend/.env`ファイルを作成し、Supabaseの認証情報を設定します。

```bash
cd backend
cp .env.supabase .env
```

#### 1.2 `.env`ファイルの編集
以下の項目を実際の値に置き換えてください：

```env
# 必須項目
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here

# オプション（管理者権限が必要な操作用）
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Supabaseモードを有効化
USE_SUPABASE=true
```

**重要**: Supabaseの認証情報は以下から取得できます：
1. [Supabase Dashboard](https://app.supabase.com)にログイン
2. プロジェクトを選択
3. Settings → API から以下を取得：
   - Project URL → `SUPABASE_URL`
   - anon public key → `SUPABASE_ANON_KEY`
   - service_role key → `SUPABASE_SERVICE_ROLE_KEY`（秘密にしてください）

### 2. Dockerを使用する場合

#### 2.1 Dockerコンテナの起動
```bash
# Windowsの場合
start-local.bat

# または手動で
docker-compose up -d
```

#### 2.2 依存関係の確認
Dockerイメージには必要なパッケージが含まれているため、追加インストールは不要です。

### 3. ローカル環境で直接実行する場合

#### 3.1 Python依存関係のインストール
```bash
cd backend
pip install -r requirements.txt
```

必要なパッケージ：
- `supabase==2.0.3`
- `python-dotenv==1.0.0`
- `psycopg2-binary==2.9.9`

#### 3.2 接続テスト
```bash
python test_supabase_connection.py
```

### 4. トラブルシューティング

#### 問題1: "supabaseパッケージがインストールされていません"
**解決方法**:
```bash
pip install supabase==2.0.3
```

#### 問題2: "SUPABASE_URLまたはキーが設定されていません"
**解決方法**:
1. `.env`ファイルが`backend/`ディレクトリに存在することを確認
2. 環境変数が正しく設定されていることを確認
3. Dockerの場合、コンテナを再起動:
   ```bash
   docker-compose restart backend
   ```

#### 問題3: "device_attributesテーブルへの接続に失敗しました"
**解決方法**:
1. Supabaseダッシュボードでテーブルが作成されているか確認
2. 必要に応じてテーブルを作成:
   ```bash
   python create_supabase_tables.py
   ```

#### 問題4: ネットワーク接続エラー
**解決方法**:
1. インターネット接続を確認
2. ファイアウォール/プロキシ設定を確認
3. Supabaseプロジェクトがアクティブであることを確認

### 5. SQLiteモードへのフォールバック

Supabaseが使用できない場合、SQLiteモードで動作させることができます：

#### 5.1 `.env`ファイルの設定
```env
USE_SUPABASE=false
```

#### 5.2 SQLiteデータベースの確認
`backend/product_attributes_new.db`ファイルが存在することを確認。
存在しない場合は、システムが自動的に作成します。

### 6. データの移行

既存のデータをSupabaseに移行する場合：

```bash
cd backend
python migrate_to_supabase.py
```

このスクリプトは：
- SQLiteからデータを読み込み
- Supabaseテーブルにデータを転送
- 重複を避けて安全に移行

### 7. 動作確認

#### 7.1 ブラウザでアクセス
```
http://localhost:3000
```

#### 7.2 機能テスト
1. CSVファイルのアップロード
2. デバイス管理画面の表示
3. ブランド選択の動作確認
4. データのエクスポート

### 8. セキュリティに関する注意事項

⚠️ **重要**:
- `.env`ファイルをGitにコミットしない
- `SUPABASE_SERVICE_ROLE_KEY`は秘密にする
- 本番環境では適切なCORS設定を行う
- 定期的にキーをローテーションする

### 9. サポート

問題が解決しない場合：
1. `docker-compose logs backend`でログを確認
2. `test_supabase_connection.py`で診断を実行
3. Supabaseダッシュボードでプロジェクトステータスを確認

---

## クイックチェックリスト

- [ ] `.env`ファイルが`backend/`に存在する
- [ ] `SUPABASE_URL`が設定されている
- [ ] `SUPABASE_ANON_KEY`が設定されている
- [ ] `USE_SUPABASE=true`が設定されている
- [ ] Dockerコンテナが起動している（Docker使用時）
- [ ] supabaseパッケージがインストールされている（ローカル実行時）
- [ ] インターネット接続が可能
- [ ] Supabaseプロジェクトがアクティブ