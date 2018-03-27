import pymongo
import hashlib
from datetime import datetime
from policy_study import app

hashfunc = app.config["HASHFUNC"]
dbname = app.config["DBNAME"]

coll_names = {
    "users": app.config["USER_COLL_NAME"],
    "config": app.config["CONFIG_COLL_NAME"],
    "questionnaire": app.config["QUESTIONNAIRE_COLL_NAME"],
    "logs": app.config["LOG_COLL_NAME"],
}


from pymongo.son_manipulator import SONManipulator


### from http://stackoverflow.com/a/20698802/2088767
### This only gets the job partway done... see the TransformCollection class
class KeyTransform(SONManipulator):
    """Transforms keys going to database and restores them coming out.

    This allows keys with dots in them to be used (but does break searching on
    them unless the find command also uses the transform).

    Example & test:
        # To allow `.` (dots) in keys
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost")
        db = client['delete_me']
        db.add_son_manipulator(KeyTransform(".", "_dot_"))
        db['mycol'].remove()
        db['mycol'].update({'_id': 1}, {'127.0.0.1': 'localhost'}, upsert=True,
                           manipulate=True)
        print db['mycol'].find().next()
        print db['mycol'].find({'127_dot_0_dot_0_dot_1': 'localhost'}).next()

    Note: transformation could be easily extended to be more complex.
    """

    def __init__(self, replace, replacement):
        self.replace = replace
        self.replacement = replacement

    def transform_key(self, key):
        """Transform key for saving to database."""
        return key.replace(self.replace, self.replacement)

    def revert_key(self, key):
        """Restore transformed key returning from database."""
        return key.replace(self.replacement, self.replace)

    def transform_incoming(self, son, collection):
        """Recursively replace all keys that need transforming."""
        for (key, value) in son.items():
            if self.replace in key:
                if isinstance(value, dict):
                    son[self.transform_key(key)] = self.transform_incoming(
                        son.pop(key), collection)
                else:
                    son[self.transform_key(key)] = son.pop(key)
            elif isinstance(value, dict):  # recurse into sub-docs
                son[key] = self.transform_incoming(value, collection)
        return son

    def transform_outgoing(self, son, collection):
        """Recursively restore all transformed keys."""
        for (key, value) in son.items():
            if self.replacement in key:
                if isinstance(value, dict):
                    son[self.revert_key(key)] = self.transform_outgoing(
                        son.pop(key), collection)
                else:
                    son[self.revert_key(key)] = son.pop(key)
            elif isinstance(value, dict):  # recurse into sub-docs
                son[key] = self.transform_outgoing(value, collection)
        return son


class TransformCollection(object):
    """Mongo doesn't allow dots in keys? We'll see about that"""
    def __init__(self, collection, replace, replacement):
        self.collection = collection
        self.trans = KeyTransform(replace, replacement)

    def __getattr__(self, name):
        return self.collection.__getattribute__(name)

    def find(self, son=None, *args, **kwargs):
        if not son:
            return self.collection.find(*args, **kwargs)
        return self.collection.find(self.trans.transform_incoming(son,
                                                                  self.collection),
                                    *args, **kwargs)

    def find_one(self, son=None, *args, **kwargs):
        if not son:
            return self.collection.find_one(*args, **kwargs)
        return self.collection.find_one(self.trans.transform_incoming(son,
                                                                      self.collection),
                                        *args, **kwargs)

    def remove(self, son=None, *args, **kwargs):
        if not son:
            return self.collection.remove(*args, **kwargs)
        return self.collection.remove(self.trans.transform_incoming(son,
                                                                    self.collection),
                                      *args, **kwargs)

client = pymongo.MongoClient()
db = client[dbname]
db.add_son_manipulator(KeyTransform(".", "_dot_"))

conns = { k: TransformCollection(db[v], ".", "_dot_") for k,v in coll_names.items() }
