import json

from pymongo import MongoClient

from server.settings import settings

client = MongoClient(settings.mongo_uri)
db = client.get_database("bellerouze_chatbot")


pipeline = [
    {
        "$lookup": {
            "from": "statuses",  # collection to join
            "localField": "output.messages.id",  # field in messages collection
            "foreignField": "entry.changes.value.statuses.id",  # field in statuses collection
            "as": "statuses",  # output array field
        }
    },
    # {"$unwind": {"path": "$matched_statuses", "preserveNullAndEmptyArrays": True}},
]

results = db.messages.aggregate(pipeline)

for doc in results:
    print("-" * 150)
    print(json.dumps(doc, indent=2, default=str))
