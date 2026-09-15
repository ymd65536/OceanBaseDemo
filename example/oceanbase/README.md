## OceanBase Community Edition

小さく始めるならOSS版が良いだろう。Prometheusも対応しているみたいなので可視化もバッチリ。
ちなみにコンポーネントは5つあるが、そのうち3つが重要、あと2つはPrometheusとGrafanaなので実質可視化コンポーネント

- [OceanBase Community Editionクイックスタート](https://jp.oceanbase.com/docs/common-oceanbase-database-1000000000011372)

## dockerでの起動

```bash
docker run -p 2881:2881 --name oceanbase-ce -e MODE=mini -d oceanbase/oceanbase-ce
```

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

```bash
obd cluster edit-config obcluster
```

## 片付け

コンテナを削除します。

```bash
docker rm oceanbase-ce
```
