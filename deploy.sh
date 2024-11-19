#!/bin/bash -e

# リソースグループの場所と名前を定義
LOCATION="japaneast"
RESOURCE_GROUP_NAME="rag-poc"

# リソースグループを作成する
az group create \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP_NAME

# リソースグループへ Azure リソースをデプロイする
az deployment group create \
  --name deploy \
  --resource-group $RESOURCE_GROUP_NAME \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.parameters.json