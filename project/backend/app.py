import os
from flask import Flask, render_template, request, redirect, url_for, flash
from queries import *
from interactions import *

app = Flask(
    __name__, 
    template_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'templates'),
    static_folder=os.path.join(os.getcwd(), 'project', 'frontend', 'src', 'static')
)
app.secret_key = 'magickey'


# Route for menu page (homepage)
@app.route('/')
def maintenance_logs():
    vehicle_id = request.args.get('vehicle', type=int)
    component_id = request.args.get('component', type=int)
    year = request.args.get('year', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    # Fetch maintenance logs with applied filters
    logs = get_filtered_logs(session, vehicle_id, component_id, year, date_from, date_to)

    # Populate dropdown data
    vehicles = session.query(Vehicle).all()
    components = session.query(Component).all()
    years = session.query(func.extract('year', MainLogs.date)).distinct().order_by(func.extract('year', MainLogs.date)).all()

    return render_template(
        'maintenance_logs.html',
        logs=logs,
        vehicles=vehicles,
        components=components,
        years=[y[0] for y in years]  # Flatten result into a list of years
    )


if __name__ == '__main__':
    app.run(debug=True)