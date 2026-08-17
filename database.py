from sqlmodel import SQLModel, create_engine

import models

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"chec'_same_thread": False}, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
