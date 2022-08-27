import pymongo
import json

myclient = pymongo.MongoClient("mongodb://aniket:Aniketsprx077@cluster0-shard-00-00-uugt8.mongodb.net:27017,cluster0-shard-00-01-uugt8.mongodb.net:27017,cluster0-shard-00-02-uugt8.mongodb.net:27017/main?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")
mydb = myclient["main"]
mycol = mydb["syllabus"]



mydoc = mycol.find()

with open("data2.json", "a+") as f:
    ls = []
    for x in mydoc:
        del x['_id']
        ls.append(x);
    f.write(json.dumps(ls))
