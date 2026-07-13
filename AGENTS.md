# 手順

## uvによる環境構築

環境が存在しない場合は初回だけ、uvをインストールする必要があります。
uvは、Pythonの仮想環境を簡単に作成・管理するためのツールです。以下の手順で環境を構築します。

```bash
# uvのインストール
pip install uv
```

環境を作成するには、以下のコマンドを実行します。

```bash
# 新しい仮想環境の作成
uv venv .venv
```

## uvによる環境の有効化

環境を有効化するには、以下のコマンドを実行します。

```bash
# 環境の有効化
. .venv/bin/activate
```

## SeekDBのインストール

SeekDBをインストールするには、以下のコマンドを実行します。

```bash
# SeekDBのインストール
uv run pip install -U pyseekdb
```

## 最初のスクリプト

最初のスクリプトをseekdbディレクトリに作成します。以下の内容を`seekdb/first_script.py`として保存してください。

## スクリプトを実行

最初のスクリプトを実行するには、以下のコマンドを実行します。

```bash
uv run seekdb/first_script.py
```
