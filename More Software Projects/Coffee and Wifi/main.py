from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, URLField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
# app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.secret_key = "my-secret-strings"
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField(label='Cafe name', validators=[DataRequired()])
    cafe_location = URLField(label='Cafe Location on Google Map (URL)', validators=[DataRequired(), URL()])
    opening = StringField(label='Opening Time e.g. 8AM', validators=[DataRequired()])
    closing = StringField(label='Closing Time e.g. 5:30PM', validators=[DataRequired()])
    coffee_rating = SelectField(label='Rate Coffee', choices=[('✘', '✘'), ('⭐️', '⭐️'), ('⭐️⭐️', '⭐️⭐️'), ('⭐️⭐️⭐', '⭐️⭐️⭐️'), ('⭐️⭐️⭐️⭐', '⭐️⭐️⭐️⭐️'), ('⭐️⭐️⭐️⭐️⭐️', '⭐️⭐️⭐️⭐️⭐️')], validators=[DataRequired()])
    wifi_rating = SelectField(label='Rate Wifi', choices=[('✘', '✘'), ('⭐️', '⭐️'), ('⭐️⭐️', '⭐️⭐️'), ('⭐️⭐️⭐', '⭐️⭐️⭐️'), ('⭐️⭐️⭐️⭐', '⭐️⭐️⭐️⭐️'), ('⭐️⭐️⭐️⭐️⭐️', '⭐️⭐️⭐️⭐️⭐️')], validators=[DataRequired()])
    power_outlet_rating = SelectField(label='Rate Power Outlet', choices=[('✘', '✘'), ('⭐️', '⭐️'), ('⭐️⭐️', '⭐️⭐️'), ('⭐️⭐️⭐', '⭐️⭐️⭐️'), ('⭐️⭐️⭐️⭐', '⭐️⭐️⭐️⭐️'), ('⭐️⭐️⭐️⭐️⭐️', '⭐️⭐️⭐️⭐️⭐️')], validators=[DataRequired()])
    submit = SubmitField(label='Submit')


# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe_data = {
            'cafe': form.cafe.data,
            'cafe_location': form.cafe_location.data,
            'opening': form.opening.data,
            'closing': form.closing.data,
            'coffee_rating': form.coffee_rating.data,
            'wifi_rating': form.wifi_rating.data,
            'power_outlet_rating': form.power_outlet_rating.data
        }
        # Append data to CSV file
        with open('cafe-data.csv', mode='a', newline='') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=['cafe', 'cafe_location', 'opening', 'closing', 'coffee_rating', 'wifi_rating', 'power_outlet_rating'], delimiter=',')
            csv_writer.writerow(new_cafe_data)
            print(form.data)

        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
