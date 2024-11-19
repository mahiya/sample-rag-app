import os
from dotenv import load_dotenv
from pydantic import BaseModel
from flask import Flask, request, Response
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from utils.openai import OpenAIServiceClient

# .env ファイルから環境変数を読み込む
load_dotenv()

# Flask の初期化
app = Flask(__name__)

# デバッグ実行かどうかを判定
debug = True if os.getenv("DEBUG") == "true" else False

# デバッグ実行でない場合のみ、Azure Application Insights によるログ出力とトレースを有効化
if not debug:
    configure_azure_monitor()
    FlaskInstrumentor().instrument_app(app)

# Azure OpenAI Service を使用するためのクライアントを生成する
openai_client = OpenAIServiceClient()

# Azure OpenAI Service で使用するシステムメッセージを環境変数から取得
system_message = """
ユーザが入力したドキュメントの文章から、ドキュメントのタイトルと要約を生成して、かつキーワードを抽出してください。
"""


# Azure OpenAI Service - Chat Completion API の出力フォーマット定義
class OutputModel(BaseModel):
    title: str
    summary: str
    keywords: list[str]


# 静的ファイルの配信
@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    return app.send_static_file(path)


# Azure OpenAI Service で処理を実行する Web API
@app.route("/api/completion", methods=["POST"])
def get_completion_api() -> Response:
    """ユーザから送られてきたメッセージを Azure OpenAI Service で処理し、結果を返却する API

    Returns:
        Response: Azure OpenAI Service での処理結果
    """

    # ユーザからのメッセージを取得
    user_message = request.json["message"]

    # Azure OpenAI Service で処理をする
    extracted_data = openai_client.get_completion(system_message, user_message, OutputModel)

    # 処理結果を返却
    return extracted_data.model_dump(), 200


# Flask アプリケーションの起動
if __name__ == "__main__":
    app.run(debug=debug)
