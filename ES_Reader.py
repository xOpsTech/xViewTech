__author__ = 'evantha'
import logging
from elasticsearch import Elasticsearch

INDEX = 'xops'
TYPE = 'metrics'

es_client = Elasticsearch('localhost:9200')
print ('initialized ES')

logger = logging.getLogger(__name__)


def read_index_data(index, id):
    try:
        res = es_client.get(index=index, id=id)
        return res['_source']
    except Exception:
        print ("There was a read index exception")
        # self.logger.exception(e)


def search_index_data(index, query, is_aggregated_query=False):
    try:
        res = es_client.search(index=index, body=query, ignore_unavailable=True)
        if is_aggregated_query:
            return res['aggregations']['products']['buckets']
        else:
            return res['hits']['hits']
    except Exception:
        print ("There was a search index exception")


def create_index_data(body, index=INDEX, doc_type=TYPE, id=None):
    try:
        res = es_client.index(index=index, doc_type=doc_type, id=id, body=body)
        print('source: %s | source status: %s | document id: %s' % (
            body.get('source', ''), body.get('sourceStatus', ''), res['_id']))
        logger.info('source: %s | source status: %s | document id: %s', body.get('source', ''),
                    body.get('sourceStatus', ''), res['_id'])
        return res['result']
    except Exception:
        print ("There was a create index exception")
        # self.logger.exception(e)


def delete_document(index, doc_type, id):
    try:
        es_client.delete(index=index, doc_type=doc_type, id=id)
    except Exception:
        print ("There was a delete document exception")
        # self.logger.exception(e)


def delete_index(index):
    try:
        es_client.indices.delete(index=index, ignore=[400, 404])
    except Exception:
        print ("There was a delete index exception")


def delete_by_query(index, doc_type, query):
    try:
        es_client.delete_by_query(index=index, doc_type=doc_type, body=query)
    except Exception:
        print ("There was a delete by query exception")
        # self.logger.exception(e)


def get_mapping(index, doc_type):
    try:
        es_client.indices.get_mapping(index=index, doc_type=doc_type)
    except Exception:
        print ("There was a get mapping exception")


def put_mapping(index, doc_type, body):
    try:
        es_client.indices.put_mapping(doc_type, body, index=index)
    except Exception:
        print ("There was a put mapping exception")
