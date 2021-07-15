from constants import DAYS, TIMES
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import validates, sessionmaker


def restartdb(engine, Base, Data, Count, PastData):
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
    
    restartdb(engine, Base, Data, Count, PastData)
    return engine, Base, Data, Count, PastData
