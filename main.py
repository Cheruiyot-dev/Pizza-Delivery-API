from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
import uvicorn
from contextlib import asynccontextmanager
from database import create_tables, engine, Base
import sqlalchemy as sa


app = FastAPI()


app.include_router(auth_router)
app.include_router(order_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        import models
        print("Checking if tables exist...")
        with engine.connect() as connection:
            table_names = [table.name for table in Base.metadata.sorted_tables]
            missing_tables = [table for table in table_names if not sa.inspect(connection).has_table(table)]
            
            if missing_tables:
                print(f"Tables {missing_tables} not found. Creating tables...")
                create_tables()
                print("Tables created successfully!")
            else:
                print("Tables already exist.")
        yield
    finally:
        print("Closing database connections...")
        engine.dispose()
app = FastAPI(lifespan=lifespan)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
