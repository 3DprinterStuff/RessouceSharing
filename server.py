import json
from flask import Flask,request,redirect

app = Flask(__name__)

class Group(object):
    def __init__(self,name,secretary):
        self.name = name
        self.id = name
        self.members = []
        self.secretary = secretary

class Instance(object):
    counter = 0
    def __init__(self,name,admin):
        self.name = name
        self.adminId = admin.id
        self.people = {}
    
    def AaddPerson(actorId,person):
        if actorId == person.id:
            raise Exception("permission violation")
        self.people[person.id] = person

    def AgetInventory(actor, personId):
        self.people[personId].AgetInventory(actor)

class Compartment(object):
    def __init__(self,name):
        self.name = name

class Actor(object):
    def __init__(self,name):
        self.name = name
        self.desires = []
        self.inventory = []
        self.places = []
        self.groups = []
        self.contacts = []
        self.compartments = []
        self.id = name

        self.inbox = []
        self.outbox = []

        self.inBoundRequests = []
        self.outBoundRequests = []
    
    def TgetRecord(self):
        json.dumps({"@context":"https://www.w3.org/ns/activitystreams",
                    "id":name,
                    "name":name})
    def TgetOutbox(self):
        return self.outbox
    
    def TpostToOutbox(self,actor,message):
        self.outbox.append(message)

    def TgetInbox(self):
        return self.inbox
    
    def TpostToInbox(self):
        self.inbox.append(message)
    
    def IaddContact(self,contact):
        self.contacts.append(contact)
    
    def IaddToInventory(self, actor, items):
        if not actor == self:
            raise Exception("invalid change")

        for item in items:
            item.AchangeHolder(self,self)
        self.inventory.extend(items)
    
    def IaddDesires(self, actor, desires):
        if not actor == self:
            raise Exception("invalid change")

        self.desires.extend(desires)

    def IscanForDesiredThings(self):
        result = ""

        for query in self.desires:
            for thing in self.inventory:
                if matchesQuery(thing,query):
                    result += "You already own this! Thing: %s Query: %s"%(thing.name, query)+"\n"

        for query in self.desires:
            for person in self.contacts:
                if person == self:
                    continue

                for thing in person.AgetInventory(self):
                    if matchesQuery(thing,query):
                        result += "person %s has the thing: %s Query: %s"%(person.name, thing.name, query)+"\n"

        return result

    def IscanForSuggestions(self):
        result = ""

        categoryQueries = []
        collectedCategories = []
        for query in self.desires:
            if not query.categories:
                continue
            if query.categories in collectedCategories:
                continue
            collectedCategories.append(query.categories)
            categoryQueries.append(Query(None,query.categories))
    
        for query in categoryQueries:
            for person in self.contacts:
                if person == self:
                    continue

                for thing in person.AgetInventory(self):
                    if matchesQuery(thing,query):
                        result += "person %s has some thing you might care about: %s Query: %s"%(person.name, thing.name, query)+"\n"

        return result

    def IscanForSinks(self):
        result = ""
        for person in self.contacts:
            if person == self:
                continue

            for query in person.desires:
                for thing in self.inventory:
                    if matchesQuery(thing,query):
                        result += "person %s could need your %s query %s"%(person.name,thing.name,query)+"\n"
        return result
    
    def AgetInventory(self, requester):
        return self.inventory

    def IrequestTransfer(self, item, me):
        holder = item.AgetHolder(self)
        request = TransferRequest(item,me,"id like to have your %s"%(item.name))
        holder.AregisterTransferRequest(holder,request)
        self.outBoundRequests.append(request)
    
    def AregisterTransferRequest(self,actor,request):
        self.inBoundRequests.append(request)
    
    def IAllowTransferRequest(self,actor,request):
        request.allowed = True
        request.ASendNotification("ok, hols dir ab")
    
    def ASendNotification(self, text):
        pass
    
    def IfinalizeTransfer(self, actor, request):
        actor.AremoveFromInventory(request.item)
        request.requester.IaddToInventory(request.item)

class TransferRequest(object):
    def __init__(self,item,requester,message):
        self.item = item
        self.requester = requester
        self.message = message
        self.allowed = False

categoryMap = {}
def getCategory(name):
    if not name in categoryMap:
        categoryMap[name] = Category(name)
    return categoryMap[name]
    
class Category(object):

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return self.name

class Thing(object):
    def __init__(self, name, description="", categories=[]):
        tags = []
        self.name = name
        self.description = []
        self.categories = categories
        self.holder = None
        self.wikidata_id = None
        self.desireability = 0
        self.compartment = None
        self.amount = None
    
    def IchangeCategories(self,actor,categories):
        self.categories = categories

    def AchangeHolder(self,actor,holder):
        if not actor == self and not self.holder == None:
            raise Exception("Illegal owner change")
        self.holder = holder
    
    def AgetHolder(self,actor):
        return self.holder
    
    def __repr__(self):
        return self.name

class Query(object):
    def __init__(self, name, categories=[]):
        self.name = name
        self.categories = categories
    
    def __repr__(self):
        baseString = "QUERY: "
        values = []
        if self.name:
            baseString += "name: %s "
            values.append(self.name)
        if self.categories:
            baseString += "categories: %s "
            values.append(self.categories)
        return baseString%tuple(values)

class Server(object):
     def __init__(self,dataset=None):
         self.users = {}

         if dataset:
             self.load(dataset)
    
     def load(self,dataset):
         with open("%s.json"%dataset) as raw_file:
             rawData = json.loads(raw_file.read())

         # add root objects
         for rawUser in rawData["actors"]:
             user = Actor(rawUser["name"])
             self.users[rawUser["name"]] = user
             
             if "inventory" in rawUser:
                 for rawItem in rawUser["inventory"]:
                     thing = Thing(rawItem["name"])
                     if "categories" in rawItem:
                         thing.categories = list(map(lambda x: getCategory(x),rawItem["categories"]))
                     if "desireability" in rawItem:
                         thing.desireability = rawItem["desireability"]
                     if "description" in rawItem:
                         thing.description = rawItem["description"]
                     if "wikidata_id" in rawItem:
                         thing.wikidata_id = rawItem["wikidata_id"]
                     if "compartment" in rawItem:
                         thing.compartment = rawItem["compartment"]
                     if "amount" in rawItem:
                         thing.amount = rawItem["amount"]
                     user.inventory.append(thing)

             if "desires" in rawUser:
                 for rawDesire in rawUser["desires"]:
                     user.desires.append(Query(rawDesire["name"]))
    
             if "compartments" in rawUser:
                 for rawCompartment in rawUser["compartments"]:
                     user.compartments.append(Compartment(rawCompartment["name"]))

             if "groups" in rawUser:
                 for rawGroup in rawUser["groups"]:
                     if rawGroup["reference"] == True:
                         continue
                     user.groups.append(Group(rawGroup["name"],user))

         # add group references
         for rawUser in rawData["actors"]:
             user = self.users[rawUser["name"]]
             if "groups" in rawUser:
                 for rawGroup in rawUser["groups"]:
                     if rawGroup["reference"] == False:
                         continue
                     secretary = self.users[rawGroup["secretary"]]
                     for group in secretary.groups:
                         if group.id == rawGroup["name"]:
                            user.groups.append(group)
                            group.members.append(user)
                            break
    
     def store(self,dataset):
         rawData = {}
         rawData["actors"] = []
         for actor in self.users.values():
             rawUser = {}
             rawUser["name"] = actor.name
             rawUser["inventory"] = []
             rawUser["desires"] = []
             rawUser["groups"] = []
             if actor.compartments:
                 rawUser["compartments"] = []
                 for compartment in actor.compartments:
                     rawUser["compartments"].append({"name":compartment.name})

             for group in actor.groups:
                 rawGroup = {}
                 if group.secretary == actor:
                     rawGroup["reference"] = False
                     rawGroup["name"] = group.name
                     rawGroup["members"] = []
                     for member in group.members:
                         rawGroup["members"].append(member.name)
                 else:
                     rawGroup["reference"] = True
                     rawGroup["name"] = group.name
                 rawGroup["secretary"] = group.secretary.id
                 rawUser["groups"].append(rawGroup)

             for item in actor.inventory:
                 rawItem = {}
                 rawItem["name"] = item.name
                 rawItem["desireability"] = item.desireability
                 rawItem["wikidata_id"] = item.wikidata_id
                 rawItem["description"] = item.description
                 rawItem["compartment"] = item.compartment
                 rawItem["amount"] = item.amount
                 rawItem["categories"] = list(map(lambda x: x.name, item.categories))
                 rawUser["inventory"].append(rawItem)

             for desire in actor.desires:
                 rawQuery = {}
                 rawQuery["name"] = desire.name
                 rawUser["desires"].append(rawQuery)

             rawData["actors"].append(rawUser)
         with open("%s.json"%dataset,"w") as raw_file:
             rawData = raw_file.write(json.dumps(rawData))
    
def findRessources(person):
    result = ""
    result += person.IscanForDesiredThings()+"\n"
    result += person.IscanForSuggestions()+"\n"
    result += person.IscanForSinks()+"\n"
    return result

def matchesQuery(thing,query):
    if thing.name == query.name or query.name == None:
        for category in query.categories:
            if not category in thing.categories:
                return False
        return True
    else:
        return False
