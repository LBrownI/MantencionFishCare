import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean, Time, Enum
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
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

with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS mantencion"))
engine = create_engine(f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}:{3306}/{config["database_name"]}', echo=True)

Base = declarative_base()

# User model
class User(UserMixin, Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum('admin', 'mantencion'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
# Vehicles model
class Vehicle(Base):
    __tablename__ = 'Vehicle'
    id = Column(Integer, primary_key=True)
    code = Column(Text, nullable=False)
    type = Column(Enum('Tracto Camión', 'Semiremolque'), nullable=False)
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
    log_date = Column(Date, nullable=False, default=date.today())  # Renamed from 'date'
    start_time = Column(Time, nullable=True)  # Start time (HH:MM)
    end_time = Column(Time, nullable=True)  # End time (HH:MM)
    action = Column(Text, nullable=False) 
    component_id = Column(Integer, ForeignKey('Component.id'), nullable=False)
    odometer_km = Column(Integer, nullable=True) # FREE INPUT
    odometer_hrs = Column(Integer, nullable=True) # FREE INPUT
    supervisor = Column(Text, nullable=False) # FREE INPUT
    comment = Column(Text, nullable=True) # FREE INPUT
    cost = Column(DECIMAL(10, 2), nullable=True) # FREE INPUT

    vehicles = relationship('Vehicle', back_populates='maintenance_logs')
    components = relationship('Component', back_populates='maintenance_logs')

# TechnicalReview model
class TechnicalReview(Base):
    __tablename__ = 'TechnicalReview'
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('Vehicle.id'), nullable=False)
    date = Column(Date, nullable=False)  # Date of the review
    next_rev_date = Column(Date, nullable=False)  # Scheduled next review
    in_charge = Column(Text, nullable=False) # FREE INPUT
    cost = Column(DECIMAL(10, 2), nullable=True)

    vehicles = relationship('Vehicle', back_populates='technical_reviews')

# Create the tables in the database
Base.metadata.create_all(engine)