'''



'''

from pyonr import read
from os import mkdir, remove
from os.path import isfile, abspath
from typing import Any, List

from .tasks_queue import TasksQueue

dict_items = type({}.items())
dict_keys = type({}.keys())
dict_values = type({}.values())

def connect(db:str, *, model:str=None, use_tasks_queue:bool=False):
   '''
   `connect()` is used to connect to the database easily

   can be used instead of calling `speeddb.database.DocumentDatabase()` directly

   but does the same job

   >>> db = connect("dbs/database")

   ### Parameters:
   `db`:`str`
      Database rel/abs path

   `model`:`str` (optional)
      Database Model type

   `use_tasks_queue`:`bool` (optional)
      Execute database related tasks in a thread which makes it faster (not in every project)

      Read more [here](https://illTypeThisLater)
   
   '''
   if not db.endswith(".sdb"):
      db += ".sdb"
      
   decoder = read(db)
   db_model = model or decoder.read["model"]

   if db_model in documentStatements:
      return DocumentDatabase(db, use_tasks_queue)
   if db_model in keyvalStatements:
      return KeyValDatabase(db, use_tasks_queue)

class Database:
   '''
   SpeedDB Database Main Class (Do not use this to connect to your database)

   '''
   def __init__(self, db:str, use_tasks_queue:bool=False):
      '''
      Initialize SpeedDB Database

      ### Parameters
      `db`:`str`
         Database rel/abs path

      `use_tasks_queue`:`bool` (optional)
         Execute database related tasks in a thread which makes it faster (not in every project)

         Read more [here](https://illTypeThisLater)
      
      '''

      if not db.endswith(".sdb"):
         db += ".sdb"
      with open(db, "r", encoding="utf-8") as file: # file checking
         self.db = abspath(db)
         self.decoder = read(db)

      self.use_tasks_queue = use_tasks_queue
      self.tasks_queue = TasksQueue()
      self.model = self.decoder.read["model"]

      self._check()

class DocumentDatabase(Database):
   '''
   a document-oriented database is data storage system designed for storing, retrieving and managing document-oriented information

   '''
   
   @property
   def documents(self) -> int:
      '''
      Retrieve number of documents in the database
      >>> db.documents
      10
      >>> type(db.documents)
      <class 'int'
      '''
      return len(self.decoder.read)

   def get(self, filter:dict) -> dict:
      '''
      Retrieve data based of a `filter`

      >>> db.get({}) # get the latest document in the database
      >>> db.get({"age": 20}) # get latest 20 year old user
      >>> type(db.get({}))
      <class 'dict'>
      
      '''

      documents = self.getAll(filter)

      return None if not documents else documents[0]

   def getAll(self, filter:dict) -> List[dict]:
      '''
      Retrieve every document that match a `filter`
      
      >>> db.getAll({}) # get every document in the database
      >>> db.getAll({"age": 20}) # get all 20 years old users
      >>> type(db.getAll({}))
      <class 'list'>

      '''
      if not isinstance(filter, dict):
         raise TypeError("filter must be a dict")
      
      data = self.decoder.read
      documents = find(data["data"], filter)

      return None if not documents else documents

   def append(self, document:dict):
      '''
      Append a single document to the database

      >>> db.append({"name": "Nawaf"})
      >>> db.append({"name": "Khayal"})
      
      '''
      
      if self.use_tasks_queue:
         self.tasks_queue.add_task_and_execute(self._append, document)
      else:
         self._append(document)

   def _append(self, document:dict):
      if not isinstance(document, dict):
         raise TypeError("document must be a dict")

      data = self.decoder.read
      data["data"].append(document)
      self.decoder.write(data)

   def appendAll(self, documents:List[dict]):
      '''
      Append multiple documents

      >>> numbers = [ { "x": y } for y in range(1, 10) ]
      >>> db.appendAll(numbers)
      
      '''
      
      if self.use_tasks_queue:
         self.tasks_queue.add_task_and_execute(self._appendAll, documents)
      else:
         self._appendAll(documents)

   def _appendAll(self, documents:List[dict]):
      if not isinstance(documents, list):
         raise TypeError("documents must be a list of dicts (list[dict])")
      if not check_types(documents, dict):
         raise TypeError("document must be a dict")
      
      data = self.decoder.read
      data["data"].extend(documents)
      self.decoder.write(data)

   def remove(self, filter:dict):
      '''
      Remove a single document that match `filter`

      >>> db.remove({"name": "Nawaf"})
      
      '''
      
      if self.use_tasks_queue:
         self.tasks_queue.add_task_and_execute(self._remove, filter)
      else:
         self._remove(filter)

   def _remove(self, filter:dict):
      if not isinstance(filter, dict):
         raise TypeError("filter must be a dict")

      data = self.decoder.read
      full_document = self.get(filter)
      
      if not full_document:
         return

      data["data"].remove(full_document)
      self.decoder.write(data)

   def removeAll(self, filter:dict):
      '''
      Remove a multiple documents that match `filter`

      >>> db.removeAll("age": 13)
      
      '''
      
      if self.use_tasks_queue:
         self.tasks_queue.add_task_and_execute(self._removeAll, filter)
      else:
         self._removeAll(filter)

   def _removeAll(self, filter:dict):
      if not isinstance(filter, dict):
         raise TypeError("filter must be a dict")

      data = self.decoder.read
      documents = self.getAll(filter) 

      if not documents:
         return

      for document in documents:
         data["data"].remove(document)

      self.decoder.write(data)

   def update(self, filter:dict, document:dict):
      '''
      Update a document that match `filter`

      >>> db.append({"name": "Nawaf"})
      >>> user = db.get({"name": "Nawaf"})
      >>> user["age"] = 16
      >>> user
      {"name": "Nawaf", "age": 15}
      >>> db.update({"name": "Nawaf"}, user) # "update()" will update the entire database
      
      '''
      
      if self.use_tasks_queue:
         self.tasks_queue.add_task_and_execute(self._update, filter, document)
      else:
         self._update(filter, document)

   def _update(self, filter:dict, document:dict):
      if not isinstance(filter, dict):
         raise TypeError("filter must be a dict")
      if not isinstance(document, dict):
         raise TypeError("document must be a dict")

      data = self.decoder.read
      full_document = self.get(filter)

      if not full_document:
         return

      index = data["data"].index(full_document)
      data["data"][index] = document
      self.decoder.write(data)

   def _check(self):
      if self.model == "keyval":
         raise TypeError("can't use DocumentDatabase for a keyval database")

class KeyValDatabase(Database):
   '''
   A key-value database, is a data storage paradigm designed for storing, retrieving, and managing associative arrays, and a data structure more commonly known today as a dictionary or hash table.

   '''

   def set(self, key:str, value:Any):
      '''
      
      set `key`=`value`     

      '''
      if not isinstance(key, str):
         raise TypeError("key must be a string")

      data = self.decoder.read
      data["data"][key] = value
      self.decoder.write(data)

   def unset(self, key:str):
      '''
      remove `key`
      
      '''

      if not isinstance(key, str):
         raise TypeError("key must be a string")

      data = self.decoder.read

      if not data["data"].get(key):
         return

      del data["data"][key]
      self.decoder.write(data)

   def get(self, key:str, default:Any=None) -> Any:
      '''
      retrieve `key` if exists

      if not return `default` or None
      
      '''

      if not isinstance(key, str):
         raise TypeError("key must be a string")

      return self.decoder.read["data"].get(key, default)

   def has(self, key:str) -> bool:
      '''
      check if `key` exists
      
      '''

      if not isinstance(key, str):
         raise TypeError("key must be a string")
      return True if key in self.decoder.read["data"] else None

   def clear(self):
      '''
      remove every key in database
      
      '''

      data = self.decoder.read
      data["data"].clear()
      self.decoder.write(data)

   def items(self) -> dict_items:
      '''
      return data like `dict.items()`

      >>> test_dict = {
      ...   "name":" "Nawaf",
      ...   "age": 15
      ... }

      >>> for key, value in test_dict.items():
      >>>   # ...

      >>> # That's the exact same thing when you do
      >>> db.items()
      
      '''

      return self.decoder.read["data"].items()

   def copy(self) -> dict:
      '''
      return a shallow copy of the database data
      
      '''
      
      return self.decoder.read["data"].copy()

   def keys(self) -> dict_keys:
      '''
      return database keys

      '''

      return self.decoder.read["data"].keys()

   def values(self) -> dict_values:
      '''
      return database values
      
      '''

      return self.decoder.read["data"].values()

   def pop(self, key:str, default:Any=None) -> Any:
      '''
      remove specified key and return the corresponding value.

      If key is not found, default is returned if given, otherwise None will be returned
      
      '''

      if not isinstance(key, str):
         raise TypeError("key must be a string")
      
      data = self.decoder.read
      value = data["data"].pop(key, default)
      self.decoder.write(data)

      return value


   def __getitem__(self, key:str) -> Any:
      if not isinstance(key, str):
         raise TypeError("key must be a string")

      return self.decoder.read["data"][key]

   def _check(self):
      if self.model == "document":
         raise TypeError("can't use KeyValDatabase for a document database")

documentSchema = {
   "model": "document",
   "data": []
}
KeyValSchema = {
   "model": "keyval",
   "data": {},
}

keyvalStatements = ["kv", "keyval", "keyvalue", "key-value", "key_value", "key-val", "key_val"]
documentStatements = ["docs", "documents", "doc", "document", "d"]

def build_db(*dbs:str, model:str):
   '''
   Create a new database
   
   '''
   model = model.strip().lower()
   if model in keyvalStatements:
      model = "keyval"
   elif model in documentStatements:
      model = "document"
   else:
      return "Invalid model!"

   for db in dbs:
      if not db.endswith(".sdb"):
         db += ".sdb"

      if isfile(db):
         return f"{db} already exists!"

      with open(db, "w", encoding="utf-8") as file:
         if model == "keyval":
            file.write(str(KeyValSchema))
         elif model == "document":
            file.write(str(documentSchema))

def destroy_db(db:str):
   '''
   Delete a database
   
   '''
   verification = input("Are your sure? this can't be undone (y/n)> ").strip().lower()
   correctAnswer = False
   YESs = ["y", "yes"]
   NOs = ["n", "no"]

   while not correctAnswer:
      if (verification not in YESs) and (verification not in NOs):
         verification = input("Invalid answer! (y/n)> ").strip().lower()
         continue
      else:
         if verification in YESs: # YES:
            if not db.endswith(".sdb"):
               db += ".sdb"
               
            remove(db)
            correctAnswer = True
         if verification in NOs: # NO
            break


def init(name:str=None):
   '''
   Initialize a folder to store your databases
   
   '''

   name = name or "db"
   mkdir(name)

def find(documents, _filter):
   '''
   this algorithm searchs in a list of dicts (list[dict]) for a matching key and value
   
   >>> docs = [{"name": "Nawaf", "age": 15}, {"name": "Joe", "age": 16}]
   >>> find(docs, {"age": 15})
   {"name": "Nawaf", "age": 15}
   
   btw i copied this from somewhere i forget where
   
   '''
   return [d for d in documents if sum(1 for k, v in d.items() if _filter.get(k)==v) >= len(_filter)]

def check_types(l:list, type):
   '''
   check if every element is the same type

   >>> check_types([1, 2, 3, "Hey!", int])
   False
   >>> check_types([1, 2, 3, 4], int)
   True

   from https://stackoverflow.com/questions/13252333/check-if-all-elements-of-a-list-are-of-the-same-type
   
   '''
   return all([isinstance(x, type) for x in l])