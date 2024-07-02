# Google Speech-to-Text APIの使用方法

Google Speech-to-Text APIを使用して、オーディオファイルをテキストに変換する方法のステップバイステップガイドです。

## 前提条件

- Pythonがインストールされていること
- Google Cloud Platform (GCP) アカウントを持っていること

## ステップ1: GCPアカウントの設定

### GCPアカウントの作成

1. Google Cloud Platform のウェブサイトにアクセスし、アカウントを作成します。
2. 初めて利用する場合は、無料トライアルを利用できます。

### プロジェクトの作成

1. GCPダッシュボードで「プロジェクトを作成」を選択し、新しいプロジェクトを作成します。

### APIの有効化

1. 「APIとサービス」ダッシュボードに移動します。
2. 「APIとサービスを有効化」を選択。
3. 「Speech-to-Text API」を検索して有効化します。

### 認証情報の作成

1. APIの有効化後、「認証情報」ページに移動します。
2. 「認証情報を作成」ボタンをクリックし、「サービスアカウントキー」を選択。
3. 新しいサービスアカウントを作成し、ロールを選択（例: オーナー）。
4. キーのタイプは「JSON」を選択し、「作成」をクリックすると、キーファイルがダウンロードされます。

## ステップ2: 環境設定

### Python 環境の準備

1. Pythonがインストールされていることを確認します。
2. 必要に応じて仮想環境を作成し、アクティベートします。

### 必要なライブラリのインストール

```bash
pip install --upgrade google-cloud-speech
```

## ステップ3: 認証情報の設定

### 環境変数の設定

1. ダウンロードしたサービスアカウントキーファイルのパスを環境変数に設定します。
2. Bashでの設定方法：

    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
    ```

## ステップ4: Pythonスクリプトの作成

以下は、単純なSpeech-to-Text APIの使用例です：

```python
from google.cloud import speech
import io

# クライアントの初期化
client = speech.SpeechClient()

# ローカルファイルからオーディオを読み込む
with io.open('path/to/audio/file.wav', 'rb') as audio_file:
    content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='ja-JP')  # 日本語の音声認識を指定

# APIリクエストを送信してレスポンスを取得
response = client.recognize(config=config, audio=audio)

# 結果を出力
for result in response.results:
    print("Transcript: {}".format(result.alternatives[0].transcript))
```