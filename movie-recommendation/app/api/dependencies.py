from app.services.engines.hybrid_service import HybridService
from fastapi import Depends
from elasticsearch import AsyncElasticsearch, Elasticsearch
from typing import AsyncGenerator

from app.services.es_service import EsService
from app.services.embed_service import EmbeddingProvider
from app.services.engines.cbf_service import ContentBasedService
from app.services.engines.cf_service import CollaborativeService
from app.core.config import settings

def get_embedding_provider():
    return EmbeddingProvider

async def get_es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    client = AsyncElasticsearch(**settings.elasticsearch_config)
    try:
        yield client
    finally:
        await client.close()

def get_es_service(es_client: AsyncElasticsearch = Depends(get_es_client)):
    return EsService(es_client)



def get_cbf_service(
    es_client: Elasticsearch = Depends(get_es_client), 
    embedding_provider = Depends(get_embedding_provider)
):
    return ContentBasedService(es_client, embedding_provider)


def get_cf_service(es_client: Elasticsearch = Depends(get_es_client)):
    return CollaborativeService(es_client)


def get_hybrid_service( cf_service: CollaborativeService = Depends(get_cf_service),
                        cbf_service: ContentBasedService = Depends(get_cbf_service),
                        es_service: EsService = Depends(get_es_service), 
                        ):
    return HybridService(cf_service, cbf_service, es_service)