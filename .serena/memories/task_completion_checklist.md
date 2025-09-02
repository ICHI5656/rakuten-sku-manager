# タスク完了時のチェックリスト

## 必須確認項目
1. [ ] Dockerコンテナが正常起動している
2. [ ] APIエンドポイントが応答する
3. [ ] フロントエンドビルドが成功する
4. [ ] デバッグログを削除またはコメントアウト
5. [ ] エラーハンドリングが適切

## テスト項目
1. [ ] 単一ファイルアップロード
2. [ ] 機種追加（先頭、末尾、特定位置）
3. [ ] カスタム順序指定
4. [ ] バッチ処理
5. [ ] データベース保存

## コマンド実行
```bash
# ビルドテスト
docker exec rakuten-sku-frontend npm run build

# API動作確認
curl http://localhost:8000/api/product-attributes/brands

# ログ確認（エラーがないこと）
docker logs --tail 100 rakuten-sku-backend | grep ERROR
```

## 品質チェック
- 日本語コメントが適切
- エンコーディング処理が正しい（Shift-JIS）
- 機種順序が期待通り
- SKU採番が正常