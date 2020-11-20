from datetime import datetime
import logging
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Text,
    Unicode,
    DateTime,
    Boolean,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db = declarative_base()


def init_db(uri):
    engine = create_engine(uri)
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    db.query = db_session.query_property()
    db.metadata.create_all(bind=engine)

    return db_session


class Reservation(db):
    # reservations
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_date = Column(DateTime)
    reservation_end = Column(DateTime)
    # customer that did the the reservation
    customer_id = Column(Integer)
    #
    # reserved table
    table_id = Column(Integer)
    #
    people_number = Column(Integer)  # number of people in this reservation
    checkin = Column(Boolean, default=False)


class Friend(db):
    __tablename__ = "friend"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # reservation
    reservation_id = Column(Integer, ForeignKey("reservation.id"))
    # email
    email = Column(Text())
