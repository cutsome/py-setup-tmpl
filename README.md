
# Python × Postgresql × Poetry 環境構築テンプレ

## Installation

- .env.example を .env にコピーし、中身を書く
- 下記をインストール
  - [postgresql](https://www.postgresql.org)
  - [poetry](https://github.com/python-poetry/poetry)
  - [hadolint](https://github.com/hadolint/hadolint)
- 以下コマンドで依存ライブラリのインストールと、commit 前にチェックをかけてくれる pre-commit hook を設定する
- （詳細は`./Makefile` を確認）

```bash
make install
```

## Development

hot reload する開発環境サーバーを立ち上げるには以下のコマンドを実行する

```sh
docker compose up
```

docker-compose.yml に定義したリソースを削除するには以下を実行する

```sh
docker volume rm py-setup-tmpl_db-volume # DB volumeの削除
docker compose down --rmi all --volumes --remove-orphans # 全ての削除
```

コミットには commitizen を使用する。 [参考](https://github.com/commitizen/cz-cli#conventional-commit-messages-as-a-global-utility)

```bash
git cz
```

自動アプデ, 自動リント, 自動テストコマンドは以下。

```bash
make update
make lint
make test
```

開発環境データベースに seeds を追加するには `sql/seeds/` 内のファイルを追加・更新し、以下のコマンドを実行する。  
その後、DB 用の docker volume を削除し、コンテナを再ビルドする。

```bash
make seeds
```
