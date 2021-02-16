from flask import Flask, render_template, request, g, redirect, url_for, jsonify, abort
from markupsafe import escape
import db

app = Flask(__name__)

# have the DB submodule set itself up before we get started. groovy.
@app.before_first_request
def initialize():
    db.setup()

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/people', methods=['GET'])
def people():
    with db.get_db_cursor() as cur:
        cur.execute("SELECT * FROM person;")
        people = [(record[0], record[1]) for record in cur]

        return render_template("people.html", people=people)

@app.route('/people', methods=['POST'])
def new_person():
    with db.get_db_cursor(True) as cur:
        name = request.form.get("name", "unnamed friend")
        app.logger.info("Adding person %s", name)
        cur.execute("INSERT INTO person (name) values (%s)", (name,))
        
        return redirect(url_for('people'))

@app.route('/people/<int:person_id>', methods=['POST'])
def edit_name(person_id):
	with db.get_db_cursor(True) as cur:
		name = request.form.get("new_name", "No name")
		app.logger.info("Updating person %s name to %s", person_id, name);
		cur.execute("UPDATE person SET name = %s WHERE person_id = %s", (name, person_id))
		return redirect(url_for('people'))


@app.route('/api/foo')
def api_foo():
    data = {
        "message": "hello, world",
        "isAGoodExample": False,
        "aList": [1, 2, 3],
        "nested": {
            "key": "value"
        }
    }
    return jsonify(data)
	
@app.route('/people/<int:person_id>', methods=['GET'])
def show_person_details(person_id):
	with db.get_db_cursor() as cur:
		cur.execute("SELECT * FROM person WHERE person_id = %s", (person_id,))
		name = None
		name = [record[1] for record in cur]
		if len(name) == 0:
			abort(404)
		else:
			return render_template("person.html", person_id=person_id, name=name[0])
		

@app.errorhandler(404)
def error404(error):
	return render_template("404.html")

