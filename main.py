from flask import Flask, render_template, request, redirect
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
from math import ceil

app = Flask(__name__)
conn_str = "mysql://root:1234@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route("/")
def index():
	return render_template("index.html")

# View boats and search
@app.route("/boats/", methods=["GET"])
@app.route("/boats/<page>", methods=["GET", "POST"])
def get_boats(page = 1):
	page = 1 if int(page) < 1 else int(page)
	per_page = 10  # num of records to show per page
	max_page = 0
	boats = None

	if request.method == "POST":
		type = request.form["search_type"]
		value = request.form["search_value"]

		max_page = ceil(conn.execute(text(f"select count(*) / {per_page} from boats")).first()[0])

		if not value:
			boats = conn.execute(text(f"select * from boats limit {per_page} offset {(page - 1) * per_page}")).all()

			return render_template("boats.html", boats = boats, page = page, per_page = per_page, max_page = max_page)

		value = int(value) if value.isnumeric() else f"'{value}'"

		max_page = ceil(conn.execute(text(f"select count(*) / {per_page} from boats where {type} = {value}")).first()[0])

		boats = conn.execute(text(f"select * from boats where {type} = {value} limit {per_page} offset {(page - 1) * per_page}")).all()

	else:
		boats = conn.execute(text(f"select * from boats limit {per_page} offset {(page - 1) * per_page}")).all()

	return render_template("boats.html", boats = boats, page = page, per_page = per_page, max_page = max_page)

# View data for boat
@app.route("/boats/view/<id>", methods=["GET"])
def get_boat_data(id = 1):
	data = conn.execute(text(f"select * from boats where id = {id}")).first()

	return render_template("boat_info.html", boat = data)

# Manage page
@app.route("/manage/")
def navigate_to_manage():
	return render_template("manage.html")

# Create boat
@app.route("/manage/add/", methods=["GET"])
def create_get_request():
	return render_template("boats_create.html")

@app.route("/manage/add/", methods=["POST"])
def create_boat():
	id = conn.execute(text(f"select max(id) + 1 from boats")).first()[0]

	try:
		conn.execute(
			text(f"insert into boats values ({id}, :name, :type, :owner_id, :rental_price)"),
			request.form
		)
		return render_template("boats_create.html", error=None, success="Data inserted successfully!")

	except:
		return render_template("boats_create.html", error= "Data could not be inserted", success=None)

# Delete boat
@app.route("/manage/delete/", methods=["GET"])
def create_delete_boat():
	return render_template("boats_delete.html")

@app.route("/manage/delete/", methods=["POST"])
def delete_boat():
	try:
		id = conn.execute(
			text(f"select id from boats where id = :id"),
			request.form
		).first()

		if id == None:
			return render_template("boat_delete.html", error = "No data found", success = None)

		conn.execute(
			text(f"delete from boats where id = :id"),
			request.form
		)

		return render_template("boats_delete.html", error = None, success = "Data deleted successfully!")
	except:
		return render_template("boats_delete.html", error = "Boat not found", success = None)

# Update boat
@app.route("/manage/update/", methods=["GET"])
def create_update_boat():
	return render_template("boats_update.html")

@app.route("/manage/update/", methods=["POST"])
def update_boat():
	try:
		id = conn.execute(
			text(f"select id from boats where id = :id"),
			request.form
		).first()

		if id == None:
			return render_template("boats_update.html", error = "No data found", success = None)

		conn.execute(
			text("update boats set name = :name, type = :type, owner_id = :owner_id, rental_price = :rental_price where id = :id"),
			request.form
		)

		return render_template("boats_update.html", error = None, success = "Data updated successfully!")
	except Exception as e:
		print(e)
		return render_template("boats_update.html", error = "Boat not found", success = None)

if __name__ == "__main__":
	app.run(debug=True)
