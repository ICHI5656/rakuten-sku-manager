# 商品属性（値）8 管理画面ガイド

## 概要
商品属性（値）8データベースを、画像で示されたようなテーブル形式で表示し、ブランド別にタブで切り替えられる専用管理画面を実装しました。

## アクセス方法
**URL**: http://localhost:3000/product-attributes-8

## 主な機能

### 1. ブランド別タブ切り替え
以下のブランドごとにタブで表示を切り替えられます：
- 🍎 **iPhone** - Apple製品
- 📱 **Xperia** - Sony製品
- 💧 **AQUOS** - Sharp製品
- 🌌 **Galaxy** - Samsung製品
- 🔷 **Pixel** - Google製品
- 🔴 **HUAWEI** - Huawei製品
- ➡️ **arrows** - 富士通製品
- 📱 **その他** - 上記以外の製品

### 2. テーブル表示
画像のリクエスト通り、以下の列でデータを表示：
- **ID**: レコードID
- **device_name**: デバイス名（バリエーション項目選択肢2）
- **attribute_value**: 属性値（商品属性（値）8）
- **size_category**: サイズカテゴリー（カラーチップで視覚的に表示）
- **usage_count**: 使用回数
- **created_at**: 作成日時

### 3. ページネーション
- デフォルトで25件ずつ表示
- 行数を10、25、50、100から選択可能
- ページ移動ボタンで簡単にナビゲート

### 4. デバイス追加機能
各ブランドタブで「デバイス追加」ボタンから新規デバイスを追加可能：
- **device_name**: バリエーション項目選択肢2を入力
- **attribute_value**: 商品属性（値）8を入力
- **size_category**: サイズをドロップダウンから選択
  - [SS], [S], [M], [L], [LL], [2L], [3L], [4L], [i6]

## サイズカテゴリーの色分け
サイズは視覚的に区別しやすいようカラーチップで表示：
- 🔵 **青系** (info): [SS], [S]
- 🟢 **緑系** (success): [L]
- 🔷 **青** (primary): [M]
- 🟡 **黄系** (warning): [LL], [2L], [3L], [4L]
- ⚫ **グレー** (default): その他

## APIエンドポイント

### ブランド別デバイス取得
```
GET /api/multi-database/product_attributes_8/devices-by-brand?brand={brand}&limit={limit}&offset={offset}
```
パラメータ：
- `brand`: iphone, xperia, aquos, galaxy, pixel, huawei, arrows, other
- `limit`: 取得件数（最大100）
- `offset`: オフセット

### デバイス追加
```
POST /api/multi-database/product_attributes_8/add-device
```
リクエストボディ：
```json
{
  "size_category": "[L]",
  "variation_item_choice_2": "iPhone16 ProMax",
  "product_attribute_8": "iPhone 16 Pro Max"
}
```

## 使用方法

### 1. ブランド別表示
1. 上部のタブから表示したいブランドを選択
2. 自動的にそのブランドのデバイスが表示されます

### 2. 新規デバイス追加
1. 右上の「デバイス追加」ボタンをクリック
2. ダイアログでデバイス情報を入力
3. 「追加」ボタンをクリック
4. 自動的にリストが更新されます

### 3. ページング
1. テーブル下部のページネーションコントロールを使用
2. 「行数」ドロップダウンで表示件数を変更
3. 矢印ボタンでページを移動

## データ統計
現在のデータベースには以下のデータが登録されています：
- **総デバイス数**: 77件
- **サイズカテゴリー**: 8種類
- 各ブランドのデバイスがサイズ別に管理されています

## 技術仕様
- **フロントエンド**: React + TypeScript + Material-UI
- **バックエンド**: FastAPI + SQLite
- **データベース**: product_attributes_new.db
- **テーブル構造**:
  - product_devices: メインデバイステーブル
  - attribute_mappings: 属性マッピングテーブル
  - size_categories: サイズカテゴリーテーブル

## 注意事項
- 同じデバイスが異なるサイズで存在することを許可しています
- データ追加時は自動的に現在選択中のブランドに関連付けられます
- 削除・編集機能は今後の拡張として実装可能です