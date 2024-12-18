import os
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DECIMAL, Date, Text, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# docker run --name fish-mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=fishybusiness -d mysql

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

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into Vehicle table
vehicle_data = [
    {'id': 1, 'code': 'T1', 'type': 'Tracto Camión', 'model': 'Tracto Camión 1'},
    {'id': 2, 'code': 'S1', 'type': 'Semiremolque', 'model': 'Semiremolque 1'},
    {'id': 3, 'code': 'T2', 'type': 'Tracto Camión', 'model': 'Tracto Camión 2'},
    {'id': 4, 'code': 'S2', 'type': 'Semiremolque', 'model': 'Semiremolque 2'},
    {'id': 5, 'code': 'T3', 'type': 'Tracto Camión', 'model': 'Tracto Camión 3'},
    {'id': 6, 'code': 'S3', 'type': 'Semiremolque', 'model': 'Semiremolque 3'},
    {'id': 7, 'code': 'T4', 'type': 'Tracto Camión', 'model': 'Tracto Camión 4'},
    {'id': 8, 'code': 'S4', 'type': 'Semiremolque', 'model': 'Semiremolque 4'},
    {'id': 9, 'code': 'T5', 'type': 'Tracto Camión', 'model': 'Tracto Camión 5'},
    {'id': 10, 'code': 'S5', 'type': 'Semiremolque', 'model': 'Semiremolque 5'},
    {'id': 11, 'code': 'T6', 'type': 'Tracto Camión', 'model': 'Tracto Camión 6'},
    {'id': 12, 'code': 'S6', 'type': 'Semiremolque', 'model': 'Semiremolque 6'},
    {'id': 13, 'code': 'T7', 'type': 'Tracto Camión', 'model': 'Tracto Camión 7'},
    {'id': 14, 'code': 'S7', 'type': 'Semiremolque', 'model': 'Semiremolque 7'},
    {'id': 15, 'code': 'T8', 'type': 'Tracto Camión', 'model': 'Tracto Camión 8'},
    {'id': 16, 'code': 'S8', 'type': 'Semiremolque', 'model': 'Semiremolque 8'},
    {'id': 17, 'code': 'T9', 'type': 'Tracto Camión', 'model': 'Tracto Camión 9'},
    {'id': 18, 'code': 'S9', 'type': 'Semiremolque', 'model': 'Semiremolque 9'},
    {'id': 19, 'code': 'T10', 'type': 'Tracto Camión', 'model': 'Tracto Camión 10'},
    {'id': 20, 'code': 'S10', 'type': 'Semiremolque', 'model': 'Semiremolque 10'},
    {'id': 21, 'code': 'T11', 'type': 'Tracto Camión', 'model': 'Tracto Camión 11'},
    {'id': 22, 'code': 'S11', 'type': 'Semiremolque', 'model': 'Semiremolque 11'},
    {'id': 23, 'code': 'T12', 'type': 'Tracto Camión', 'model': 'Not available'},
    {'id': 24, 'code': 'S12', 'type': 'Semiremolque', 'model': 'Not available'}
]

for data in vehicle_data:
    vehicle = Vehicle(**data)
    session.add(vehicle)
session.commit()

# Insert data into Components table
component_data = [
    # Semiremolque 1. Estanque
    {'id': 101, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Chapa'},
    {'id': 102, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Mamparo Tk1'},
    {'id': 103, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Mamparo Tk2'},
    {'id': 104, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Mamparo Tk3'},
    {'id': 105, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Mamparo Tk4'},
    {'id': 106, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Tk1'},
    {'id': 107, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Tk2'},
    {'id': 108, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Tk3'},
    {'id': 109, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Tk4'},
    {'id': 110, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Escalera'},
    {'id': 111, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Baranda'},
    {'id': 112, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'General'},
    {'id': 113, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Airlift Tk1'},
    {'id': 114, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Airlift Tk2'},
    {'id': 115, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Airlift Tk3'},
    {'id': 116, 'vehicle_type': 'S', 'part': 'Estanque', 'component': 'Airlift Tk4'},

    # Semiremolque 2. Chasis
    {'id': 201, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Soporte cilindros'},
    {'id': 202, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Viga derecha'},
    {'id': 203, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Viga izquierda'},
    {'id': 204, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Quinta rueda'},
    {'id': 205, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°1 delantera'},
    {'id': 206, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°2'},
    {'id': 207, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°3'},
    {'id': 208, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°4'},
    {'id': 209, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°5'},
    {'id': 210, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°6'},
    {'id': 211, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°7'},
    {'id': 212, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cuna N°8 trasera'},
    {'id': 213, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Parachoque'},
    {'id': 214, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Tapabarro eje levante'},
    {'id': 215, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Tapabarro eje trasero'},
    {'id': 216, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Cubierta Genset'},
    {'id': 217, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'Eje levante'},
    {'id': 218, 'vehicle_type': 'S', 'part': 'Chasis', 'component': 'General'},

    # Semiremolque 3. Salamaquina
    {'id': 301, 'vehicle_type': 'S', 'part': 'Salamaquina', 'component': 'Cubierta'},
    {'id': 302, 'vehicle_type': 'S', 'part': 'Salamaquina', 'component': 'Piso'},
    {'id': 303, 'vehicle_type': 'S', 'part': 'Salamaquina', 'component': 'Estructura'},
    {'id': 304, 'vehicle_type': 'S', 'part': 'Salamaquina', 'component': 'General'},

    # Semiremolque 4. Piping
    {'id': 401, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Válvula peces'},
    {'id': 402, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Aspersión'},
    {'id': 403, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Succión'},
    {'id': 404, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Aire'},
    {'id': 405, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Aire airlift'},
    {'id': 406, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Saturada'},
    {'id': 407, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Presurizada'},
    {'id': 408, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Oxigeno'},
    {'id': 409, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Difusores Tk1'},
    {'id': 410, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Difusores Tk2'},
    {'id': 411, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Difusores Tk3'},
    {'id': 412, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Difusores Tk4'},
    {'id': 413, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Saturador 1'},
    {'id': 414, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Saturador 2'},
    {'id': 415, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Saturador 3'},
    {'id': 416, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'Saturador 4'},
    {'id': 417, 'vehicle_type': 'S', 'part': 'Piping', 'component': 'General'},

    # Semiremolque 5. Rodado
    {'id': 501, 'vehicle_type': 'S', 'part': 'Rodado', 'component': 'Buje trasero'},
    {'id': 502, 'vehicle_type': 'S', 'part': 'Rodado', 'component': 'Buje levante'},
    {'id': 503, 'vehicle_type': 'S', 'part': 'Rodado', 'component': 'Ejes levante'},
    {'id': 504, 'vehicle_type': 'S', 'part': 'Rodado', 'component': 'Ejes Trasero'},
    {'id': 505, 'vehicle_type': 'S', 'part': 'Rodado', 'component': 'General'},

    # Semiremolque 6. Frenos
    {'id': 601, 'vehicle_type': 'S', 'part': 'Frenos', 'component': 'Válvulas'},
    {'id': 602, 'vehicle_type': 'S', 'part': 'Frenos', 'component': 'Balatas o tambores'},
    {'id': 603, 'vehicle_type': 'S', 'part': 'Frenos', 'component': 'Pulmón freno'},
    {'id': 604, 'vehicle_type': 'S', 'part': 'Frenos', 'component': 'Flexibles línea'},
    {'id': 605, 'vehicle_type': 'S', 'part': 'Frenos', 'component': 'General'},

    # Semiremolque 7. Neumáticos
    {'id': 701, 'vehicle_type': 'S', 'part': 'Neumáticos', 'component': 'Neumáticos eje trasero'},
    {'id': 702, 'vehicle_type': 'S', 'part': 'Neumáticos', 'component': 'Neumáticos eje levante'},
    {'id': 703, 'vehicle_type': 'S', 'part': 'Neumáticos', 'component': 'General'},

    # Semiremolque 8. Ejes
    {'id': 801, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Pulmón eje trasero'},
    {'id': 802, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Pulmón eje levante'},
    {'id': 803, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Válvulas'},
    {'id': 804, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Retenes eje trasero'},
    {'id': 805, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Retenes eje levante'},
    {'id': 806, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Rodamientos eje trasero'},
    {'id': 807, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Rodamientos eje levante'},
    {'id': 808, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'Flexibles línea'},
    {'id': 809, 'vehicle_type': 'S', 'part': 'Ejes', 'component': 'General'},
   
    # Semiremolque 9. Generador
    {'id': 901, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'Tubo escape'},
    {'id': 902, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'Soportes'},
    {'id': 903, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'Arranque'},
    {'id': 904, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'Motor'},
    {'id': 905, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'Tk combustible'},
    {'id': 906, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'Filtros y aceite'},
    {'id': 907, 'vehicle_type': 'S', 'part': 'Generador', 'component': 'General'},

    # Semiremolque 10. Bombas
    {'id': 1001, 'vehicle_type': 'S', 'part': 'Bombas', 'component': 'Sellos'},
    {'id': 1002, 'vehicle_type': 'S', 'part': 'Bombas', 'component': 'Rodamientos'},
    {'id': 1003, 'vehicle_type': 'S', 'part': 'Bombas', 'component': 'General'},

    # Semiremolque 11. Soplador
    {'id': 1101, 'vehicle_type': 'S', 'part': 'Soplador', 'component': 'Alabes'},
    {'id': 1102, 'vehicle_type': 'S', 'part': 'Soplador', 'component': 'Rodamientos'},
    {'id': 1103, 'vehicle_type': 'S', 'part': 'Soplador', 'component': 'Filtros'},
    {'id': 1104, 'vehicle_type': 'S', 'part': 'Soplador', 'component': 'General'},

    # Semiremolque 12. Electrónica
    {'id': 1201, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Electro válvula Tk1'},
    {'id': 1202, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Electro válvula Tk2'},
    {'id': 1203, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Electro válvula Tk3'},
    {'id': 1204, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Electro válvula Tk4'},
    {'id': 1205, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Sensor Tk 1'},
    {'id': 1206, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Sensor Tk 2'},
    {'id': 1207, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Sensor Tk 3'},
    {'id': 1208, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Sensor Tk 4'},
    {'id': 1209, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Fuente de poder 220 a 12/24V'},
    {'id': 1210, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Cargador batería'},
    {'id': 1211, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Transductores'},
    {'id': 1212, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Controlador'},
    {'id': 1213, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Notebook o Tablet'},
    {'id': 1214, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'Alarma'},
    {'id': 1215, 'vehicle_type': 'S', 'part': 'Electrónica', 'component': 'General'},

    # Semiremolque 13. Luces
    {'id': 1301, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'Tk1'},
    {'id': 1302, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'Tk2'},
    {'id': 1303, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'Tk3'},
    {'id': 1304, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'Tk4'},
    {'id': 1305, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'Semirremolque'},
    {'id': 1306, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'Canalización eléctrica'},
    {'id': 1307, 'vehicle_type': 'S', 'part': 'Luces', 'component': 'General'},
    
    # Semiremolque 14. Equipos
    {'id': 1401, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'Generador'},
    {'id': 1402, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'Bomba 1'},
    {'id': 1403, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'Bomba backup'},
    {'id': 1404, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'Soplador'},
    {'id': 1405, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'Canalización eléctrica fuerza'},
    {'id': 1406, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'General'},
    {'id': 1407, 'vehicle_type': 'S', 'part': 'Equipos', 'component': 'Bateria'},
    
    # Semiremolque 15. Tablero
    {'id': 1501, 'vehicle_type': 'S', 'part': 'Tablero', 'component': 'Protección'},
    {'id': 1502, 'vehicle_type': 'S', 'part': 'Tablero', 'component': 'VDF'},
    {'id': 1503, 'vehicle_type': 'S', 'part': 'Tablero', 'component': 'Control'},
    {'id': 1504, 'vehicle_type': 'S', 'part': 'Tablero', 'component': 'General'},

    # Tracto camion 16. Vigas
    {'id': 1601, 'vehicle_type': 'T', 'part': 'Vigas', 'component': 'Viga Principal'},
    {'id': 1602, 'vehicle_type': 'T', 'part': 'Vigas', 'component': 'Travesaños'},
    {'id': 1603, 'vehicle_type': 'T', 'part': 'Vigas', 'component': 'General'},

    # Tracto camion 17. Adosados
    {'id': 1701, 'vehicle_type': 'T', 'part': 'Adosados', 'component': 'Quinta Rueda'},
    {'id': 1702, 'vehicle_type': 'T', 'part': 'Adosados', 'component': 'Placa montaje'},
    {'id': 1703, 'vehicle_type': 'T', 'part': 'Adosados', 'component': 'Conectores Electricos'},
    {'id': 1704, 'vehicle_type': 'T', 'part': 'Adosados', 'component': 'Conectores Neumaticos'},
    {'id': 1705, 'vehicle_type': 'T', 'part': 'Adosados', 'component': 'General'},

    # Tracto camion 18. Interior
    {'id': 1801, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Tablero'},
    {'id': 1802, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Asientos'},
    {'id': 1803, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Litera'},
    {'id': 1804, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Tapices'},
    {'id': 1805, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Cinturones'},
    {'id': 1806, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Volante'},
    {'id': 1807, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'Telecomandos'},
    {'id': 1808, 'vehicle_type': 'T', 'part': 'Interior', 'component': 'General'},

    # Tracto camion 19. Exterior
    {'id': 1901, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Puertas'},
    {'id': 1902, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Espejos'},
    {'id': 1903, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Deflectores'},
    {'id': 1904, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Pisaderas'},
    {'id': 1905, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Parachoques'},
    {'id': 1906, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Tapabarros'},
    {'id': 1907, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'Iluminacion'},
    {'id': 1908, 'vehicle_type': 'T', 'part': 'Exterior', 'component': 'General'},

    # Tracto camion 20. Eje Direccional
    {'id': 2001, 'vehicle_type': 'T', 'part': 'Eje Direccional', 'component': 'Neumaticos'},
    {'id': 2002, 'vehicle_type': 'T', 'part': 'Eje Direccional', 'component': 'Frenos'},
    {'id': 2003, 'vehicle_type': 'T', 'part': 'Eje Direccional', 'component': 'Suspension'},
    {'id': 2004, 'vehicle_type': 'T', 'part': 'Eje Direccional', 'component': 'Reten'},
    {'id': 2005, 'vehicle_type': 'T', 'part': 'Eje Direccional', 'component': 'General'},

    # Tracto camion 21. Motor
    {'id': 2101, 'vehicle_type': 'T', 'part': 'Motor', 'component': 'Arranque'},
    {'id': 2102, 'vehicle_type': 'T', 'part': 'Motor', 'component': 'Alimentacion'},
    {'id': 2103, 'vehicle_type': 'T', 'part': 'Motor', 'component': 'Generacion'},
    {'id': 2104, 'vehicle_type': 'T', 'part': 'Motor', 'component': 'Refrigeracion'},
    {'id': 2105, 'vehicle_type': 'T', 'part': 'Motor', 'component': 'Soportes'},
    {'id': 2106, 'vehicle_type': 'T', 'part': 'Motor', 'component': 'General'},

    # Tracto camion 22. Embrague
    {'id': 2201, 'vehicle_type': 'T', 'part': 'Embrague', 'component': 'Regulacion'},
    {'id': 2202, 'vehicle_type': 'T', 'part': 'Embrague', 'component': 'General'},

    # Tracto camion 23. Transmisio
    {'id': 2301, 'vehicle_type': 'T', 'part': 'Transmision', 'component': 'Mando'},
    {'id': 2302, 'vehicle_type': 'T', 'part': 'Transmision', 'component': 'Soportes'},
    {'id': 2303, 'vehicle_type': 'T', 'part': 'Transmision', 'component': 'General'},

    # Tracto camion 24. Cardan
    {'id': 2401, 'vehicle_type': 'T', 'part': 'Cardan', 'component': 'Cruceta'},
    {'id': 2402, 'vehicle_type': 'T', 'part': 'Cardan', 'component': 'General'},
    {'id': 2403, 'vehicle_type': 'T', 'part': 'Cardan', 'component': 'Soportes'},

    # Tracto camion 25. Eje Trasero
    {'id': 2501, 'vehicle_type': 'T', 'part': 'Eje Trasero', 'component': 'Neumaticos'},
    {'id': 2502, 'vehicle_type': 'T', 'part': 'Eje Trasero', 'component': 'Frenos'},
    {'id': 2503, 'vehicle_type': 'T', 'part': 'Eje Trasero', 'component': 'Suspension'},
    {'id': 2504, 'vehicle_type': 'T', 'part': 'Eje Trasero', 'component': 'Reten'},
    {'id': 2505, 'vehicle_type': 'T', 'part': 'Eje Trasero', 'component': 'General'},

    # Tracto camion 26. Eje Levante
    {'id': 2601, 'vehicle_type': 'T', 'part': 'Eje Levante', 'component': 'Neumaticos'},
    {'id': 2602, 'vehicle_type': 'T', 'part': 'Eje Levante', 'component': 'Frenos'},
    {'id': 2603, 'vehicle_type': 'T', 'part': 'Eje Levante', 'component': 'Suspension'},
    {'id': 2604, 'vehicle_type': 'T', 'part': 'Eje Levante', 'component': 'Reten'},
    {'id': 2605, 'vehicle_type': 'T', 'part': 'Eje Levante', 'component': 'General'}
]

for data in component_data:
    component = Component(**data)
    session.add(component)
session.commit()

# Insert data into MaintenanceLogs
maintenance_data = [
    {
        'id': 1,
        'vehicle_id': 1,  
        'date': '2024-04-08',
        'start_time': None,
        'end_time': None,
        'action': 'Instalación',
        'component_id': 408,  # Manómetro de oxígeno (Piping -> Oxígeno)
        'kilometers': None,
        'hobbs_meter': None,
        'next_change': None,
        'in_charge': 'Desconocido',
        'comment': 'Se entrega 01 manómetro de oxígeno (nuevo)',
        'cost': None,
    },
    {
        'id': 2,
        'vehicle_id': 1,
        'date': '2024-04-12',
        'start_time': None,
        'end_time': None,
        'action': 'Relleno', 
        'component_id': 2104,  # Motor -> Refrigeración
        'kilometers': None,
        'hobbs_meter': None,
        'next_change': None,
        'in_charge': 'Desconocido',
        'comment': 'Se rellenó con aceite tracto camión 4 Lt.',
        'cost': None,
    },
    {   
        'id': 3,
        'vehicle_id': 2,  
        'date': '2024-04-22',
        'start_time': None,
        'end_time': None,
        'action': 'Cambio',
        'component_id': 603,  # Frenos -> Pulmón freno (Semirremolque)
        'kilometers': None,
        'hobbs_meter': None,
        'next_change': None,
        'in_charge': 'Desconocido',
        'comment': 'Cambio pulmón de aire',
        'cost': None,
    },
    {
        'id': 4,
        'vehicle_id': 1,
        'date': '2024-04-26',
        'start_time': None,
        'end_time': None,
        'action': 'Cambio',
        'component_id': 2104,  # Motor -> Refrigeración
        'kilometers': 356867,
        'hobbs_meter': None,
        'next_change': None,
        'in_charge': 'Desconocido',
        'comment': 'Se cambió líquido refrigerante radiador km 356867',
        'cost': None,
    },
    {
        'id': 5,
        'vehicle_id': 2,
        'date': '2024-04-26',
        'start_time': None,
        'end_time': None,
        'action': 'Cambio',
        'component_id': 1305,  # Luces -> Iluminación trocha (amarillas)
        'kilometers': None,
        'hobbs_meter': None,
        'next_change': None,
        'in_charge': 'Desconocido',
        'comment': 'Se cambiaron luces de trocha (amarillas)',
        'cost': None,
    }
]

for data in maintenance_data:
    maintenance = MainLogs(**data)
    session.add(maintenance)
session.commit()


# Insert data into TechnicalReview table
tech_review_data = [
]

for data in tech_review_data:
    tech_review = TechnicalReview(**data)
    session.add(tech_review)
session.commit()

# Close the session
session.close()
