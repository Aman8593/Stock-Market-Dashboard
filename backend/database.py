from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")  # like mongodb+srv://user:pass@cluster.mongodb.net/mydb

if not MONGO_URI:
    logger.warning("MONGO_URI not found in environment variables. Using default local MongoDB.")
    MONGO_URI = "mongodb://localhost:27017"

try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["stockuserdb"]
    logger.info("MongoDB client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    raise

async def test_db_connection():
    """Test database connection"""
    try:
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        return False

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


