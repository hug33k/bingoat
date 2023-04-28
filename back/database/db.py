from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from . import dump


class Database:
	_instance = None


	@staticmethod
	def get_instance(path="database/"):
		if Database._instance is None :
			databaseFile = "db.sqlite"
			sqliteUrl = f"sqlite:///{path}{databaseFile}"
			Database._instance = create_engine(sqliteUrl, connect_args={"check_same_thread": False}, poolclass=StaticPool)
		return Database._instance


def get_session():
	return Session(Database.get_instance())


def create_database_and_tables(engine):
	SQLModel.metadata.create_all(engine)


def init_db():
	engine = Database.get_instance()
	create_database_and_tables(engine)
	dump.inject(engine)


if __name__ == "__main__":
	init_db()
