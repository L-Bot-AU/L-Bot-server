from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import validates, sessionmaker
from constants import DAYS, TIMES, DO_RESTARTDB#, OPENING_TIMES, CLOSING_TIMES, MAX_CAPS, LIBRARIANS 
import os

def restartdb(engine, Base, Data, Count, PastData):
    try:
        os.remove("library_usage.db")
    except FileNotFoundError:
        pass
    Session = sessionmaker(bind=engine)
    begsession = Session()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    for day in DAYS:
        for time in TIMES:
            d = Data(day=day, time=time)
            begsession.add(d)

    begsession.add(Count())
    begsession.commit()
    
def genDatabase():
    engine = create_engine("sqlite:///library_usage.db", echo=False, connect_args={"check_same_thread": False})
    Base = declarative_base()
    
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
        
    class GeneralInfo(Base):
        __tablename__ = "generalinfo"
        
        id = Column(Integer, primary_key=True)
        library = Column(String, nullable=False)
        openinghour = Column(Integer, nullable=False)
        openingminute = Column(Integer, nullable=False)
        closinghour = Column(Integer, nullable=False)
        closingminute = Column(Integer, nullable=False)
        maximumSeats = Column(Integer, nullable=False)
        
    class Librarians(Base):
        __tablename__ = "librarians"
        
        id = Column(Integer, primary_key=True)
        name = Column(String(32), nullable=False)

    class Events(Base):
        __tablename__ = "events"
        
        id = Column(Integer, primary_key=True)
        event = Column(String(100), nullable=False)
        impact = Column(String(8), nullable=False)
    
    class Alerts(Base):
        __tablename__ = "alerts"
        
        id = Column(Integer, primary_key=True)
        alert = Column(String(100),  nullable=False)
        type = Column(String(11), nullable=False)

    if DO_RESTARTDB:
        restartdb(engine, Base, Data, Count, PastData)
    return engine, Base, Data, Count, PastData
