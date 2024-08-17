from typing import Dict, List, Union

import numpy as np
from elasticsearch import Elasticsearch, exceptions


SAMPLE__EMBEDDINGS = ["When is the next cohort?"]


@data_loader
def search(*args, **kwargs) -> List[Dict]:
    """
    query_embedding: Union[List[int], np.ndarray]
    """
    
    connection_string = kwargs.get('connection_string', 'http://localhost:9200')
    index_name = kwargs.get('index_name', 'documents_20240816_3752')
    source = kwargs.get('source', "cosineSimilarity(params.query_vector, 'embedding') + 1.0")
    top_k = kwargs.get('top_k', 5)
    chunk_column = kwargs.get('chunk_column', 'content')

    query_embedding = None
    if len(args):
        query_embedding = args[0]
    if not query_embedding:
        query_embedding = SAMPLE__EMBEDDINGS[0]

    if isinstance(query_embedding, np.ndarray):
        query_embedding = query_embedding.tolist()

    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": source,
                "params": {"query_vector": query_embedding},
            }
        }
    }

    print("Sending script query:", script_query)

    es_client = Elasticsearch(connection_string)
    
    try:
        response = es_client.search(
            index="documents_20240816_3752",
            body={
                "size": top_k,
                "query": script_query,
                "_source": [chunk_column],
            },
        )

        print("Raw response from Elasticsearch:", response)

        return [hit['_source'][chunk_column] for hit in response['hits']['hits']]
    
    except exceptions.BadRequestError as e:
        print(f"BadRequestError: {e.info}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []