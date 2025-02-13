import os
import pandas as pd
from decimal import Decimal
from sqlalchemy import create_engine, text, func, update
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import date, datetime
from tables import *

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

Session = sessionmaker(bind=engine)
session = Session()

def add_maintenance_to_db(session, maintenance_data):
    """Add a maintenance log to the database."""
    try:
        # Fetch the vehicle IDs based on code or type
        if maintenance_data['vehicle'].lower() == 'todos los equipos':
            vehicle_ids = [v[0] for v in session.query(Vehicle.id).filter(Vehicle.type.ilike('%T')).all()]
        elif maintenance_data['vehicle'].lower() == 'todos los semiremolques':
            vehicle_ids = [v[0] for v in session.query(Vehicle.id).filter(Vehicle.type.ilike('%S')).all()]
        else:
            vehicle_ids = [session.query(Vehicle.id).filter_by(code=maintenance_data['vehicle']).scalar()]

        if not vehicle_ids:
            raise ValueError(f"Vehicle with code '{maintenance_data['vehicle']}' not found.")

        # Fetch the component ID based on part and component
        component_id = session.query(Component.id).filter_by(
            part=maintenance_data['part'],
            component=maintenance_data['component']
        ).scalar()

        if not component_id:
            raise ValueError(f"Component '{maintenance_data['component']}' for part '{maintenance_data['part']}' not found.")

        # Add a maintenance log for each vehicle in the list
        for vehicle_id in vehicle_ids:
            new_log = MainLogs(
                vehicle_id=vehicle_id,
                date=maintenance_data['date'],
                start_time=maintenance_data['start_time'],
                end_time=maintenance_data['end_time'],
                action=maintenance_data['action'],
                component_id=component_id,
                kilometers=maintenance_data['kilometers'],
                hobbs_meter=maintenance_data['hobbs_meter'],
                next_change=maintenance_data['next_change'],
                in_charge=maintenance_data['in_charge'],
                comment=maintenance_data['comment'],
                cost=maintenance_data['cost']
            )
            session.add(new_log)

        session.commit()
        return "Registro(s) de mantenimiento agregado(s) exitosamente"
    except Exception as e:
        session.rollback()
        return f"Error al agregar el registro de mantenimiento: {e}"
    




