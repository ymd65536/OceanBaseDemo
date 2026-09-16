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

## OceanBase CE on GitHub Codespaces

このリポジトリでは、GitHub Codespaces 上で OceanBase CE を短時間で起動し、開発・検証を開始できる Disposable Playground を提供します。

目的は本番相当の OceanBase クラスタを構築することではなく、Developer Experience と Time to First Query を重視した再現可能な検証環境を提供することです。

### 基本方針

Codespaces では OceanBase CE Docker Image を `MODE=SLIM` で起動します。

```bash
mkdir -p /tmp/oceanbase-volume

docker run \
  --name oceanbase-ce \
  --ulimit nofile=65535:65535 \
  -p 2881:2881 \
  -e MODE=SLIM \
  -v /tmp/oceanbase-volume:/mnt/oceanbase \
  -d oceanbase/oceanbase-ce
```

`/mnt/oceanbase` は dataset、dump、benchmark data、生成ファイルなどを配置する scratch space として使用します。

この環境は Disposable Playground です。

永続運用、性能評価、HA評価、本番相当の耐久性評価を目的とした環境ではありません。

---

## Known Issues / Troubleshooting

### 1. `MODE=MINI` で OceanBase が起動しない

#### 症状

`MODE=MINI` で起動すると OBD precheck で以下のようなエラーが発生する場合があります。

```text
open files ... ERROR
not enough memory
disk ... Avail: 4G, Need: 14G
```

OceanBase の設定を以下のように縮小しても、

```text
OB_MEMORY_LIMIT=4G
OB_DATAFILE_SIZE=1G
OB_LOG_DISK_SIZE=1G
```

ディスク容量不足が発生する場合があります。

```text
Avail: 4G, Need: 6G
```

#### 原因

Codespaces のホストに十分なディスク容量が存在していても、Docker の root filesystem は別の overlay filesystem を使用します。

検証時には概ね以下の状態でした。

```text
Docker Root Dir: /var/lib/docker

overlay:
32GB total
約4GB available
```

一方、Codespaces ホストの `/tmp` には約100GB以上の空き容量が存在しました。

`MODE=MINI` は通常の OBD deployment を実行し、OceanBase の datafile や log disk を確保するため、Codespaces の Docker overlay の空き容量では不足する場合があります。

#### 対処

Codespaces Playground では `MODE=MINI` ではなく `MODE=SLIM` を使用します。

```bash
-e MODE=SLIM
```

`SLIM` は prebuilt store を利用する fastboot path を使用します。

Time to First Query を重視する Disposable Playground では `SLIM` を使用してください。

---

### 2. Codespaces ホストの `/tmp` の空き容量が OceanBase コンテナから見えない

#### 症状

Codespaces ホストでは、

```bash
df -h /tmp
```

で100GB以上の空き容量が存在するにもかかわらず、OceanBase コンテナ内の `/tmp` では数GB程度しか利用できない場合があります。

#### 原因

OceanBase コンテナの `/tmp` は Codespaces ホストの `/tmp` ではありません。

通常は Docker の overlay filesystem 上に存在するため、Codespaces ホスト側の大容量 `/tmp` を自動的に利用できません。

#### 対処

大容量の一時領域が必要な場合は Codespaces ホストの `/tmp` を bind mount します。

```bash
mkdir -p /tmp/oceanbase-volume

docker run \
  --name oceanbase-ce \
  --ulimit nofile=65535:65535 \
  -p 2881:2881 \
  -e MODE=SLIM \
  -v /tmp/oceanbase-volume:/mnt/oceanbase \
  -d oceanbase/oceanbase-ce
```

確認:

```bash
docker exec oceanbase-ce df -h /mnt/oceanbase
```

`/tmp/oceanbase-volume` は永続ストレージとして扱わないでください。

このリポジトリでは scratch space として使用します。

---

### 3. `/root/ob/observer/store` を直接 bind mount すると OBD deploy が失敗する

#### 症状

OceanBase の内部 store directory を bind mount すると、以下のようなエラーが発生する場合があります。

```text
OBD-1002: Fail to init
home path: /root/ob/observer is not empty
```

#### 原因

OceanBase の内部 store directory を事前に bind mount すると、Docker によって対象ディレクトリが作成されます。

その結果、OBD が deployment directory を初期化するときに、既にディレクトリが使用されていると判定する場合があります。

#### 対処

以下のような OceanBase 内部ディレクトリへ直接 mount しないでください。

```text
/root/ob/observer/store
```

scratch space が必要な場合は OceanBase の管理対象外となるパスを使用します。

```text
/mnt/oceanbase
```

例:

```bash
-v /tmp/oceanbase-volume:/mnt/oceanbase
```

---

### 4. `open files` の precheck に失敗する

#### 症状

OBD precheck で `open files` に関する ERROR または WARN が発生します。

```text
The recommended number of open files ...
```

#### 原因

Codespaces ホスト側の `ulimit -n` が十分大きくても、Docker container 内の limit は別に設定されます。

ホスト側の値だけでは OceanBase コンテナへ反映されません。

#### 対処

Docker 起動時に `nofile` を明示します。

```bash
--ulimit nofile=65535:65535
```

SLIM 環境では OceanBase の推奨値より低いという WARN が残る場合があります。

ただし Disposable Playground では observer が `ACTIVE` になり SQL 接続できることを確認できれば、開発用途の環境として利用できます。

---

### 5. Dev Container の `docker-in-docker` Feature がインストールできない

#### 症状

Dev Container の構築中に以下のエラーが発生する場合があります。

```text
The 'moby' option is not supported on ubuntu 'resolute'
because 'moby-cli' and related system packages are not available
```

続いて以下のエラーになります。

```text
ERROR: Feature "Docker (Docker-in-Docker)" failed to install
```

#### 原因

`mcr.microsoft.com/devcontainers/base:ubuntu` が使用する Ubuntu version と、`docker-in-docker` Feature がデフォルトで使用する Moby package の組み合わせに互換性問題があります。

#### 対処

Dev Container Feature で Moby を無効化します。

```json
{
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {
      "moby": false
    }
  }
}
```

再現性を高める場合は、floating OS tag への依存を避け、検証済みの base image version を固定することも検討してください。

---

### 6. `postCreateCommand` から setup script が見つからない

#### 症状

Dev Container の作成自体は成功しても `postCreateCommand` で以下のエラーが発生する場合があります。

```text
bash: scripts/setup-oceanbase.sh: No such file or directory
```

または、

```text
postCreateCommand from devcontainer.json failed with exit code 127
```

#### 原因

`postCreateCommand` に指定した相対パスと、実際の repository layout が一致していません。

Dev Container configuration の移動や統合によって script directory が変更された場合、古いパスが `devcontainer.json` に残っている可能性があります。

#### 対処

推測でパスを変更せず、現在の repository layout を確認してください。

```bash
pwd
find . -maxdepth 4 -type f | sort
```

その結果に基づいて、Workspace root から解決できる正しいパスを `postCreateCommand` に指定します。

例:

```json
{
  "postCreateCommand": "bash scripts/setup-oceanbase.sh"
}
```

Dev Container configuration や scripts の配置を変更した場合は、必ず `postCreateCommand` も同時に確認してください。

---

### 7. `obd cluster start obcluster` が失敗する

#### 症状

SLIM モードで起動した OceanBase コンテナ内で、

```bash
obd cluster start obcluster
```

を実行すると以下のエラーになります。

```text
[ERROR] No such deploy: obcluster.
```

#### 原因

`MODE=MINI` と `MODE=SLIM` では OceanBase Docker Image の boot path が異なります。

概念的には以下の違いがあります。

```text
MODE=MINI
  ↓
normal boot
  ↓
OBD deploy
  ↓
obcluster
```

一方、SLIM は以下のように動作します。

```text
MODE=SLIM
  ↓
fastboot
  ↓
prebuilt store / configuration
  ↓
observer
  ↓
OBD deployment: demo
```

そのため SLIM 環境には `obcluster` という deployment が存在しません。

#### 対処

まず deployment を確認します。

```bash
obd cluster list
```

SLIM 環境では `demo` を操作してください。

状態確認:

```bash
obd cluster display demo
```

停止:

```bash
obd cluster stop demo
```

起動:

```bash
obd cluster start demo
```

実際に `demo` の stop/start 後、observer が `ACTIVE` になり SQL 接続できることを確認済みです。

---

### 8. SLIM 起動時に OS パラメータやメモリの WARN が出る

#### 症状

`obd cluster start demo` で以下のような WARN が発生する場合があります。

```text
The recommended value of fs.aio-max-nr is 1048576
The recommended number of open files is 655350
The recommended number of stack size is unlimited
The value of the "vm.max_map_count" ...
not enough memory
```

#### 原因

Codespaces は本番用 OceanBase host としてチューニングされた環境ではありません。

OceanBase / OBD が推奨する kernel parameters、resource limits、memory conditions と Codespaces の実行環境には差があります。

#### 対処

Disposable Playground では WARN と ERROR を区別してください。

以下まで正常に進んでいることを確認します。

```text
Start observer ok
observer program health check ok
Connect to observer 127.0.0.1:2881 ok
status ACTIVE
demo running
```

さらに SQL 接続を確認します。

```bash
obclient \
  -h127.0.0.1 \
  -P2881 \
  -uroot@sys \
  -Doceanbase \
  -A
```

WARN が存在していても SQL 接続まで成功していれば、Codespaces Playground の開発用途では利用できます。

ただし、性能評価、HA評価、本番相当評価ではこれらの WARN を無視しないでください。

---

## OceanBase Health Check

### Docker container の確認

```bash
docker ps --filter name=oceanbase-ce
```

### OBD deployment の確認

```bash
docker exec oceanbase-ce obd cluster display demo
```

### SQL 接続確認

```bash
docker exec oceanbase-ce \
  obclient \
  -h127.0.0.1 \
  -P2881 \
  -uroot@sys \
  -Doceanbase \
  -A \
  -e "SELECT VERSION(); SELECT 1;"
```

### 対話接続

```bash
docker exec -it oceanbase-ce \
  obclient \
  -h127.0.0.1 \
  -P2881 \
  -uroot@sys \
  -Doceanbase \
  -A
```

検証時には以下のバージョンで動作確認しています。

```text
OceanBase_CE 4.4.2.1
5.7.25-OceanBase_CE-v4.4.2.1
```

---

## OceanBase Codespaces Agent Rules

AI Agent が OceanBase Codespaces 環境を変更・調査するときは以下のルールを守ってください。

- Codespaces の Disposable Playground では原則として `MODE=SLIM` を使用する
- `MODE=MINI` と `MODE=SLIM` の boot path の違いを考慮する
- `obcluster` と `demo` を混同しない
- SLIM の OBD deployment name は `demo`
- deployment name が不明な場合は推測せず `obd cluster list` で確認する
- OceanBase 内部の `/root/ob/observer/store` を直接 bind mount しない
- 大容量 scratch data は `/mnt/oceanbase` を使用する
- Codespaces ホストの filesystem と Docker overlay filesystem を混同しない
- Dev Container configuration を変更した場合は `postCreateCommand` のパスも確認する
- ファイルパスが不明な場合は推測せず `pwd` と `find` で確認する
- setup 成功の判定は Docker container の起動だけで行わない
- observer の `ACTIVE` を確認する
- 最終的に SQL `SELECT 1` が成功するところまで確認する
- OBD の WARN と ERROR を区別する
- Codespaces Playground で発生する resource WARN を本番環境の設計判断へそのまま適用しない
- この環境の結果を本番性能、HA、durability の評価として扱わない
- Time to First Query と Developer Experience を優先する
