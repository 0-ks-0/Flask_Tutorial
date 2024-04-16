from flask import Flask, render_template, request
from sqlalchemy import Column, Integer, String, Numeric, create_engine, text
from math import ceil

app = Flask(__name__)
conn_str = "mysql://root:1234@localhost/boatdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route('/')
def index():
	return render_template('index.html')

# View boats
@app.route('/boats/')
@app.route('/boats/<page>')
def get_boats(page = 1):
	page = 1 if int(page) < 1 else int(page)  # request params always come as strings. So type conversion is necessary.
	per_page = 10  # records to show per page
	max_page = ceil(conn.execute(text(f"select count(*) / {per_page} from boats")).first()[0])

	boats = conn.execute(text(f"select * from boats limit {per_page} offset {(page - 1) * per_page}")).all()

	return render_template('boats.html', boats = boats, page = page, per_page = per_page, max_page = max_page)

# View data for boat
@app.route('/boats/view/<id>')
def get_boat_data(id = 1):
	data = conn.execute(text(f"select name, type, owner_id, rental_price from boats where id = {id}")).first()

	return render_template('boat_info.html', boat = data)

# Manage page
@app.route('/manage/')
def navigate_to_manage():
	return render_template('manage.html')

# Create boat
@app.route('/manage/create/', methods=['GET'])
def create_get_request():
	return render_template('boats_create.html')

@app.route('/manage/create/', methods=['POST'])
def create_boat():
	# you can access the values with request.from.name
	# this name is the value of the name attribute in HTML form's input element
	# ex: print(request.form['id'])
	try:
		conn.execute(
			text("INSERT INTO boats values (:id, :name, :type, :owner_id, :rental_price)"),
			request.form
		)
		return render_template('boats_create.html', error=None, success="Data inserted successfully!")
	except Exception as e:
		error = e.orig.args[1]
		print(error)
		return render_template('boats_create.html', error=error, success=None)


if __name__ == '__main__':
	app.run(debug=True)
