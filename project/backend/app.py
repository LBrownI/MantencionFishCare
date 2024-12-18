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
    vehicle_id = request.args.get('code', type=int)
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

@app.route('/add_maintenance', methods=['GET', 'POST'])
def add_maintenance():
    if request.method == 'POST':
        # Get form data
        maintenance_data = {
            'vehicle': request.form['vehicle'],
            'part': request.form['part'],
            'component': request.form['component'],
            'date': datetime.strptime(request.form['date'], '%Y-%m-%d'),
            'start_time': datetime.strptime(request.form['start_time'], '%H:%M') if request.form['start_time'] else None,
            'end_time': datetime.strptime(request.form['end_time'], '%H:%M') if request.form['end_time'] else None,
            'action': request.form['action'],
            'kilometers': request.form['kilometers'] or None,
            'hobbs_meter': request.form['hobbs_meter'] or None,
            'next_change': request.form['next_change'] or None,
            'in_charge': request.form['in_charge'],
            'comment': request.form['comment'],
            'cost': request.form['cost'] or None
        }

        # Call the query function to add the maintenance log
        result = add_maintenance_to_db(session, maintenance_data)

        if "exitosamente" in result:
            flash(result, 'success')
            return redirect(url_for('maintenance_logs'))  # Redirect to a view logs page or other relevant page
        else:
            flash(result, 'error')

    # Fetch data for dropdowns (parts, components, vehicles)
    parts = session.query(Component.part).distinct().all()
    components = session.query(Component.component).distinct().all()
    vehicles = session.query(Vehicle.code).all()

    return render_template('add_maintenance.html', parts=parts, components=components, vehicles=vehicles)


if __name__ == '__main__':
    app.run(debug=True)