from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

doc = {
    'author': 'Sely Svit',
    'text': 'life depends on nodes',
    'timestamp': datetime.now()
}

res = es.index(index="test-index",body=doc)
print(res['result'])

new_res = es.get(index="test-index")
print(new_res['_source'])

print(es.search())
