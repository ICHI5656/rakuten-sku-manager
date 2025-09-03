================================================================================
楽天SKU管理システム - ローカル環境セットアップガイド（メモ帳用）
================================================================================

【必要なソフトウェア】

1. Docker Desktop
   - Windows版: https://docs.docker.com/desktop/install/windows-install/

2. Git 
   - ダウンロード: https://git-scm.com/downloads


【セットアップ手順】

■ Step 1: GitHubからダウンロード

コマンドプロンプトで実行:

  git clone https://github.com/ICHI5656/rakuten-sku-manager.git
  cd rakuten-sku-manager


■ Step 2: Docker Desktopを起動

  1. Docker Desktopアプリを起動
  2. タスクトレイで緑色のアイコンになるまで待つ


■ Step 3: システムを起動

Windows の場合:
  start-local.bat をダブルクリック

または、コマンドプロンプトで:
  docker-compose up -d


■ Step 4: ブラウザでアクセス

  フロントエンド: http://localhost:3000
  API: http://localhost:8000/docs


【よく使うコマンド】

システム起動:
  docker-compose up -d

システム停止:
  docker-compose down

ログ確認:
  docker-compose logs -f

再起動:
  docker-compose restart


【ネットワーク共有する場合】

■ Step 1: ファイアウォール設定（管理者権限で実行）
  configure-firewall.bat

■ Step 2: ネットワーク共有モードで起動
  start-network.bat

■ Step 3: 他のPCからアクセス
  表示されたIPアドレスを使用
  例: http://192.168.1.100:3000


【トラブルシューティング】

ポート使用中エラーの場合:
  docker-compose.yml でポート番号を変更
  例: 3000 → 3001

Dockerメモリ不足の場合:
  Docker Desktop設定でメモリを4GB以上に

アクセスできない場合:
  1. Docker Desktopが起動しているか確認
  2. docker-compose ps でコンテナ状態確認
  3. ファイアウォール設定を確認


【更新方法】

1. コンテナ停止
   docker-compose down

2. 最新版を取得
   git pull origin master

3. 再ビルド
   docker-compose build --no-cache

4. 起動
   docker-compose up -d


【サポート】

GitHubイシュー:
https://github.com/ICHI5656/rakuten-sku-manager/issues

================================================================================