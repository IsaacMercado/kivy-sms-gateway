import requests

from src.utils import sync_to_async

http_get = sync_to_async(requests.get)
http_post = sync_to_async(requests.post)
