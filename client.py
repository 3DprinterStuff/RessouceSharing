import json
from flask import Flask, request, redirect, render_template, session

import server as serverLib

app = Flask(__name__)

@app.route("/login",methods = ['GET'])
def loginForm():
    return render_template('login.html')

@app.route("/login",methods = ['POST'])
def login():
    session['username'] = request.form.get("name")
    return redirect("/",code=302)

@app.route("/newActor",methods = ['GET'])
def showCreateUserForm():
    return render_template('newUser.html')

@app.route("/newActor",methods = ['POST'])
def createUser():
    if request.form.get("name") in server.users:
        return "user already exists", 401

    user = serverLib.Actor(request.form.get("name"))
    server.users[user.name] = user
    store()
    return redirect("actors/%s"%(user.id),code=302)

@app.route("/actors/<user_id>/deleteDesire",methods = ['POST'])
def deleteQuery(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    toRemove = None
    for query in user.desires:
        if query.name == request.form.get("name"):
            toRemove = query
            break

    if not toRemove:
        return "query not found", 404

    user.desires.remove(toRemove)
    store()
    return redirect("actors/%s"%(user_id), code=302)

@app.route("/actors/<user_id>/addGroup",methods = ['GET'])
def addGroupForm(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    return "<form>form</form>"

@app.route("/actors/<user_id>/addGroup",methods = ['POST'])
def addGroup(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    user.groups.append(serverLib.Group(request.form.get("name")))
    store()

    return redirect("actors/%s"%(user_id), code=302)

@app.route("/actors/<user_id>/group/<group_id>",methods = ['GET'])
def viewGroup(user_id,group_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    groupFound = None
    for group in user.groups:
        if group.name == group_id:
            groupFound = group
            break

    if not groupFound:
        return "group not found", 404

    return render_template('group.html',user=user,group=groupFound)
    
@app.route("/actors/<user_id>/group/<group_id>/inviteActor",methods = ['POST'])
def inviteActorToGroup(user_id,group_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    groupFound = None
    for group in user.groups:
        if group.name == group_id:
            groupFound = group
            break

    if not groupFound:
        return "group not found", 404

    invitedUser = request.form.get("name")
    if not invitedUser in server.users:
        return "invited user not found", 404
    invitedUser = server.users[invitedUser]

    groupFound.members.append(invitedUser)
    invitedUser.groups.append(groupFound)

    store()

    return redirect("actors/%s/group/%s"%(user_id,group_id), code=302)
    
@app.route("/actors/<user_id>/group/<group_id>/removeActor",methods = ['POST'])
def removeActorFromGroup(user_id,group_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    groupFound = None
    for group in user.groups:
        if group.name == group_id:
            groupFound = group
            break

    if not groupFound:
        return "group not found", 404

    invitedUser = request.form.get("id")
    if not invitedUser in server.users:
        return "user to remove not found", 404
    invitedUser = server.users[invitedUser]

    groupFound.members.remove(invitedUser)
    invitedUser.groups.remove(groupFound)

    store()

    return redirect("actors/%s/group/%s"%(user_id,group_id), code=302)

@app.route("/actors/<user_id>/deleteGroup",methods = ['POST'])
def deleteGroup(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    name = request.form.get("name")

    toKill = None
    for group in user.groups:
        if group.name == name:
            toKill = group
            break
    if toKill:
        user.groups.remove(toKill)

    store()

    return redirect("actors/%s"%(user_id), code=302)

@app.route("/actors/<user_id>/deleteItem",methods = ['POST'])
def deleteItem(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    toRemove = None
    for item in user.inventory:
        if item.name == request.form.get("name"):
            toRemove = item
            break

    if not toRemove:
        return "item not found", 404

    user.inventory.remove(toRemove)
    store()
    return redirect("actors/%s"%(user_id), code=302)


@app.route("/actors/<user_id>/item/<item_id>/edit",methods = ['POST'])
def editItem(user_id,item_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    foundItem = None
    for item in user.inventory:
        if item.name == item_id:
            foundItem = item
            break

    if not foundItem:
        return "item not found", 404

    foundItem.description = request.form.get("description")
    foundItem.desireability = request.form.get("desireability")
    foundItem.wikidata_id = request.form.get("wikidata_id")
    foundItem.compartment = request.form.get("compartment")
    foundItem.amount = request.form.get("amount")
    categories = []
    for category_id in request.form.get("categories").split(","):
        category_id = category_id.strip()
        if category_id == "":
            continue
        categories.append(serverLib.getCategory(category_id))
    foundItem.categories = categories
    store()
    return redirect("actors/%s/item/%s"%(user_id,item_id), code=302)

@app.route("/actors/<user_id>/item/<show_item>",methods = ['GET'])
def showItem(user_id,show_item):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    foundItem = None
    for item in user.inventory:
        if item.name == show_item:
            foundItem = item
            break

    if not foundItem:
        return "item not found", 404

    categories = (','.join(map(lambda x: x.name, foundItem.categories)))
    return render_template('item.html',user=user,item=item,categories=categories)

@app.route("/actors/<user_id>/addCompartment",methods = ['POST','GET'])
def addCompartment(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    if request.method == 'GET':
        return '<form method="POST" action="/actors/%s/addCompartment"> <input name="name"/> <input type="submit"></form>'%(user_id)
    if request.method == 'POST':
        print(request.form.get("name"))
        user.compartments.append(serverLib.Compartment(request.form.get("name")))
        store()
        return redirect("actors/%s"%(user_id), code=302)

@app.route("/actors/<user_id>/addDesire",methods = ['POST','GET'])
def addDesire(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    if request.method == 'GET':
        return '<form method="POST" action="/actors/%s/addDesire"> <input name="name"/> <input type="submit"></form>'%(user_id)
    if request.method == 'POST':
        print(request.form.get("name"))
        user.IaddDesires(user,[serverLib.Query(request.form.get("name"))])
        store()
        return redirect("actors/%s"%(user_id), code=302)

@app.route("/actors/<user_id>/addItem",methods = ['POST','GET'])
def addItem(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    if request.method == 'GET':
        return '<form method="POST" action="/actors/%s/addItem"> <input name="name"/> <input type="submit"></form>'%(user_id)
    if request.method == 'POST':
        print(request.form.get("name"))
        user.IaddToInventory(user,[serverLib.Thing(request.form.get("name"))])
        store()
        return redirect("actors/%s"%(user_id), code=302)

@app.route("/actors/<user_id>/compartment/<compartment_id>/delete",methods = ['POST','GET'])
def deleteCompartment(user_id,compartment_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    for compartment in user.compartments:
        if compartment_id == compartment.name:
            user.compartments.remove(compartment)

    store()
    return redirect("actors/%s"%(user_id), code=302)

@app.route("/explore",methods = ['POST','GET'])
def explore():
    return render_template('explore.html')

@app.route("/actions",methods = ['POST','GET'])
def listActions():
    return render_template('actions.html')

@app.route("/actions/relocation",methods = ['POST','GET'])
def startRelocation():
    return render_template('startRelocation.html')

@app.route("/list",methods = ['GET'])
def listUsers():
    return render_template('list.html',users=server.users.values())

@app.route("/actors/<user_id>")
def showActor(user_id):
    if not user_id in server.users:
        return "user not found", 404
    user = server.users[user_id]

    noCategories = []
    categories = {}
    for item in user.inventory:
        if not item.categories:
            noCategories.append(item)
            continue
        for category in item.categories:
            if not category in categories:
                categories[category] = []
            categories[category].append(item)

    compartments = {}
    for compartment in user.compartments:
        compartments[compartment.name] = []

    for item in user.inventory:
        if not item.compartment:
            continue
        if not item.compartment in compartments:
            continue
        compartments[item.compartment].append(item)

    return render_template('actorOverview.html',user=user,categories=categories,noCategories=noCategories,ressourceText=serverLib.findRessources(user),compartments=compartments)

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/store")
def store():
    server.store("test2")
    return ''

if __name__ == "__main__":
    app.secret_key = 'sadlkJDSALKASDAIUSdgasdjlkajdöASFH'
    server = serverLib.Server("test2")
    for user in server.users.values():
        user.contacts = list(server.users.values())
    app.run(host='0.0.0.0',debug=True)
    app.config['SESSION_TYPE'] = 'filesystem'
