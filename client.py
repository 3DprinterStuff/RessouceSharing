import json
from flask import Flask, request, redirect, render_template

import server as serverLib

app = Flask(__name__)

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

@app.route("/explore",methods = ['POST','GET'])
def explore():
    return render_template('explore.html')

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

    return render_template('actorOverview.html',user=user,categories=categories,noCategories=noCategories,ressourceText=serverLib.findRessources(user))

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/store")
def store():
    server.store("test2")
    return ''

if __name__ == "__main__":
    server = serverLib.Server("test2")
    for user in server.users.values():
        user.contacts = list(server.users.values())
    app.run(host='0.0.0.0')
