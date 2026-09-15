## OceanBase Community Edition

小さく始めるならOSS版が良いだろう。Prometheusも対応しているみたいなので可視化もバッチリ。
ちなみにコンポーネントは5つあるが、そのうち3つが重要、あと2つはPrometheusとGrafanaなので実質可視化コンポーネント

- [OceanBase Community Editionクイックスタート](https://jp.oceanbase.com/docs/common-oceanbase-database-1000000000011372)

## dockerでの起動

```bash
docker run -p 2881:2881 --name oceanbase-ce -e MODE=mini -d oceanbase/oceanbase-ce
```

小さく起動する場合は以下のコマンドを実行します。

```bash
docker run \
  --name oceanbase-ce \
  --ulimit nofile=65535:65535 \
  -p 2881:2881 \
  -e MODE=mini \
  -d oceanbase/oceanbase-ce
```

実際にクライアントを接続します。

```bash
docker exec -it oceanbase-ce obclient -h127.0.0.1 -P2881 -uroot
```

## トラブルシューティング

起動時にコンテナ終了している場合はログを確認します。

```bash
docker logs oceanbase-ce
```

イメージのプラットフォームやアーキテクチャを確認します。

```bash
docker inspect oceanbase-ce --format '{{.Platform}} {{.State.ExitCode}} {{.State.Error}}'
uname -m
docker info --format '{{.Architecture}}'
```

コンテナに入るには以下のコマンドを実行します。

```bash
docker exec -it oceanbase-ce bash
```

## クラスターの表示

```bash
obd cluster display obcluster
```

## 設定を確認と修正

コンテナの設定を確認する方法は以下のとおりです。

```bash
docker start oceanbase-ce
docker exec -it oceanbase-ce bash
```

設定を修正します。

```bash
obd cluster edit-config obcluster
```

## 片付け

コンテナを削除します。

```bash
docker rm oceanbase-ce
```

## メモ

```
Codespaces 4-core / 16GB級環境では、実リソースとして約13GiB available memoryがあるにもかかわらず、OBDは約178MiB freeとして警告する。またCodespacesのroot filesystemと大容量一時領域の配置差により、OceanBaseのデフォルトDocker deploymentがdisk precheckで失敗する。
```

OceanBaseをGitHub Codespacesで起動するときのスペック

```bash
obd cluster edit-config obcluster
```

Configは以下のとおりです。

```text
Search param plugin and load ok
oceanbase-ce:
  servers:
  - 172.17.0.2
  global:
    home_path: /root/ob/observer
    mysql_port: 2881
    rpc_port: 2882
    zone: zone1
    appname: obcluster
    memory_limit: 4G
    system_memory: 1G
    datafile_size: 1G
    log_disk_size: 1G
    root_password:
    scenario: express_oltp
    obconfig_url:
    cpu_count: 4
    production_mode: false
    syslog_level: INFO
    enable_syslog_wf: false
    enable_syslog_recycle: true
    max_syslog_file_count: 4
    enable_rich_error_msg: true
```