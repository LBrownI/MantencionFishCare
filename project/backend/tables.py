import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# Configuration should match the Docker Compose file
config = {
    'host': 'localhost',
    'database_name': 'mantencion',
    'user': 'root',  # Matches MYSQL_USER in compose
    'password': 'fishybusiness'  # Matches MYSQL_PASSWORD in compose
}

# Connect to MySQL using the database specified in the Compose file
engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}:{3306}/{config["database_name"]}', echo=True)

Base = declarative_base()

# Vehicles model
class Vehicle(Base):
    __tablename__ = 'Vehicle'
    id = Column(Integer, primary_key=True)
    code = Column(Text, nullable=False)
    type = Column(Text, nullable=False)  # Camión, Semirremolque
    model = Column(Text, nullable=True) # Patente Camión, Marca - model Semirremolque

    maintenance_logs = relationship('MainLogs', back_populates='vehicles')
    technical_reviews = relationship('TechnicalReview', back_populates='vehicles')

# Components model
class Component(Base):
    __tablename__ = 'Component'
    id = Column(Integer, primary_key=True)
    vehicle_type = Column(String(1), nullable=False)  # T or S
    part = Column(Text, nullable=False)
    component = Column(Text, nullable=False)

    maintenance_logs = relationship('MainLogs', back_populates='components')

# MaintenanceLogs model
class MainLogs(Base):
    __tablename__ = 'MainLogs'
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    action = Column(Text, nullable=False)  # Cambio, Instalación, Reparación
    component_id = Column(Integer, ForeignKey('Component.id'), nullable=False)
    kilometers = Column(Integer, nullable=True)
    hobbs_meter = Column(DECIMAL(10, 2), nullable=True)
    next_change = Column(DECIMAL(10, 2), nullable=True)
    in_charge = Column(Text, nullable=False)
    comment = Column(Text, nullable=False)
    cost = Column(DECIMAL(10, 2), nullable=True)  # Restricted access for certain users

    vehicles = relationship('Vehicle', back_populates='maintenance_logs')
    components = relationship('Component')

# TechnicalReview model
class TechnicalReview(Base):
    __tablename__ = 'TechnicalReview'
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'), nullable=False)
    date = Column(Date, nullable=False)  # Date of the review
    next_rev_date = Column(Date, nullable=False)  # Scheduled next review
    in_charge = Column(Text, nullable=False)
    cost = Column(DECIMAL(10, 2), nullable=True)  # Restricted access for certain users
    vehicles = relationship('Vehicle', back_populates='technical_reviews')

# Create the tables in the database
Base.metadata.create_all(engine)
