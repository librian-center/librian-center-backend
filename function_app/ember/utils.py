import collections

from azure.cosmosdb.table import TableService


class 莉沫TableService(TableService):
    def get_entity(self, *li, **d):
        t = super().get_entity(*li, **d)
        if 'etag' in t:
            del t['etag']
        if 'Timestamp' in t:
            del t['Timestamp']
        return t
    
    def goku_query_entities(self, *li, **d):
        t = list(super().query_entities(*li, **d))
        for i in t:
            if 'etag' in i:
                del i['etag']
            if 'Timestamp' in i:
                del i['Timestamp']
        return t
        

class 莉沫Error(Exception):
    None


def 错误简化(e):
    if len(e.args) == 1:
        return e.args[0]
    else:
        return e.args
