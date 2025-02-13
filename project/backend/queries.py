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
            MainLogs.id, MainLogs.log_date, MainLogs.start_time, MainLogs.end_time,
            MainLogs.action, MainLogs.odometer_km, MainLogs.odometer_hrs,
            MainLogs.supervisor, MainLogs.comment, MainLogs.cost,
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
                "log_date": log.log_date,
                "start_time": log.start_time,
                "end_time": log.end_time,
                "action": log.action,
                "odometer_km": log.odometer_km or "Sin KM registrado",
                "odometer_hrs": log.odometer_hrs or "Sin HRS registradas",
                "supervisor": log.supervisor,
                "comment": log.comment,
                "cost": log.cost or "Sin costo registrado",
                "code": log.code,
                "part": log.part,
                "component": log.component
            }
    except Exception as e:
        print(f"Error fetching log details: {e}")
        return None
    

def get_filtered_logs(session, vehicle_ids=None, part=None, component=None, year=None, date_from=None, date_to=None, 
                     sort_by='log_date', sort_dir='desc', page=1, per_page=20):
    try:
        # Base query
        query = (
            session.query(
                MainLogs.id, MainLogs.log_date, MainLogs.start_time, MainLogs.end_time,
                MainLogs.action, MainLogs.odometer_km, MainLogs.odometer_hrs,
                MainLogs.supervisor, MainLogs.comment, MainLogs.cost,
                Vehicle.code,
                Component.part,
                Component.component
            )
            .outerjoin(Vehicle, Vehicle.id == MainLogs.vehicle_id)
            .outerjoin(Component, Component.id == MainLogs.component_id)
        )

        # Apply filters
        if vehicle_ids:
            query = query.filter(Vehicle.id.in_(vehicle_ids))
        if part:
            query = query.filter(Component.part.ilike(f"%{part}%"))
        if component:
            query = query.filter(Component.component.ilike(f"%{component}%"))
        if year:
            query = query.filter(func.extract('year', MainLogs.log_date) == year)
        if date_from:
            query = query.filter(MainLogs.log_date >= date_from)
        if date_to:
            query = query.filter(MainLogs.log_date <= date_to)

        # Sorting logic
        sort_mapping = {
            'log_date': MainLogs.log_date,
            'code': Vehicle.code,
            'part': Component.part,
            'component': Component.component,
            'action': MainLogs.action,
            'supervisor': MainLogs.supervisor,
            'cost': MainLogs.cost
        }
        
        sort_column = sort_mapping.get(sort_by, MainLogs.log_date)
        if sort_dir == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Pagination
        total = query.count()
        query = query.offset((page - 1) * per_page).limit(per_page)

        # Process results
        raw_results = query.all()
        processed_logs = [
            {
                "id": log.id,
                "log_date": log.log_date,
                "code": log.code,
                "part": log.part,
                "component": log.component,
                "action": log.action,
                "supervisor": log.supervisor,
                "cost": log.cost or "Sin costo registrado"
            }
            for log in raw_results
        ]

        return processed_logs, total

    except Exception as e:
        print(f"Error in get_filtered_logs: {e}")
        return [], 0