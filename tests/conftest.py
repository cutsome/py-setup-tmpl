import os
import re
from typing import Any
from typing import Generator
from typing import Literal

import psycopg2
import pytest
from pytest_postgresql import factories
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.pool import NullPool

##############################
# configuration
##############################

class Database:
    def __init__(
        self,
        db_name: Literal["mart"] | Literal["sndb"],
    ) -> None:
        self.db_name = db_name
        self.sql_dir = f"sql/{self.db_name}"

    def create_table(self, **kwargs: Any) -> None:
        conn = psycopg2.connect(**kwargs)
        cursor = conn.cursor()
        queries = []
        for sql_file in sorted(os.listdir(self.sql_dir)):
            if not sql_file.endswith(".sql") or sql_file.startswith("100"):
                continue
            with open(os.path.join(self.sql_dir, sql_file), "r") as f:
                queries.append(f.read())
        with conn.cursor() as cursor:
            for query in queries:
                cursor.execute(query)
        conn.commit()


    def __create_seed(self, query: str, cursor) -> None:
        # Extract table name from query
        table_names = re.findall(r"(?<=\").+(?=\")", query)
        for table_name in table_names:
            seed_file = f"{self.sql_dir}/seeds/{table_name}.csv"
            with open(seed_file, "r") as f:
                # Skip the header row
                next(f)
                cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH (FORMAT CSV)", f)

    @property
    def postgresql_proc(self):
        return factories.postgresql_proc(
            load=[self.create_table],
            dbname=self.db_name,
        )

    def postgresql(self, postgresql_proc):
        if self.db_name == "mart":
            mart_postgres_proc = postgresql_proc
        else:
            sndb_postgres_proc = postgresql_proc
        return factories.postgresql(
            f"{self.db_name}_postgres_proc",
            dbname=self.db_name,
        )


def db_setup(db: Any) -> Connection:
    # create connection
    url = (
        f"postgresql+psycopg2://"
        f"{db.info.user}:@{db.info.host}:{db.info.port}/{db.info.dbname}"
    )
    print(url)
    engine = create_engine(url, echo=False, poolclass=NullPool)

    # create seeds
    dbname = db.info.dbname
    conn = engine.raw_connection()
    cursor = conn.cursor()

    with open(f"./sql/{dbname}/100_seeds.sql", "r") as sql:
        query = sql.read()
        table_names = re.findall(r"(?<=\").+(?=\")", query)
        for table_name in table_names:
            # Extract table name from query
            seed_file = f"./sql/{dbname}/seeds/{table_name}.csv"
            with open(seed_file, "r") as f:
                # Skip the header row
                next(f)
                cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH (FORMAT CSV)", f)
    conn.commit()
    conn.close()
    cursor.close()

    db_connection = engine.connect()
    return db_connection


##############################
# mart
##############################

m = Database("mart")
mart_postgres_proc = m.postgresql_proc
mart_postgres = m.postgresql(mart_postgres_proc)

@pytest.fixture
def mart(mart_postgres: Any) -> Generator[Connection, None, None]:
    """Database fixture for mart.

    Args:
        fixture request object
    Returns:
        sqlalchemy.MetaData
    """
    db_connection = db_setup(mart_postgres)
    yield db_connection
    db_connection.close()


@pytest.fixture
def mart_metadata(mart: Connection) -> Generator[MetaData, None, None]:
    metadata = MetaData()
    metadata.reflect(bind=mart)
    yield metadata


##############################
# sndb
##############################

s = Database("sndb")
sndb_postgres_proc = s.postgresql_proc
sndb_postgres = s.postgresql(sndb_postgres_proc)

@pytest.fixture
def sndb(sndb_postgres: Any) -> Generator[Connection, None, None]:
    """Database fixture for sndb.

    Args:
        fixture request object
    Returns:
        sqlalchemy.MetaData
    """
    db_connection = db_setup(sndb_postgres)
    yield db_connection
    db_connection.close()


@pytest.fixture
def sndb_metadata(sndb: Connection) -> Generator[MetaData, None, None]:
    metadata = MetaData()
    metadata.reflect(bind=sndb)
    yield metadata
