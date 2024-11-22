
## 開発環境の構築

### Azure CLI のインストール
[Azure CLI をインストールする方法 | Microsoft Learn](https://learn.microsoft.com/ja-jp/cli/azure/install-azure-cli)

インストール後、以下を実行してテナントへのログインとサブスクリプションの選択を行う。
```sh
# テナントへのログイン
az login

# Azure サブスクリプションの選択
az account set -s {{Subscription ID}}

# 選択されている Azure サブスクリプションの確認
az account show
```

### Python 仮想環境の作成と有効化
```sh
python -m venv .venv
source .venv/Scripts/activate
```

### 必要な Python パッケージのインストール
```sh
python -m pip install -r requirements.txt
```

## Azure 環境の準備
Azure リソースを作成する方法は以下の3通りがあります：
1. [Azure Portal](https://portal.azure.com) で作成する。
2. Azure CLI で作成する
3. IaC で作成する (Azure Resource Manager または Azure Bicep)

### Azure リソースのデプロイ
```sh
./deploy.sh
```

### Azure Web Apps リソースのシステム割り当てマネージドIDを有効化
[マネージド ID - Azure App Service | Microsoft Learn](https://learn.microsoft.com/ja-jp/azure/app-service/overview-managed-identity?tabs=portal%2Chttp)

### 開発ユーザへの Azure リソースへのアクセス権限の付与
Azure Portal にて以下の RBAC 権限付与を行う。
- 開発ユーザ → Azure OpenAI Service アカウント: Cognitive Services OpenAI User
- 開発ユーザ → Azure AI Search アカウント: 検索インデックス データ共同作成者
- Azure Web Apps → Azure OpenAI Service アカウント: Cognitive Services OpenAI User
- Azure Web Apps → Azure AI Search アカウント: 検索インデックス データ共同作成者
- Azure AI Search アカウント →  Azure OpenAI Service アカウント: Cognitive Services OpenAI User

### Azure OpenAI Service でのモデルの準備
以下のモデルをデプロイする。
- gpt-4o
- text-embedding-3-large

### .env ファイルの設定
.env ファイルの以下のパラメータに値を指定：
- AZURE_OPENAI_ENDPOINT
- AZURE_SEARCH_ENDPOINT


## サンプルアプリの実行

### Azure AI Search インデックスの準備

```sh
python indexing.py
```

### サンプル Web アプリの実行
```sh
python app.py

# 実行後、http://127.0.0.1:5000 へアクセス
```

## Web アプリケーションのデプロイ

[deploy_app.sh](deploy_app.sh)を実行する (以下の通りのスクリプトを実行)。

```sh
# デプロイ設定
REGION='japaneast'       # Azure App Service リソースのリージョン
RESOURCE_GROUP=""        # リソースグループの名前
APP_SERVICE_PLAN_NAME="" # Azure App Service プランの名前
APP_SERVICE_NAME=""      # Azure App Service の名前
RUNTIME="PYTHON:3.11"    # ランタイム

# Azure App Service へ Web アプリケーションをデプロイする
az webapp up \
    --location $REGION \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN_NAME \
    --name $APP_SERVICE_NAME \
    --runtime $RUNTIME
```