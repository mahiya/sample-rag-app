@description('使用する Azure OpenAI Service アカウントのエンドポイント')
param openAIServiceAccountEndpoint string

@description('使用する Azure OpenAI Service アカウントの Chat Completion API 用モデルのデプロイの名前')
param openAIServiceChatDeployName string

@description('使用する Azure OpenAI Service アカウントの Embeddings API 用モデルのデプロイの名前')
param openAIServiceEmbeddingsDeployName string

@description('使用する Azure AI Search のインデックスの名前')
param searchProductIndexName string

var resourcePostfix = uniqueString(resourceGroup().id)
var searchServiceName = 'srch-${resourcePostfix}'
var searchServiceSku = 'standard'
var searchServiceReplicaCount = 1
var searchServicePartitionCount = 1
var searchServiceApiVersion = '2024-07-01'
var useSemanticSearch = true
var vectorSearchFieldNames = 'contentVector'
var applicationInsightsName = 'appi-${resourcePostfix}'
var appPlanName = 'asp-${resourcePostfix}'
var appServiceName = 'app-${resourcePostfix}'
var openAIApiVersion = '2024-08-01-preview'

resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: searchServiceName
  location: resourceGroup().location
  sku: {
    name: searchServiceSku
  }
  properties: {
    replicaCount: searchServiceReplicaCount
    partitionCount: searchServicePartitionCount
    hostingMode: 'default'
    semanticSearch: 'standard'
    authOptions: { aadOrApiKey: { aadAuthFailureMode: 'http401WithBearerChallenge' } }
  }
  identity: {
    type: 'SystemAssigned'
  }
}

resource applicationInsights 'Microsoft.Insights/components@2015-05-01' = {
  name: applicationInsightsName
  location: resourceGroup().location
  properties: {
    ApplicationId: applicationInsightsName
    Request_Source: 'IbizaWebAppExtensionCreate'
  }
}

resource appPlan 'Microsoft.Web/serverfarms@2021-02-01' = {
  name: appPlanName
  location: resourceGroup().location
  sku: {
    name: 'P0V3'
    tier: 'Premium v3'
  }
  properties: {
    reserved: true
  }
}

resource appService 'Microsoft.Web/sites@2021-02-01' = {
  name: appServiceName
  location: resourceGroup().location
  properties: {
    serverFarmId: appPlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: true
      http20Enabled: true
      appSettings: [
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: true
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: reference(applicationInsights.id, '2015-05-01').InstrumentationKey
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: reference(applicationInsights.id, '2015-05-01').ConnectionString
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~2'
        }
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: openAIServiceAccountEndpoint
        }
        {
          name: 'AZURE_OPENAI_CHAT_DEPLOYMENT'
          value: openAIServiceChatDeployName
        }
        {
          name: 'AZURE_OPENAI_EMBED_DEPLOYMENT'
          value: openAIServiceEmbeddingsDeployName
        }
        {
          name: 'OPENAI_API_VERSION'
          value: openAIApiVersion
        }
        {
          name: 'AZURE_SEARCH_ENDPOINT'
          value: 'https://${searchServiceName}.search.windows.net'
        }
        {
          name: 'AZURE_SEARCH_INDEX_NAME'
          value: searchProductIndexName
        }
        {
          name: 'AZURE_SEARCH_API_VERSION'
          value: searchServiceApiVersion
        }
        {
          name: 'AZURE_SEARCH_USE_SEMANTIC_SEARCH'
          value: useSemanticSearch
        }
        {
          name: 'AZURE_SEARCH_VECTOR_FIELD_NAMES'
          value: vectorSearchFieldNames
        }
      ]
    }
    httpsOnly: true
  }
  dependsOn: [
    searchService
  ]
}
