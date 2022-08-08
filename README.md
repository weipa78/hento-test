# hento-sam

このアプリケーションはクロスワードデータの作成、取得、削除などができるAPIを提供しています。

## 環境

このディレクトリは[AWS SAM](https://docs.aws.amazon.com/ja_jp/serverless-application-model/latest/developerguide/what-is-sam.html)を利用し、作成しています。AWS SAMを利用することで利用するAWSリソースをコードで管理することができ、コマンドでローカルの変更をデプロイすることが可能です。

使用ツールや言語は以下となっています。
括弧内にプロジェクト作成時のバージョンを記述していますが、基本的に最新のものを使用してください。

- python 3.9.* (3.9.13)
- SAM CLI (1.53.0)
- AWS CLI (2.7.16)
- Visual Studio Code (1.69.2)

## ディレクトリ構成

- **app**
	Lambdaアプリケーションのコードが含まれています。デプロイ後、AWSマネジメントコンソールの対応するLambdaの画面でソースコードを確認することができます。

- **lib**
	Lambdaのレイヤーとして扱いたいコードを配置しています。genxwordディレクトリは、githubの[genxword](https://github.com/riverrun/genxword)のコードをこのプロジェクト用に編集したものです。

- **tests**
	- **data**
		テスト用のデータが含まれています。
	- **unit**
		ユニットテストのコードが含まれています。

- **tools**
	pythonコマンドで実行するファイルを配置しています。

- **.vscode**
	vscodeの設定ファイルが含まれます。開発環境をそろえるためにコミットしています。

## 環境構築

pytestを行うことを目標に環境構築を行います。

1. このプロジェクトをgit cloneし、クローンしたディレクトリに移動します。
2. pythonの3.9系がインストールされていることを確認し、そのpythonを用いて.venvディレクトリに仮想環境を作成します。
	`python -m venv .venv`
3. 仮想環境を有効にし、必要なライブラリをインストールします。
	```
	source ./.venv/bin/activate
	pip install -r requirements.txt
	```
4. pytestを実行し、すべてのテストが成功することを確認します。
	`pytest tests`
5. 以上です。
