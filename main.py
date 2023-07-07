from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Set up the MongoDB connection
mongo_uri = "mongodb+srv://spencerthurgood88:JCmravyw1IFl5e1S@performheatinginventory.zqctfzy.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["Inventory"]
collection = db["ShopInventory"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    item = request.form["item"]
    document = collection.find_one({"Item": item}, projection={"_id": 0, "Limit": 0})
    if document is not None:
        return jsonify({"result": str(document)})
    else:
        return jsonify({"result": "No results found."})
    
@app.route("/update", methods=["POST"])
def update():
    item = request.form['item_id']
    newQty = request.form['new_quantity']
    item = item.replace('\\', '')  # Remove the backslash before double quotes
    updateResult = collection.update_one({"Item": item}, {"$set": {"Qty": newQty}})
    if updateResult.modified_count == 1:
        return jsonify({"result": f"Quantity for {item} updated to {newQty}"})
    else:
        return jsonify({"result": f"No document found for {item}"}), 404

@app.route('/generate_order_list', methods=['POST'])
def generate_order_list():
    order_list = []
    for document in collection.find({}, projection={"_id": 0, "Qty": 1, "Limit": 1, "Item": 1}):
        qty = int(document["Qty"])
        limit = int(document["Limit"])
        if qty <= limit:
            order_qty = (2 * limit) - qty
            order_list.append({"Item": document["Item"], "OrderQty": order_qty})

    formatted_response = "\n".join(json.dumps(item, indent=4)[1:-1] for item in order_list)
    return (
        "<pre style='background-color: #333; color: #fff; padding: 10px;'>" 
        + formatted_response 
        + "</pre>"
    )

if __name__ == "__main__":
    app.run()
