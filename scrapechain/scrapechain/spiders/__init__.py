# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
from scrapy import Spider
import json
import hashlib

class BaseSpider(scrapy.Spider):

    def converter(self,element,type_convert):
        try:
            if type_convert == 'int':
                converted_element = int(element)
            elif type_convert == 'json':
                converted_element = json.loads(element)
            else:
                print("type %s not recognized for %s"%(type_convert,element))
            print("conversion to %s is completed"%type_convert)
        except Exception as e:
            print("%s conversion to %s not successfull"%(element,type_convert))
            print(e)
            return None

        return converted_element


    def create_unique_id(self,uniqufy):
        u_encoded = uniqufy.encode() # encoding to bytes
        hashed_u = hashlib.sha256(u_encoded)
        return hashed_u.hexdigest()


    def __init__(self,*args,**kwargs):
        Spider.__init__(self, *args, **kwargs)
