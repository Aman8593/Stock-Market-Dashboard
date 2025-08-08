from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # like mongodb+srv://user:pass@cluster.mongodb.net/mydb

client = AsyncIOMotorClient(MONGO_URI)
db = client["stockuserdb"]

# import certifi
# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI")

# client = AsyncIOMotorClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
# db = client["stockuserdb"]

# async def check_db():
#     try:
#         info = await client.server_info()
#         print("✅ MongoDB connected:", info.get("version"))
#     except Exception as e:
#         print("❌ MongoDB connection failed:", e)


