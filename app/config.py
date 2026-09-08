import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./voting.db")
JWT_SECRET = os.getenv("JWT_SECRET", "development-only-secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

