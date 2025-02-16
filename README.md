# TextToSpeak （Discord 読み上げボット）

## 概要

この Discord ボットは、VC（ボイスチャンネル）への自動参加や読み上げ機能を提供するボットです。

- スラッシュコマンドを使用した VC 参加・退出
- VC への自動参加・退出
- VC 参加ログの記録
- VC 内のテキストチャットを読み上げ
- 読み上げ辞書機能
- 無視リスト（発言を読み上げないユーザーや単語の設定）

スラッシュコマンドによる設定（辞書登録など）の変更はできません。手動でファイルを書き直してください。

## インストールとセットアップ

### 必要な Python パッケージのインストール

このボットを動作させるためには以下の Python パッケージが必要です。

まず、Python がインストールされていることを確認してください。Python 3.8 以上を推奨します。

コマンドプロンプトを開いて、以下のコマンドをコピーして貼り付け、実行してください。

```sh
pip install discord.py python-dotenv gtts emoji
```

仮想環境を使用する場合は、以下のコマンドを実行してください。

### ENVファイルの設定

`GAPI.env` というファイルを開いて、以下のように設定してください。

```
DISCORD_BOT_TOKEN=あなたが作成したボットトークン
DISCORD_GUILD_ID=サーバーのID
DISCORD_APPLICATION_ID=ボットのアプリケーションID
DISCORD_VC_AUTOJOIN01=自動接続する VC の ID
DISCORD_VC_LOG=VC ログを記録するテキストチャンネルの ID
```

### ボットトークン

Discord の開発者ポータル（[Discord Developer Portal](https://discord.com/developers/applications)）にアクセスし、新規アプリケーションを作成します。
「Bot」タブから新規ボットを作成し、「TOKEN」を取得してください。

### サーバーのID

Discord のサーバーアイコンを右クリックし、「IDをコピー」を選択して取得します。

### ボットのアプリケーションID

Discord の開発者ポータルでボットを作成した際の「APPLICATION ID」をコピーしてください。これは「OAuth2」タブに表示されます。

### 自動接続するVCのID

Discord サーバー内のボイスチャンネルを右クリックし、「IDをコピー」を選択して取得します。

### ログを記録するテキストチャンネルのID

VC にユーザーの入室があった場合にログを記録するテキストチャンネルの ID をコピーしてください。

### ボットの起動

コマンドプロンプトを開き、ボットのスクリプトがあるフォルダへ移動してください。

Cドライブに保存している場合:

```sh
cd C:\path\to\your\bot
```

Dドライブなどのサブドライブに保存している場合:

```sh
d:
cd \path\to\your\bot
```

以下のコマンドを実行してボットを起動します。

```sh
python bot.py
```

または、Windows で `Start_bot.bat` をダブルクリックして起動できます。\
この`Start_bot.bat`はDドライブで動作する事を前提として作成しています。\


起動後、コマンドプロンプトターミナルに `✅ Discord Botが起動しました` というメッセージが表示されることを確認してください。

エラーが発生した場合は、GAPI.env内のコードや依存パッケージのインストールを見直してください。

## 機能の詳細

### スラッシュコマンド（`SlashCommand.py`）

| コマンド  | 説明      |
| ----- | ------- |
| `/jv` | VC に参加  |
| `/dv` | VC から退出 |



必要の無い機能は以下のファイルを削除するだけでも機能します

### VC 自動参加・退出（`vcjoin.py`）

- 指定した VC にユーザーが参加した際、ボットが自動で参加
- 最後のユーザーが退出するとボットも自動退出

### VC 参加ログ（`vclog.py`）

- VC 参加時にログチャンネルへメッセージを送信
- 無視リスト（`Ignorelog.json`）に登録されたユーザー、ロール、VC は記録しない

### VC 読み上げ機能（`vcread.py`）

- テキストチャンネルのメッセージを音声合成（gTTS）で読み上げ
- 読み上げ辞書（`dictionary.json`）を使用し、指定された単語を別の読み方に変更可能
- 無視リスト（`ignoreprefix.json`）に登録されたプレフィックスを含むメッセージは読み上げない

## カスタマイズ

### 読み上げ辞書の編集

`dictionary.json` に以下の形式で単語の読み方を登録できます。

```json
{
  "早急": "そうきゅう",
  "貼付": "ちょうふ"
}
```

### 無視リストの編集

`Ignorelog.json` で、無視するユーザー・ロール・VC を設定できます。

```json
{
  "users": ["1234567890"],
  "roles": ["1234567890"],
  "vcs": ["1234567890"]
}
```

## 注意点

- ボットのトークンは漏洩しないように `.env` に保存してください。
- Discord の開発者ポータルで適切な `Intents` を有効にしてください（`message_content`、`voice_states` など）。

## ライセンス

MIT License

