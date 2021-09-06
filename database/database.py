from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import validates, sessionmaker

    
def genDatabase():
    """
    Generates the tables of the database for other subroutines to use

    :return: A tuple containing the engine used for accessing the database, the Base for the 
             defining of tables and a series of objects which each map to a database table
    """

    # create an engine to the database file
    engine = create_engine("sqlite:///library_usage.db", echo=False, connect_args={"check_same_thread": False})
    Base = declarative_base()
    
    # initialise classes for each table 
    class Data(Base):
        __tablename__ = "data"

        id = Column(Integer, primary_key=True)
        day = Column(String(10), nullable=False)
        time = Column(String(10), nullable=False)
        jnr_expected = Column(Integer, default=0)
        snr_expected = Column(Integer, default=0)


        @validates("jnr_expected")
        def validate_jnrexpected(self, key, count):
            if count < 0:
                return 0
            return count


        @validates("snr_expected")
        def validate_snrexpected(self, key, count):
            if count < 0:
                return 0
            return count
        
    class Count(Base):
        __tablename__ = "count"

        id = Column(Integer, primary_key=True)
        snrvalue = Column(Integer, default=0)
        jnrvalue = Column(Integer, default=0)


        @validates("snrvalue")
        def valid_snrvalue(self, key, count):
            if count < 0:
                return 0
            return count


        @validates("jnrvalue")
        def valid_jnrvalue(self, key, count):
            if count < 0:
                return 0
            return count
        
    class PastData(Base):
        __tablename__ = "pastdata"

        id = Column(Integer, primary_key=True)
        day = Column(Integer, nullable=False)
        month = Column(Integer, nullable=False)
        year = Column(Integer, nullable=False)
        term = Column(Integer, nullable=False)
        week = Column(Integer, nullable=False)
        time = Column(String(10), nullable=False)
        jnrcount = Column(Integer, nullable=False)
        snrcount = Column(Integer, nullable=False)
        
    class LibraryTimes(Base):
        __tablename__ = "generalinfo"
        
        id = Column(Integer, primary_key=True)
        library = Column(String(3), nullable=False)
        day = Column(String(9), nullable=False)
        openinghour = Column(Integer, nullable=False)
        openingminute = Column(Integer, nullable=False)
        closinghour = Column(Integer, nullable=False)
        closingminute = Column(Integer, nullable=False)
    
    class MaxSeats(Base):
        __tablename__ = "maxseats"
        
        id = Column(Integer, primary_key=True)
        library = Column(String(3), nullable=False)
        seats = Column(Integer, nullable=False)
        
    class Librarians(Base):
        __tablename__ = "librarians"
        
        id = Column(Integer, primary_key=True)
        library = Column(String(3), nullable=False)
        name = Column(String(32), nullable=False)

    class Events(Base):
        __tablename__ = "events"
        
        id = Column(Integer, primary_key=True)
        library = Column(String(3), nullable=False)
        event = Column(String(100), nullable=False)
        impact = Column(String(8), nullable=False)
    
    class Alerts(Base):
        __tablename__ = "alerts"
        
        id = Column(Integer, primary_key=True)
        library = Column(String(3), nullable=False)
        alert = Column(String(100),  nullable=False)
        type = Column(String(11), nullable=False) # warning or information

    return engine, Base, Data, Count, PastData, LibraryTimes, MaxSeats, Librarians, Events, Alerts
