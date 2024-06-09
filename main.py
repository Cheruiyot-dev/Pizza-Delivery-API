from fastapi import FastAPI
from auth_routes import auth_router
from order_routes import order_router
import uvicorn
from database import create_tables, engine, Base
import sqlalchemy as sa

app = FastAPI(
    title="Pizza delivery app",
    description="A REST API for pizza delivery service",
    version="v1",
    docs_url="/docs",
    root_path="/docs"
)

app.include_router(auth_router)
app.include_router(order_router)


@app.on_event("startup")
async def startup_event():
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


@app.on_event("shutdown")
def shutdown_event():
    print("Closing database connections...")
    engine.dispose()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)