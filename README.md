# Digitalización Mantención FishCare

El proyecto **Digitalización Mantención FishCare** permite gestionar y automatizar el mantenimiento de vehículos y components usados en el transporte de peces vivos. A través de esta plataforma, se registran y siguen las actiones de mantenimiento, revisiones técnicas, costs, y in_charges de cada registro. La base de datos, gestionada con **SQLAlchemy**, permite mantener un historial detallado de los vehículos y sus components, facilitando la toma de decisiones para optimizar operaciones y reducir tiempos de inactividad. Para la visualización se utiliza una implementación web con **Flask** para generar una pagina web donde ver las diferentes interactiones.

---

## Features

- **Página de Historial:**
  Visualiza y gestiona todo el historial de mantenimientos realizados en los vehículos, incluyendo reparaciones, cambios de piezas e instalaciones, con la opción de añadir nuevos registros.

- **Página de Registro de Mantenimiento:**
  Permite registrar nuevos mantenimientos, detallando la acción realizada, components involucrados, kilómetros recorridos, cost y otros datos relacionados con la operación de mantenimiento.

- **Página de Revisión Técnica:**
  Accede a la información de las revisiones técnicas realizadas a los vehículos, incluyendo dates, in_charges y próximas revisiones programadas.

- **Página de Información de Camiones:**
  Muestra detalles sobre los camiones, como su número de identificación, type, model y otros datos relevantes, además de permitir la edición o adición de nueva información relacionada.


---

## Tecnologias Usadas

- **Backend**:
  - Python   
  - Flask
  - SQLAlchemy
- **Frontend**:
  - HTML
  - CSS
  - JavaScript 
- **Database**:
  - MySQL
- **Others**:
  - Docker
  - Microsoft Azure (in-progress)

---


## Installation and Setup

Follow one of the three methods below to set up the project:

---

### 1. **Connect to Azure Virtual Machine (VM)**

go to http://172.214.209.5:5000/

- BEWARE: This is 1 commit behind 
- Feature missing: add remuneration button on /remuneration page. To add a remuneration go manually to /add_remuneration
---

### 2. **Manual Setup (Old School)**

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/LBrownI/RRHH-system.git
   cd RRHH-system
   ```

2. **Install Python and dependencies**:  
   - Install Python 3.12 or higher. (https://www.python.org/downloads/) 
   - Install Docker (https://www.docker.com/)
   - Install dependencies (inside project folder):  
     ```bash
     pip install -r requirements.txt
     ```

3. **Set up the database**: 
   - With docker installed do in terminal (inside project folder)
    ```bash
     docker compose up
     ```
     If you have the port occupied edit the compose.yml in project folder to fit your needs.
   - Setup a environment variable named: MYSQL_ROOT_PASSWORD and value: a301rrhh (or edit password in tables.py, queries.py and load_db.py)
   - Initialize the database with SQLAlchemy models by running the setup script load_db.py (located on /project/setup/).  

4. **Run the application**:  
   Start the Flask development server (in folder project/backend/):  
   ```bash
   python app.py
   ```

5. **Access the application**:  
   Open a browser and navigate to `http://localhost:5000`.

---

Choose the method that best suits your environment or deployment needs.


