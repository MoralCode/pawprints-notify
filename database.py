from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# create an SQLite database file and connect to it using SQLAlchemy
engine = create_engine('sqlite:///database/discord_school_mapping.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# define the mapping table schema using SQLAlchemy's declarative syntax
class GuildToSchool(Base):
	__tablename__ = 'guild_to_school'
	guild_id = Column(Integer, primary_key=True)
	school_id = Column(String, primary_key=True)
	channel_id = Column(Integer)
	notification_threshold = Column(Integer)
	subscription_name = Column(String)


class WatchedURLs(Base):
	__tablename__ = 'watched_urls'
	guild_id = Column(Integer, primary_key=True)
	url = Column(String, primary_key=True)
	url_type = Column(String, nullable=False)
	channel_id = Column(Integer)
	subscription_name = Column(String)

if __name__ == "__main__":
	# create the table in the database if it doesn't already exist
	Base.metadata.create_all(engine)


