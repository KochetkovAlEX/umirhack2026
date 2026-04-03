# Database Setup Guide

## Prerequisites
1. **Install PostgreSQL** on your system
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, remember the password you set for the `postgres` user

2. **Create the database** (run these commands in PostgreSQL):
   ```sql
   CREATE DATABASE umirhack_db;
   ```

## Configuration

1. **Update the `.env` file** with your actual values:
   ```env
   BOT_TOKEN=your_actual_bot_token_from_botfather
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   DB_NAME=umirhack_db
   DB_HOST=127.0.0.1
   DB_PORT=5432
   ```

2. **Verify PostgreSQL is running**:
   - Check if PostgreSQL service is running in Windows Services
   - Or run: `pg_isready -h 127.0.0.1 -p 5432`

## Testing the Connection

Run this simple test to verify the database connection:

```python
import asyncio
from bot.database.request import reload_database

async def test_db():
    try:
        await reload_database()
        print("✓ Database connection successful!")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")

asyncio.run(test_db())
```

## Common Issues

### Issue: "Connection refused"
- **Solution**: Make sure PostgreSQL is running
- Check Windows Services for "postgresql-x64-XX" service

### Issue: "Password authentication failed"
- **Solution**: Check your `DB_PASSWORD` in `.env` file
- Make sure it matches the password you set during PostgreSQL installation

### Issue: "database does not exist"
- **Solution**: Create the database using pgAdmin or psql:
  ```sql
  CREATE DATABASE umirhack_db;
  ```

### Issue: "role does not exist"
- **Solution**: The default user is usually `postgres`. Check your `.env` file
