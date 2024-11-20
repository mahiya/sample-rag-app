#!/bin/bash -e

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