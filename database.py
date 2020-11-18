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


class Reservation(db.Model):
    # reservations
    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reservation_date = db.Column(db.DateTime)
    reservation_end = db.Column(db.DateTime)
    # customer that did the the reservation
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    #
    # reserved table
    table_id = db.Column(db.Integer, db.ForeignKey("restaurant_table.id"))
    #
    people_number = db.Column(db.Integer)  # number of people in this reservation
    checkin = db.Column(db.Boolean, default=False)


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # reservation
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id"))
    # email
    email = db.Column(db.Text())