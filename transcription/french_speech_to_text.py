from google.cloud import speech


def transcribe_gcs(gcs_uri):
    print("# ----- Let's transcription ! ----- #\n")

    """Google Cloud Storage上のオーディオファイルを文字起こしする"""
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # 適切なエンコーディングを指定
        sample_rate_hertz=16000,  # サンプルレートを指定
        language_code="fr-FR",  # 言語コードを指定
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=90)

    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

    print("\n# ------------ finish ------------ #\n")


# 二つのオーディオファイルのURIを指定
gcs_uri1 = "gs://your-bucket-name/your-first-audio-file.mp3"
gcs_uri2 = "gs://your-bucket-name/your-second-audio-file.mp3"

# それぞれのファイルを文字起こし
transcribe_gcs(
    "gs://first_french_video_of_food/Livret grammatical (online-audio-converter.com).mp3"
)
transcribe_gcs("gs://first_french_video_of_food/CO Livret marché page 8.mp3")
