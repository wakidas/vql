# vql

Vim風キーバインドを搭載したTUIの軽量DBクライアント。

[Textual](https://github.com/Textualize/textual) フレームワークで構築されています。

## 機能

- PostgreSQLへの接続管理
- スキーマ・テーブル一覧のツリー表示
- テーブルデータの閲覧
- テーブル名のインクリメンタル検索
- Vim風キーバインド対応

## インストール

### 前提条件

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/)

### セットアップ

```bash
git clone https://github.com/wakidas/vql.git
cd vql
uv sync
```

## 使い方

```bash
uv run vql
```

起動すると接続先の選択画面が表示されます。PostgreSQLの接続情報を入力して接続してください。

## 開発

```bash
# 依存関係のインストール（開発用含む）
uv sync

# テストの実行
uv run pytest
```

## ライセンス

[MIT License](LICENSE)
