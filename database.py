from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from alembic.config import Config
from alembic import command

from pathlib import Path

# Create an Alembic configuration object
alembic_cfg = Config("./alembic.ini")  # Replace with the path to your alembic.ini file

# create an SQLite database file and connect to it using SQLAlchemy
db_path_str = 'database/discord_school_mapping.db'
# Specify the file path
db_path = Path(f"./{db_path_str}")

engine = create_engine(f'sqlite:///{db_path_str}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# define the mapping table schema using SQLAlchemy's declarative syntax
class GuildToSchool(Base):
	__tablename__ = 'guild_to_school'
	guild_id = Column(Integer, primary_key=True)
	channel_id = Column(Integer, primary_key=True)


if __name__ == "__main__":

	print("Checking if DB Directory exists...", end="")
	if not db_path.parent.exists():
		print("No")
		print(f"Creating directory at {str(db_path.parent)} ")
		# Create all directories leading up to the file
		db_path.parent.mkdir(parents=True, exist_ok=True)
	else:
		print("Yes")
	
	# create the table in the database if it doesn't already exist
	print("Creating Database...")
	Base.metadata.create_all(engine)

	print("Stamping Database version...")

	with engine.begin() as connection:
		alembic_cfg.attributes['connection'] = connection
		# Stamp the database with the latest revision

		command.stamp(alembic_cfg, "head")

	print("Done.")


