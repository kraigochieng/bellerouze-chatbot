from pymongo import AsyncMongoClient, MongoClient
from pymongo.server_api import ServerApi

from server.settings import settings

mongo_uri = (
    "mongodb://"
    f"{settings.mongo_initdb_root_username}:{settings.mongo_initdb_root_password}"
    "@"
    f"{settings.mongo_host}:{settings.mongo_port}/?authSource=admin"
)


async_mongo_client = AsyncMongoClient(
    mongo_uri,
    server_api=ServerApi(version="1", strict=True, deprecation_errors=True),
)


mongo_client = MongoClient(mongo_uri)
