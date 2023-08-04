import datetime

import jwt
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config["MONGO_URI"] = "mongodb://localhost:27017/flask_admin"  # Replace with your MongoDB URI
mongo = PyMongo(app)
print("===mongo", mongo)

ADMIN_TOKEN = 'your_admin_token'
# Decorator for admin authentication
# Decorator for admin authentication
def admin_required(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"message": "Admin access required."}), 403

        token = token.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if payload.get('user_id'):
                # You can also validate other payload data if needed
                return func(*args, **kwargs)
            else:
                return jsonify({"message": "Invalid token."}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired."}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token."}), 403

    return wrapper

# Decorator for admin authentication
# def admin_required(func):
#     def wrapper(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         print("Received token:", token)
#
#         if token == f'Bearer {ADMIN_TOKEN}':
#             print("===>ADMIN token", ADMIN_TOKEN)
#             return func(*args, **kwargs)
#         else:
#             return jsonify({"message": "Admin access required."}), 403
#     return wrapper

@app.route("/", methods=["GET"])
def index():
    return "Welcome to Ecommerce Admin panel"

from bson import ObjectId

@app.route('/auth/register_user', methods=['POST'])
def register_user():
    if request.method == "POST":
        try:
            request_json = request.get_json()
            print("Received JSON:", request_json)  # Add this line to print the request JSON

            email = request_json.get("email", None)
            password = request_json.get("password", None)
            contact = request_json.get("contact", None)
            user_role = request_json.get("user_role", None)

            if not all([email, password, contact, user_role]):
                raise ValueError("All fields (email, password, contact, user_role) are required.")
            # Check if the email is already registered
            existing_user = mongo.db.users.find_one({"email": email})
            if existing_user:
                return jsonify({
                    "status": 400,
                    "message": "Failed",
                    "error": "Email is already registered."
                }), 400

            user_data = {
                "email": str(email),
                "password": str(password),
                "contact": str(contact),
                "user_role": str(user_role),
            }

            db = mongo.db.users.insert_one(user_data)
            user_data['_id'] = str(user_data['_id'])  # Convert ObjectId to string

            payload = {
                "user_id": str(user_data.get('_id')),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }

            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
            user_data['token'] = token

            return jsonify({
                "status": 200,
                "message": "Success",
                "payload": [{"user": user_data}]
            }), 200
        except Exception as e:
            return jsonify({
                "status": 400,
                "message": "Failed",



                "error": str(e)
            }), 400
    else:
        response = "Please make a valid request!"
        return jsonify({
            "status": 400,
            "message": "Failed",
            "error": response
        }), 400


#
# @app.route('/register_user', methods=['POST'])
# def register_user():
#     if request.method == "POST":
#
#             request_json = request.get_json()
#             print("Received JSON:", request_json)  # Add this line to print the request JSON
#
#             email = request_json.get("email")
#             password = request_json.get("password")
#             contact = request_json.get("contact")
#             user_role = request_json.get("user_role")
#
#             if not all([email, password, contact, user_role]):
#                 raise ValueError("All fields (email, password, contact, user_role) are required.")
#                 # Check if the email is already registered
#             existing_user = mongo.db.users.find_one({"email": email})
#             if existing_user:
#                 return jsonify({
#                     "status": 400,
#                     "message": "Failed",
#                     "error": "Email is already registered."
#                 }), 400
#
#             user_data = {
#                 "email": str(email),
#                 "password":str(password),
#                 "contact": str(contact),
#                 "user_role": str(user_role)
#             }
#
#             db = mongo.db.users.insert_one(user_data)
#
#             payload = {
#                 "user_id": str(user_data.get('_id')),
#                 "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
#             }
#
#             token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
#             print("===>token", token)
#             user_data['token'] = token
#
#             return jsonify({
#                 "status": 200,
#                 "message": "Success",
#                 "payload": {"user": user_data}
#             }), 200
#     else:
#
#         return jsonify({
#             "status": 400,
#             "message": "Failed",
#             "error": "Enter valid value"
#         }), 400


from bson import ObjectId

@app.route("/auth/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email and password:
        user_data = mongo.db.users.find_one({'email': email, 'password': password})

        if user_data:
            # Remove the ObjectId field and convert it to a string
            user_data['_id'] = str(user_data['_id'])
            user_data.pop('password', None)

            payload = {
                "user_id": user_data['_id'],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }

            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
            user_data['token'] = token

            response = {
                "status": 200,
                "message": "User Login Successfully",
                "payload": [user_data]
            }
            return jsonify(response), 200
        else:
            error = {
                "status": 401,
                "message": "Failed",
                "error": "Invalid email or password"
            }
            return jsonify(error), 401
    else:
        error = {
            "status": 400,
            "message": "Failed",
            "error": "Email or password is missing!"
        }
        return jsonify(error), 400


# @app.route('/add_category', methods=['POST'])
# @admin_required
# def add_category():
#     data = request.get_json()
#     name = data.get('name')
#     if not name:
#         return jsonify({"message": "Category name is required."}), 400
#
#     category = {"name": name}
#     category_id = category_collection.insert_one(category).inserted_id
#     return jsonify({"message": "Category added successfully.", "category_id": str(category_id)}), 200
#
#
# @app.route('/add_subcategory', methods=['POST'])
# @admin_required
# def add_subcategory():
#     data = request.get_json()
#     name = data.get('name')
#     category_id = data.get('category_id')
#     if not name or not category_id:
#         return jsonify({"message": "Name and Category ID are required."}), 400
#
#     subcategory = {"name": name, "category_id": category_id}
#     subcategory_id = subcategory_collection.insert_one(subcategory).inserted_id
#     return jsonify({"message": "Subcategory added successfully.", "subcategory_id": str(subcategory_id)}), 200
#
#
# @app.route('/add_product', methods=['POST'])
# @admin_required
# def add_product():
#     data = request.get_json()
#     name = data.get('name')
#     image = data.get('image')
#     size = data.get('size')
#     color = data.get('color')
#     description = data.get('description')
#     category_id = data.get('category_id')
#     subcategory_id = data.get('subcategory_id')
#
#     if not all([name, image, size, color, description, category_id, subcategory_id]):
#         return jsonify({"message": "All fields are required."}), 400
#
#     # Check if the provided category and subcategory IDs exist in the database
#     if not category_collection.find_one({"_id": category_id}):
#         return jsonify({"message": "Invalid category ID."}), 400
#
#     if not subcategory_collection.find_one({"_id": subcategory_id}):
#         return jsonify({"message": "Invalid subcategory ID."}), 400
#
#     product = {
#         'name': name,
#         'image': image,
#         'size': size,
#         'color': color,
#         'description': description,
#         'category_id': category_id,
#         'subcategory_id': subcategory_id
#     }
#     product_id = mongo.db.products.insert_one(product).inserted_id
#
#     return jsonify({"message": "Product added successfully.", "product_id": str(product_id)}), 200
#

#this is the final product add query
@app.route('/product/add_product', methods=['POST'])
@admin_required
def add_product():
        data = request.form
        print("===>data", data)
        name = data.get('name')
        image = request.files.get('image')
        size = data.get('size')
        color = data.get('color')
        description = data.get('description')

        if not all([name, image, size, color, description]):
            return jsonify({"message": "All fields are required."}), 400

        # Save the image to a designated folder (optional, but recommended)
        # Replace 'uploads' with the folder path where you want to store the images
        image.save('uploads/' + image.filename)

        # Add the product to the MongoDB collection
        product = {
            'name': name,
            'image': image.filename,
            'size': size,
            'color': color,
            'description': description,
        }
        mongo.db.products.insert_one(product)

        return jsonify({"message": "Product added successfully."}), 200




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")