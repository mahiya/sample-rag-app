import os
from pydantic import BaseModel
from openai import AzureOpenAI
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class OpenAIServiceClient:

    def __init__(self):

        # Azure OpenAI Service を使用するためのクライアントを生成する (RBAC認証)
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            ),
            api_version=os.getenv("OPENAI_API_VERSION", "2024-08-01-preview"),
        )

        # Azure OpenAI Service 利用に関する設定を読み込む
        self.chat_deploy_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
        self.embed_deploy_name = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT", "text-embedding-3-large")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.0))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 4096))

    def get_completion(self, system_message: str, user_message: str, response_format: BaseModel) -> BaseModel:
        """Azure OpenAI Service での処理を実行する

        Args:
            system_message (str): システムメッセージ
            user_message (str): ユーザメッセージ
            response_format (BaseModel): 処理結果の出力フォーマット

        Returns:
            BaseModel: 処理結果
        """
        resp = self.client.beta.chat.completions.parse(
            model=self.chat_deploy_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format=response_format,
        )
        return resp.choices[0].message.parsed

    def get_embed(self, text: str) -> list[float]:
        """テキストの埋め込みを取得する

        Args:
            text (str): テキスト

        Returns:
            list[float]: テキストの埋め込み
        """
        resp = self.client.embeddings.create(model=self.embed_deploy_name, input=text)
        return resp.data[0].embedding
