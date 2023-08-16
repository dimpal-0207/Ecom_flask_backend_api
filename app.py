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
        print("===>token", token)
        if not token or not token.startswith('Bearer '):
            return jsonify({"message": "Admin access required."}), 403

        token = token.split(' ')[1]
        print("===>splittoken", token)
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print("===>payload", payload)
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

# def admin_required(func):
#     def custom_admin_wrapper(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         print("===")
#         if not token or not token.startswith('Bearer '):
#             return jsonify({"message": "Admin access required."}), 403
#
#         token = token.split(' ')[1]
#         try:
#             payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#             if payload.get('user_id'):
#                 # You can also validate other payload data if needed
#                 return func(*args, **kwargs)
#             else:
#                 return jsonify({"message": "Invalid token."}), 403
#         except jwt.ExpiredSignatureError:
#             return jsonify({"message": "Token has expired."}), 403
#         except jwt.InvalidTokenError:
#             return jsonify({"message": "Invalid token."}), 403
#
#     return custom_admin_wrapper

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

@admin_required
@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({"message": "Category name is required."}), 400

    # Check if the category with the same name already exists
    existing_category = mongo.db.category.find_one({"name": name})
    if existing_category:
        return jsonify({"message": "Category already exists."}), 400

    category = {"name": name}
    category_id = mongo.db.category.insert_one(category).inserted_id

    # Convert ObjectId to string for JSON serialization
    category['_id'] = str(category_id)

    payload = {
        "user_id": category['_id'],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    response = {
        "status": 200,
        "message": "Category added successfully.",
        "payload": [category]
    }
    return jsonify(response), 200
@admin_required
@app.route('/add_subcategory', methods=['POST'])
def add_subcategory():
    data = request.get_json()
    name = data.get('name')
    category_id = data.get('category_id')
    if not name or not category_id:
        return jsonify({"message": "Name and Category ID are required."}), 400

        # Check if the category with the same name already exists
    existing_subcategory = mongo.db.subcategory.find_one({"name": name})
    if existing_subcategory:
        return jsonify({"message": "SubCategory already exists."}), 400


    subcategory = {"name": name, "category_id": category_id}
    subcategory_id = mongo.db.subcategory.insert_one(subcategory).inserted_id
    subcategory['_id'] = str(subcategory_id)

    response = {
        "status": 200,
        "message": "SubCategory added successfully.",
        "payload": [subcategory]
    }
    return jsonify(response), 200

@admin_required
@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.form
    print("===>dtaa", data)
    name = data.get('name')
    image = request.files.get('image')
    size = data.get('size')
    color = data.get('color')
    price = data.get('price')
    description = data.get('description')
    category_id = data.get('category_id')
    subcategory_id = data.get('subcategory_id')

    if not all([name, image, size, color, description, category_id, subcategory_id]):
        return jsonify({"message": "All fields are required."}), 400


# if product already exist with same name
    existing_product = mongo.db.products.find_one({"name": name})
    if existing_product:
        return jsonify({"message": "Product already exists."}), 400

    # Check if the provided category and subcategory IDs exist in the database
    if not mongo.db.category.find_one({"_id": ObjectId(category_id)}):
        return jsonify({"message": "Invalid category ID."}), 400

    if not mongo.db.subcategory.find_one({"_id": ObjectId(subcategory_id)}):
        return jsonify({"message": "Invalid subcategory ID."}), 400
    image.save('uploads/' + image.filename)

    product = {
        'name': name,
        'image': image.filename,
        'size': size,
        'color': color,
        'price':price,
        'description': description,
        'category_id': str(category_id),
        'subcategory_id': str(subcategory_id)
    }
    print("===>product", product)

    product_id = mongo.db.products.insert_one(product).inserted_id
    product['_id'] = str(product_id)

    response = {
        "status": 200,
        "message": "Product added successfully.",
        "payload": [product]
    }

    return jsonify(response), 200


@app.route('/get_products', methods=['GET'])
def get_products():
    products = mongo.db.products.find()
    print("===>product", products)
    product_list = []

    for product in products:
        product['_id'] = str(product['_id'])  # Convert ObjectId to string
        product_list.append(product)

    response = {
        "status": 200,
        "message": "Product list get successfully.",
        "payload": product_list
    }

    return jsonify(response), 200


@app.route('/get_user_list', methods=["GET"])
def get_user_list():
    user = mongo.db.users.find()
    print("====>user", user)
    user_list =[]
    for us in user:
        us['_id'] = str(us['_id'])
        user_list.append(us)
    response={
        "status": 200,
        "message": "Product list get successfully.",
        "payload": user_list
    }
    return jsonify(response),200


@app.route('/category_list', methods=["GET"])
def get_category_list():
    category = mongo.db.category.find()
    print("===>cat", category)
    category_list=[]
    for cat in category:
        cat['_id'] = str(cat['_id'])
        category_list.append(cat)
    return jsonify(
        {
            "status" : 200,
            "message ": "category list get successfully",
            "payload": category_list
        }
    )


@app.route("/sub_category_list", methods=["GET"])
def get_subcategory_list():
    sub_category = mongo.db.subcategory.find()
    sub_cat_list =[]
    for sub in sub_category:
        sub['_id']= str(sub['_id'])
        sub_cat_list.append(sub)
        return jsonify(
            {
                "status": 200,
                "message": "sub category list get successfully",
                "payload": sub_cat_list
            }
        )


@app.route('/get_product/<string:product_id>', methods=['GET'])
def get_product_details(product_id):
    try:
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            product['_id'] = str(product['_id'])  # Convert ObjectId to string
            return jsonify({"status": 200, "message": "Success", "product": [product]}), 200
        else:
            return jsonify({"status": 404, "message": "Product not found."}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": "Failed", "error": str(e)}), 400


@app.route('/category_details/<string:product_id>', methods=['GET'])
def get_category_details(category_id):
    try:
        category = mongo.db.category.find_one({"_id": ObjectId(category_id)})
        if category:
            category['_id'] = str(category['_id'])  # Convert ObjectId to string
            return jsonify({"status": 200, "message": "Success", "payload": [category]}), 200
        else:
            return jsonify({"status": 404, "message": "Product not found."}), 404
    except Exception as e:
        return jsonify({"status": 400, "message": "Failed", "error": str(e)}), 400


@app.route("/sub_cat_details/<string:sub_cat_id>", methods=["GET"])
def get_subcategory_details(sub_cat_id):
    try:
        sub_cat = mongo.db.subcategory.find_one({"_id":ObjectId(sub_cat_id)})
        if sub_cat:
            sub_cat['_id'] = str(sub_cat['_id'])
            return jsonify({"status":200, "message": "success", "payload":[sub_cat]}),200
        else:
            return jsonify({"status":404, "message": "Not Found"}),404
    except  Exception as e:
        return jsonify({"stastus":400, "message": "Failed", "error":str(e)}), 400


@app.route("/delete_user/<string:user_id>", methods=["GET"])
def delete_user(user_id):
    try:
        user = mongo.db.users.delete_one({"_id":ObjectId(user_id)})
        if user.deleted_count > 0:
            return jsonify({"status": 200, "message": "User Deleted Successfully"}),200
        else:
            return jsonify({"status":404, "message": "Not Found User"}), 404
    except Exception as e:
        return jsonify({"status":400, "message":"Failed","error": str(e)}),400





#add product with multiple images at once
# @admin_required
# @app.route('/add_product', methods=['POST'])
# def add_product():
#     try:
#         data = request.form
#         name = data.get('name')
#         price = data.get('price')
#         description = data.get('description')
#         category_id = data.get('category_id')
#         subcategory_id = data.get('subcategory_id')
#
#         # Retrieve the list of image files
#         image_files = request.files.getlist('images')
#
#         sizes = request.json.get('sizes', [])
#         colors = request.json.get('colors', [])
#
#         if not all([name, price, description, category_id, subcategory_id, sizes, colors, image_files]):
#             return jsonify({"message": "All fields are required."}), 400
#
#         # Check if the provided category and subcategory IDs exist in the database
#         if not mongo.db.category.find_one({"_id": ObjectId(category_id)}):
#             return jsonify({"message": "Invalid category ID."}), 400
#
#         if not mongo.db.subcategory.find_one({"_id": ObjectId(subcategory_id)}):
#             return jsonify({"message": "Invalid subcategory ID."}), 400
#
#         # Save the image files and collect their filenames
#         image_filenames = []
#         for image in image_files:
#             filename = f"{ObjectId()}.{image.filename.rsplit('.', 1)[1].lower()}"
#             image.save(os.path.join('uploads', filename))
#             image_filenames.append(filename)
#
#         # Add the product to the MongoDB collection
#         product = {
#             'name': name,
#             'images': image_filenames,
#             'price': price,
#             'description': description,
#             'category_id': category_id,
#             'subcategory_id': subcategory_id,
#             'sizes': sizes,
#             'colors': colors
#         }
#
#         product_id = mongo.db.products.insert_one(product).inserted_id
#         product['_id'] = str(product_id)
#
#         response = {
#             "status": 200,
#             "message": "Product added successfully.",
#             "payload": product
#         }
#
#         return jsonify(response), 200
#     except Exception as e:
#         return jsonify({"status": 400, "message": "Failed", "error": str(e)}), 400

# #this is the final product add query
# @admin_required
# @app.route('/product/add_product', methods=['POST', 'GET'])
# def product():
#         data = request.form
#         print("===>data", data)
#         name = data.get('name')
#         image = request.files.get('image')
#         size = data.get('size')
#         color = data.get('color')
#         description = data.get('description')
#
#         if not all([name, image, size, color, description]):
#             return jsonify({"message": "All fields are required."}), 400
#
#         # Save the image to a designated folder (optional, but recommended)
#         # Replace 'uploads' with the folder path where you want to store the images
#         image.save('uploads/' + image.filename)
#
#         # Add the product to the MongoDB collection
#         product = {
#             'name': name,
#             'image': image.filename,
#             'size': size,
#             'color': color,
#             'description': description,
#         }
#         mongo.db.products.insert_one(product)
#
#         return jsonify({"message": "Product added successfully."}), 200

#all details and also show the category using object id
# @app.route('/get_product/<string:product_id>', methods=['GET'])
# def get_product_details(product_id):
#     try:
#         product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
#         if product:
#             product['_id'] = str(product['_id'])  # Convert ObjectId to string
#
#             # Retrieve category details based on the category_id
#             category_id = product.get('category_id')
#             category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
#             if category:
#                 category['_id'] = str(category['_id'])  # Convert ObjectId to string
#                 product['category'] = category
#
#             return jsonify({"status": 200, "message": "Success", "product": product}), 200
#         else:
#             return jsonify({"status": 404, "message": "Product not found."}), 404
#     except Exception as e:
#         return jsonify({"status": 400, "message": "Failed", "error": str(e)}), 400


#
# @app.route('/get_products', methods=['GET'])
# def get_products():
#     try:
#         # Query parameters
#         sort_by = request.args.get('sort_by', 'name')  # Default sorting by name
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 10))
#         search_query = request.args.get('search_query', '')
#
#         # Create a query dictionary based on the search query
#         query = {}
#         if search_query:
#             query['name'] = {'$regex': search_query, '$options': 'i'}
#
#         # Retrieve the products with sorting and pagination
#         products = mongo.db.products.find(query).sort(sort_by).skip((page - 1) * per_page).limit(per_page)
#
#         # Convert ObjectId to string and build the response
#         product_list = []
#         for product in products:
#             product['_id'] = str(product['_id'])
#             product_list.append(product)
#
#         return jsonify({"status": 200, "message": "Success", "products": product_list}), 200
#
#     except Exception as e:
#         return jsonify({"status": 400, "message": "Failed", "error": str(e)}), 400

@app.route('/details_pro', methods=['GET'])
def details_pro():
    try:
        # Get query parameters
        category = request.args.get('category')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search_query = request.args.get('q', '')
        min_price = float(request.args.get('min_price', 0))
        max_price = float(request.args.get('max_price', float('inf')))

        # Build the query based on parameters
        query = {}
        if category:
            query['category_id'] = category
        if search_query:
            query['name'] = {'$regex': search_query, '$options': 'i'}
        query['price'] = {'$gte': min_price, '$lte': max_price}

        # Get total count for pagination
        total_count = mongo.db.products.count_documents(query)

        # Get products based on query and pagination
        products = mongo.db.products.find(query).skip((page - 1) * limit).limit(limit)
        products_list = []
        for product in products:
            product['_id'] = str(product['_id'])
            products_list.append(product)

        response = {
            "status": 200,
            "message": "Success",
            "total_count": total_count,
            "products": products_list
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"status": 400, "message": "Failed", "error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)