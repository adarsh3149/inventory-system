
import streamlit as st
import pymongo
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import datetime

MONGO_URI = "mongodb+srv://adarshsoham03:rBHuz1IIWUnu296o@cluster0.gruemzb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "electronics_store"
COLLECTION_NAME = "inventory"
LOG_FILE = "inventory_logs.txt"

# MongoDB setup
@st.cache_resource
def get_collection():
    try:
        client = pymongo.MongoClient(MONGO_URI)
        client.admin.command('ismaster')
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        collection.create_index("product_id", unique=True)
        return collection
    except Exception as e:
        st.error("MongoDB connection failed: " + str(e))
        return None

def log_operation(action, details=""):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {action}: {details}\n")

# Application UI and logic
collection = get_collection()
st.title("📦 Electronics Inventory Management System")

menu = ["Add Product", "Update Quantity", "View Inventory", "Calculate Total Value", "Search Product"]
choice = st.sidebar.selectbox("Choose Action", menu)

if collection:
    if choice == "Add Product":
        st.subheader("➕ Add New Product")
        product_id = st.text_input("Product ID")
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        quantity = st.number_input("Quantity", min_value=0, format="%d")
        if st.button("Add Product"):
            if product_id and name:
                try:
                    collection.insert_one({
                        "product_id": product_id,
                        "name": name,
                        "price": price,
                        "quantity": quantity
                    })
                    st.success(f"Product '{name}' added.")
                    log_operation("Add Product", f"{product_id}, {name}, {price}, {quantity}")
                except DuplicateKeyError:
                    st.warning("Product ID already exists.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Product ID and Name are required.")

    elif choice == "Update Quantity":
        st.subheader("🔄 Update Product Quantity")
        product_id = st.text_input("Enter Product ID")
        new_qty = st.number_input("New Quantity", min_value=0, format="%d")
        if st.button("Update Quantity"):
            result = collection.update_one({"product_id": product_id}, {"$set": {"quantity": new_qty}})
            if result.matched_count:
                st.success("Quantity updated successfully.")
                log_operation("Update Quantity", f"{product_id} => {new_qty}")
            else:
                st.warning("Product not found.")

    elif choice == "View Inventory":
        st.subheader("📋 Inventory List")
        items = list(collection.find({}, {"_id": 0}))
        if items:
            st.table(items)
        else:
            st.info("Inventory is empty.")

    elif choice == "Calculate Total Value":
        st.subheader("💰 Total Inventory Value")
        items = list(collection.find())
        total = sum(item["price"] * item["quantity"] for item in items)
        st.success(f"Total Value: ₹{total:.2f}")
        log_operation("Calculate Total", f"Value = ₹{total:.2f}")

    elif choice == "Search Product":
        st.subheader("🔍 Search Product by Name")
        keyword = st.text_input("Enter keyword")
        if st.button("Search") and keyword:
            result = list(collection.find({"name": {"$regex": keyword, "$options": "i"}}, {"_id": 0}))
            if result:
                st.table(result)
            else:
                st.info("No products found.")
            log_operation("Search Product", keyword)
