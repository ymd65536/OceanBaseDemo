import pyseekdb

# Create embedded admin client
admin = pyseekdb.AdminClient(path="./seekdb.db")
# Create database
admin.create_database("hybrid_search_test")
