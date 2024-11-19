import os
import json
from concurrent.futures.thread import ThreadPoolExecutor
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizableTextQuery, VectorizedQuery
from azure.search.documents.indexes.models import SearchIndex


class AzureSearchClient:

    def __init__(self):

        # Azure AI Search に関する設定を環境変数から読み込む
        self.index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        self.use_semantic_search = True if os.getenv("AZURE_SEARCH_USE_SEMANTIC_SEARCH", "false").lower() == "true" else False
        self.vector_field_names = os.getenv("AZURE_SEARCH_VECTOR_FIELD_NAMES", "")
        self.vector_field_names = self.vector_field_names.split(",") if self.vector_field_names else []

        # Azure AI Search クライアントを生成
        self.index_client = SearchIndexClient(
            endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            credential=DefaultAzureCredential(),
            api_version=os.getenv("AZURE_SEARCH_API_VERSION", "2024-07-01"),
        )
        self.search_client = self.index_client.get_search_client(self.index_name)

    def create_index(self, json_file_path: str, vectorizer: dict = None):
        """
        インデックスを作成する

        Args:
            json_file_path (str): インデックス定義のJSONファイルパス
            vectorizer (dict): ベクトル化の設定

        Returns:
            int: HTTP ステータスコード
        """

        # インデックス定義を読み込む
        with open(json_file_path) as f:
            index_def = json.load(f)

        # インデックス名を設定
        index_def["name"] = self.index_name

        # ベクトル検索の設定を追加
        if "vectorSearch" in index_def and vectorizer:
            index_def["vectorSearch"]["vectorizers"][0]["azureOpenAIParameters"] = vectorizer

        # インデックスを作成
        index = SearchIndex.from_dict(index_def)
        self.index_client.create_index(index)

    def delete_index(self):
        """
        インデックスを削除する
        """
        self.index_client.delete_index(self.index_name)

    def check_index_exists(self) -> bool:
        """
        インデックスが存在するか確認する

        Returns:
            bool: インデックスが存在する場合は True
        """
        try:
            self.index_client.get_index(self.index_name)
            return True
        except ResourceNotFoundError:
            return False

    def index_documents(self, docs: list[dict], chunk_size: int = 250):
        """
        インデックスにドキュメントを追加する

        Args:
            docs (list[dict]): ドキュメントのリスト
            chunk_size (int): １つのスレッドで一度にアップロードするドキュメント数
        """
        chunks = [docs[i : i + chunk_size] for i in range(0, len(docs), chunk_size)]
        upload_documents = lambda d: self.search_client.upload_documents(documents=d)
        with ThreadPoolExecutor(max_workers=4) as executor:
            threads = [executor.submit(upload_documents, c) for c in chunks]
            [t.result() for t in threads]

    def delete_documents(self, ids: list[str]):
        """
        インデックスのドキュメントを削除する

        Args:
            ids (list[str]): 削除するドキュメントのIDリスト
        """
        docs = [{"id": id} for id in ids]
        self.search_client.delete_documents(documents=docs)

    def get_document(self, key: str):
        """
        指定したキーのインデックスのドキュメントを取得する

        Args:
            key (str): ドキュメントのキー

        Returns:
            dict: ドキュメント (存在しない場合は None を返す)
        """
        try:
            return self.search_client.get_document(key=key)
        except ResourceNotFoundError:
            return None

    def get_index_statistics(self) -> dict:
        """
        インデックスの統計情報を取得する
        """
        return self.index_client.get_index_statistics(self.index_name)

    def search(
        self,
        query: str = None,
        query_vector: list[float] = None,
        top: int = 5,
        skip: int = 0,
    ) -> list[dict]:
        """
        Azure AI Search によるドキュメント検索を実行する

        Args:
            query (str): 検索クエリ
            query_vector (list[float]): 検索ベクトル
            top (int): 取得する検索結果の最大数
            skip (int): 検索結果のオフセット

        Returns:
            list[dict]: 検索結果のドキュメント一覧
        """
        docs = self.search_client.search(
            search_text=query,
            query_type="semantic" if self.use_semantic_search else "full",
            top=top,
            skip=skip,
            vector_queries=(
                [
                    (
                        VectorizableTextQuery(
                            k_nearest_neighbors=top,
                            fields=field_name,
                            text=query,
                        )
                        if query_vector is None
                        else VectorizedQuery(
                            k_nearest_neighbors=top,
                            fields=field_name,
                            vector=query_vector,
                        )
                    )
                    for field_name in self.vector_field_names
                ]
            ),
        )
        return [d for d in docs]  # Paged item -> list
