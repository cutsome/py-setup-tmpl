from config.env import settings
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection


class SQLAlchemy:
    def __init__(
        self,
        db_name,
    ) -> None:
        self.db_name = db_name.upper()

    def create_connection(self) -> Connection:
        engine = create_engine(
            url=self._get_postgres_url(),
            echo=False,
            executemany_mode="values_plus_batch",
            executemany_values_page_size=10000,
            executemany_batch_page_size=500,
            future=True,
        )
        return engine.connect()

    def _get_postgres_url(self) -> str:
        user = getattr(settings, f"{self.db_name}_USER")
        password = getattr(settings, f"{self.db_name}_PASSWORD")
        host = getattr(settings, f"{self.db_name}_HOST")
        dbname = getattr(settings, f"{self.db_name}_NAME")
        return f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
