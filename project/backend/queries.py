import os
from decimal import Decimal
from sqlalchemy import create_engine, text, func
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

# MENU Queries ------------------------------------------------------------------------------------------------|
def all_logs(session):
    """Devuelve todo el historial de mantenimiento"""
    try:
        query = (session.query(
                    MainLogs.id, MainLogs.date, MainLogs.start_time, MainLogs.end_time, 
                    MainLogs.action, MainLogs.kilometers, MainLogs.hobbs_meter, MainLogs.next_change,
                    MainLogs.in_charge, MainLogs.comment, MainLogs.cost, 
                    Vehicle.code.label('code'), 
                    Component.component.label('component'), 
                    Component.part.label('part')
                )
                .outerjoin(Vehicle, Vehicle.id == MainLogs.vehicle_id) \
                .outerjoin(Component, Component.id == MainLogs.component_id)
        )

        return [
            {
                "id": row.id,
                "date": row.date,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "action": row.action,
                "kilometers": row.kilometers or "Sin KM registrado",
                "hobbs_meter": row.hobbs_meter or "Sin HRS registradas",
                "next_change": row.next_change or "-",
                "in_charge": row.in_charge,
                "comment": row.comment,
                "cost": row.cost or "Sin cost registrado",
                "code": row.code,
                "component": row.component,
                "part": row.part
            }
            for row in query.all()
        ]
    except Exception as e:
        print(f'Error in all_employees: {e}')
    return []

def get_log_details(session, log_id):
    """Fetches detailed information about a specific maintenance log."""
    try:
        log = session.query(
            MainLogs.id, MainLogs.date, MainLogs.start_time, MainLogs.end_time,
            MainLogs.action, MainLogs.kilometers, MainLogs.hobbs_meter, MainLogs.next_change,
            MainLogs.in_charge, MainLogs.comment, MainLogs.cost,
            Vehicle.code.label('code'),
            Component.component.label('component'),
            Component.part.label('part')
        ).outerjoin(Vehicle, Vehicle.id == MainLogs.vehicle_id) \
         .outerjoin(Component, Component.id == MainLogs.component_id) \
         .filter(MainLogs.id == log_id).first()
        
        # Convert to a dictionary if a result is found
        if log:
            return {
                "id": log.id,
                "date": log.date,
                "start_time": log.start_time or "No registrado",
                "end_time": log.end_time or "No registrado",
                "action": log.action,
                "kilometers": log.kilometers or "No registrado",
                "hobbs_meter": log.hobbs_meter or "No registrado",
                "next_change": log.next_change or "No registrado o Innecesario",
                "in_charge": log.in_charge or "Desconocido",
                "comment": log.comment or "Sin comentarios",
                "cost": log.cost or "No registrado",
                "code": log.code,
                "component": log.component,
                "part": log.part
            }
    except Exception as e:
        print(f"Error fetching log details: {e}")
        return None
    
def get_filtered_logs(session, vehicle_id=None, part=None, component=None, year=None, date_from=None, date_to=None):
    """
    Obtener historial de mantenimiento filtrado por vehiculo, parte, componente, año o rango de tiempo.
    """
    try:
        # Base query with joins to include related data
        query = (
            session.query(
                MainLogs.id, MainLogs.date, MainLogs.start_time, MainLogs.end_time,
                MainLogs.action, MainLogs.kilometers, MainLogs.hobbs_meter, MainLogs.next_change,
                MainLogs.in_charge, MainLogs.comment, MainLogs.cost,
                Vehicle.code.label('code'),
                Component.part.label('part'),
                Component.component.label('component')
            )
            .outerjoin(Vehicle, Vehicle.id == MainLogs.vehicle_id)
            .outerjoin(Component, Component.id == MainLogs.component_id)
        )

        # Apply filters if provided
        if vehicle_id:
            query = query.filter(Vehicle.id == vehicle_id)
        if part:
            query = query.filter(Component.part.ilike(f"%{part}%"))  # Case-insensitive match
        if component:
            query = query.filter(Component.component.ilike(f"%{component}%"))  # Case-insensitive match
        if year:
            query = query.filter(func.extract('year', MainLogs.date) == year)
        if date_from:
            query = query.filter(MainLogs.date >= date_from)
        if date_to:
            query = query.filter(MainLogs.date <= date_to)

        # Debugging: Print the raw query results
        raw_results = query.all()
        print("Raw Query Results:", raw_results)

        # Transform results into a list of dictionaries
        processed_logs = [
            {
                "id": log.id,
                "date": log.date,
                "start_time": log.start_time,
                "end_time": log.end_time,
                "action": log.action,
                "kilometers": log.kilometers or "Sin KM registrado",
                "hobbs_meter": log.hobbs_meter or "Sin HRS registradas",
                "next_change": log.next_change or "-",
                "in_charge": log.in_charge,
                "comment": log.comment,
                "cost": log.cost or "Sin costo registrado",
                "code": log.code,
                "part": log.part,
                "component": log.component
            }
            for log in query.all()
        ]
    
        # Debugging: Print the processed logs
        print("Processed Logs:", processed_logs)

        return processed_logs
    
    except Exception as e:
        print(f"Error in get_filtered_logs: {e}")
        return []


