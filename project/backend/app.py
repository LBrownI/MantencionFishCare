import os
import pandas as pd
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from queries import *
from interactions import *
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz

app = Flask(
    __name__, 
    template_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'templates'),
    static_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'static')
)
app.secret_key = 'magickey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:fishybusiness@localhost/mantencion'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def get_local_time():
    return datetime.now(pytz.timezone('America/Santiago'))

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {"xlsx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_to_date(value):
    """Convert different date formats to proper SQL date format (YYYY-MM-DD)."""
    if pd.isna(value) or value == "":
        return None  # Handle empty values

    try:
        # If the value is already in datetime format (Excel auto-conversion)
        if isinstance(value, datetime):
            return value.date()  # Return only the date part
        
        # Try parsing common formats (26/04/2024 or 2021-04-21)
        return datetime.strptime(str(value), "%d/%m/%Y").date()  # Convert DD/MM/YYYY
    except ValueError:
        try:
            return datetime.strptime(str(value), "%Y-%m-%d").date()  # Convert YYYY-MM-DD
        except ValueError:
            print(f"Date conversion failed for value: {value}")
            return None  # Return None if conversion fails

def process_excel(file_path):
    df = pd.read_excel(file_path)

    # Delete existing logs (optional, if you want to replace all data)
    db.session.query(MainLogs).delete()

    for _, row in df.iterrows():
        # Check if vehicle exists
        vehicle = db.session.query(Vehicle).filter_by(code=row["Equipo"]).first()
        if not vehicle:
            print(f"Vehicle not found: {row['Equipo']}")
            continue

        # Check if component exists
        component = db.session.query(Component).filter_by(part=row["Parte"], component=row["Componente"]).first()
        if not component:
            print(f"Component not found: {row['Parte']} - {row['Componente']}")
            continue

        # Clean data
        log_date = convert_to_date(row["Fecha"])
        start_time = row["Hora Inicio"] if pd.notna(row["Hora Inicio"]) else None
        end_time = row["Hora Término"] if pd.notna(row["Hora Término"]) else None
        action = row["Acción"] if pd.notna(row["Acción"]) else None
        odometer_km = row["Odometro (Km.)"] if pd.notna(row["Odometro (Km.)"]) else None
        odometer_hrs = row["Odometro (hrs.)"] if pd.notna(row["Odometro (hrs.)"]) else None
        supervisor = row["Responsable"] if pd.notna(row["Responsable"]) else "N/A"  # Default value
        comment = row["Comentario"] if pd.notna(row["Comentario"]) else None
        cost = row["Costo"] if pd.notna(row["Costo"]) else None

        # Insert new log
        new_log = MainLogs(
            vehicle_id=vehicle.id,
            component_id=component.id,
            log_date=log_date,
            start_time=start_time,
            end_time=end_time,
            action=action,
            odometer_km=odometer_km,
            odometer_hrs=odometer_hrs,
            supervisor=supervisor,
            comment=comment,
            cost=cost
        )
        db.session.add(new_log)

    db.session.commit()
    print("Data successfully replaced.")

# Route for menu page (homepage)
@app.route('/')
def logs():
    # Filter parameters
    vehicle_code = request.args.get('code')  # Changed to string type
    part = request.args.get('part')
    component = request.args.get('component')
    year = request.args.get('year', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Handle T/S pairing
    vehicle_ids = []
    if vehicle_code and vehicle_code.startswith('T'):
        try:
            group_number = vehicle_code[1:]
            # Get IDs for both T and S versions
            vehicles = session.query(Vehicle.id).filter(
                Vehicle.code.in_([f'T{group_number}', f'S{group_number}'])
            ).all()
            vehicle_ids = [v.id for v in vehicles]
        except:
            vehicle_ids = []

    # Sorting parameters
    sort_by = request.args.get('sort_by', 'log_date')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Get filtered and paginated logs
    logs, total = get_filtered_logs(
        session=session,
        vehicle_ids=vehicle_ids,  # Now passing list of IDs
        part=part,
        component=component,
        year=year,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page
    )

    # Calculate total pages
    total_pages = (total + per_page - 1) // per_page

    # Populate dropdown data
    vehicles = session.query(Vehicle).all()
    components = session.query(Component).all()
    years = session.query(func.extract('year', MainLogs.log_date)).distinct().order_by(func.extract('year', MainLogs.log_date)).all()

    return render_template(
        'maintenance_logs.html',
        logs=logs,
        vehicles=vehicles,
        components=components,
        years=[y[0] for y in years],
        current_page=page,
        per_page=per_page,
        total_pages=total_pages,
        sort_by=sort_by,
        sort_dir=sort_dir,
        current_filters={
            'code': vehicle_code,  # Now passing the string code
            'part': part,
            'component': component,
            'year': year,
            'date_from': date_from,
            'date_to': date_to
        }
    )

@app.route('/log_detail', methods=['GET'])
def detailed_log():
    # Get the log ID
    log_id = request.args.get('id')

    if not log_id:
        return render_template('detailed_log.html', error_message="No log ID provided")

    # Fetch log details
    log_details = get_log_details(session, log_id)

    if not log_details:
        return render_template('detailed_log.html', error_message="Log not found")

    return render_template(
        'detailed_log.html',
        **log_details  # Pass all log details as template variables
    )

@app.route('/logs/<int:id>/delete', methods=['POST'])
def delete_log(id):
    if log_deleter(session, id):
        flash("Registro eliminado exitosamente", "detailed_log")
    else:
        flash("Error al eliminar el registro", "detailed_log")
    return redirect(url_for('logs'))

@app.route('/log_detail/<int:id>/update_cost', methods=['POST'])
def update_cost(id):
    new_cost = request.form.get('new_cost')
    if update_log_cost(session, id, new_cost):
        flash("Costo actualizado exitosamente", "main_logs")
    else:
        flash("Error al actualizar el costo", "main_logs")
    return redirect(url_for('detailed_log', id=id))

@app.route('/add_maintenance', methods=['GET', 'POST'])
def add_maintenance():
    if request.method == 'POST':
        # Base team selection (T1-T11)
        team = request.form.get('team')
        if not team or not team.startswith('T'):
            flash("Selección de equipo inválida", "add_maintenance")
            return redirect(url_for('add_maintenance'))

        try:
            team_number = int(team[1:])
            if team_number < 1 or team_number > 11:
                raise ValueError
        except ValueError:
            flash("Número de equipo inválido", "add_maintenance")
            return redirect(url_for('add_maintenance'))

        # Shared fields
        date_str = request.form.get('date')
        in_charge = request.form.get('in_charge')
        kilometers = request.form.get('kilometers') or None
        hobbs_meter = request.form.get('hobbs_meter') or None

        try:
            log_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else None
        except ValueError:
            flash("Formato de fecha inválido.", "add_maintenance")
            return redirect(url_for('add_maintenance'))

        # Get dynamic entries
        vehicle_codes = request.form.getlist('vehicle_type[]')
        start_times = request.form.getlist('start_time[]')
        end_times = request.form.getlist('end_time[]')
        parts = request.form.getlist('part[]')
        components = request.form.getlist('component[]')
        actions = request.form.getlist('action[]')
        comments = request.form.getlist('comment[]')

        # Validate equal number of entries
        if len(set(map(len, [vehicle_codes, start_times, end_times, parts, components, actions, comments]))) != 1:
            flash("Número de entradas inconsistentes", "add_maintenance")
            return redirect(url_for('add_maintenance'))

        # Process each entry
        for i in range(len(vehicle_codes)):
            vehicle_code = vehicle_codes[i]
            expected_prefixes = ['T', 'S']
            
            # Validate vehicle code format
            if not any(vehicle_code.startswith(p) for p in expected_prefixes):
                flash(f"Código de vehículo inválido en entrada {i+1}: {vehicle_code}", "add_maintenance")
                continue

            # Validate team number matches
            try:
                code_number = int(vehicle_code[1:])
                if code_number != team_number:
                    flash(f"El vehículo {vehicle_code} no pertenece al equipo {team}", "add_maintenance")
                    continue
            except ValueError:
                flash(f"Formato de vehículo inválido en entrada {i+1}: {vehicle_code}", "add_maintenance")
                continue

            # Look up vehicle
            vehicle = session.query(Vehicle).filter_by(code=vehicle_code).first()
            if not vehicle:
                flash(f"Vehículo {vehicle_code} no encontrado en entrada {i+1}", "add_maintenance")
                continue

            # Convert times
            try:
                start_time = datetime.strptime(start_times[i], '%H:%M').time() if start_times[i] else None
                end_time = datetime.strptime(end_times[i], '%H:%M').time() if end_times[i] else None
            except ValueError:
                flash(f"Formato de hora inválido en entrada {i+1}", "add_maintenance")
                continue

            # Look up component
            component_obj = session.query(Component).filter_by(
                part=parts[i],
                component=components[i]
            ).first()
            if not component_obj:
                flash(f"Componente no encontrado para entrada {i+1}: {parts[i]} - {components[i]}", "add_maintenance")
                continue

            # Create log entry
            new_log = MainLogs(
                vehicle_id=vehicle.id,
                log_date=log_date,
                start_time=start_time,
                end_time=end_time,
                action=actions[i],
                component_id=component_obj.id,
                odometer_km=kilometers,
                odometer_hrs=hobbs_meter,
                supervisor=in_charge,
                comment=comments[i],
                cost=None
            )
            session.add(new_log)

        try:
            session.commit()
            flash("Registros añadidos exitosamente.", "add_maintenance")
        except Exception as e:
            session.rollback()
            flash(f"Error al guardar los registros: {str(e)}", "add_maintenance")

        return redirect(url_for('add_maintenance'))

    # GET request handling
    parts = session.query(Component.part).distinct().all()
    components = session.query(Component.component).distinct().all()
    vehicles = session.query(Vehicle).filter(Vehicle.code.startswith('T')).all()

    return render_template('add_maintenance.html',
                          parts=parts,
                          components=components,
                          vehicles=vehicles)

@app.route('/get_parts/<vehicle_type>')
def get_parts(vehicle_type):
    parts = session.query(Component.part).filter_by(vehicle_type=vehicle_type).distinct().all()
    return jsonify([p[0] for p in parts])

@app.route('/get_components/<vehicle_type>/<part>')
def get_components(vehicle_type, part):
    components = session.query(Component.component).filter_by(
        vehicle_type=vehicle_type,
        part=part
    ).distinct().all()
    return jsonify([c[0] for c in components])

@app.route('/download_logs')
def download_logs():
    # Generate timestamp
    local_time = get_local_time()
    timestamp = local_time.strftime("%Y-%m-%d_%H%M%S")
    filename = f"mantenimiento_{timestamp}.xlsx"

    # Get filter parameters from request
    vehicle_id = request.args.get('code', type=int)
    part = request.args.get('part')
    component = request.args.get('component')
    year = request.args.get('year', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Base query
    query = (
        db.session.query(
            Vehicle.code.label("Equipo"),
            Component.part.label("Parte"),
            Component.component.label("Componente"),
            MainLogs.log_date,
            MainLogs.start_time,
            MainLogs.end_time,
            MainLogs.action,
            MainLogs.odometer_km.label("Kilometros"),
            MainLogs.odometer_hrs.label("Odometro (hrs.)"),
            MainLogs.supervisor.label("Responsable"),
            MainLogs.comment.label("Comentario"),
            MainLogs.cost.label("Costo")
        )
        .join(Vehicle, MainLogs.vehicle_id == Vehicle.id)
        .join(Component, MainLogs.component_id == Component.id)
    )

    # Apply filters
    if vehicle_id:
        query = query.filter(Vehicle.id == vehicle_id)
    if part:
        query = query.filter(Component.part.ilike(f"%{part}%"))
    if component:
        query = query.filter(Component.component.ilike(f"%{component}%"))
    if year:
        query = query.filter(db.extract('year', MainLogs.log_date) == year)
    if date_from:
        query = query.filter(MainLogs.log_date >= date_from)
    if date_to:
        query = query.filter(MainLogs.log_date <= date_to)

    # Execute query
    logs = query.all()

    # Convert to DataFrame
    df = pd.DataFrame(logs, columns=[
        "Equipo", "Parte", "Componente", "Fecha", "Hora Inicio", "Hora Termino", 
        "Acción", "Odometro (Km.)", "Odometro (hrs.)", "Responsable", "Comentario", "Costo"
    ])

    # Format date
    df['Fecha'] = pd.to_datetime(df['Fecha']).dt.strftime('%d/%m/%Y')

    # Save to Excel in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Registros')
        
        # Add auto-filter
        worksheet = writer.sheets['Registros']
        worksheet.autofilter(0, 0, 0, len(df.columns)-1)
        
        # Add column formatting
        for idx, col in enumerate(df):
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1
            worksheet.set_column(idx, idx, max_len)

    output.seek(0)

    # Create filename with date filter if applicable
    filename = "registros_mantenimiento"
    if date_from and date_to:
        filename += f"_{date_from}_a_{date_to}"
    elif date_from:
        filename += f"_desde_{date_from}"
    elif date_to:
        filename += f"_hasta_{date_to}"
    filename += ".xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload_logs", methods=["POST"])
def upload_logs():
    if "file" not in request.files:
        flash("No file part")
        return redirect(url_for("logs"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect(url_for("logs"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        process_excel(file_path)
        flash("Excel data uploaded successfully!", "main_logs")
        return redirect(url_for("logs"))

    flash("Invalid file type. Please upload an Excel file.", "main_logs")
    return redirect(url_for("logs"))

if __name__ == '__main__':
    app.run(debug=True)