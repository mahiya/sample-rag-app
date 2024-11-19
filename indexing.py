import os
import json
from dotenv import load_dotenv
from utils.search import AzureSearchClient
from utils.openai import OpenAIServiceClient

# .env ファイルから環境変数を読み込む
load_dotenv()

# Azure AI Search へ登録する検索ドキュメントの JSON ファイルのパス
docs_json_path = "infra/sample_docs.json"

# Azure AI Search と Azure OpenAI Search のクライアントを生成
search_client = AzureSearchClient()
openai_client = OpenAIServiceClient()


def main():

    # Azure AI Search のインデックスが存在しない場合は作成
    if not search_client.check_index_exists():
        search_client.create_index(
            "infra/index.json",
            {
                "resourceUri": os.getenv("AZURE_OPENAI_ENDPOINT"),
                "deploymentId": os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT"),
                "modelName": "text-embedding-3-large",
            },
        )

    # 検索ドキュメントをインデックスへ登録
    with open(docs_json_path, encoding="utf-8") as f:
        docs = json.load(f)
        search_client.index_documents(docs)

    # 試しにクエリを実行
    docs = search_client.search("*")
    print(docs)


if __name__ == "__main__":
    main()
