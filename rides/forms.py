####################################
# File name: models.py             #
# Author: Fred Rybin & Ayush Goel  #
####################################
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, FormField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Length

class RideForm(FlaskForm):
    name = StringField(('What is the name of the event?'), validators=[DataRequired(), Length(min=1, max=140)])
    address = StringField(('Where is the event?'), validators=[DataRequired()])
    start_date_time = DateTimeField(label="Start", validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    end_date_time = DateTimeField(label="End", validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    submit = SubmitField(('Submit'))

class SizeForm(FlaskForm):
    capacity_choice = []
    for i in range(1, 11):
        capacity_tuple = (str(i), str(i))
        capacity_choice.append(capacity_tuple)
    max_capacity = SelectField((""), choices=capacity_choice,
    validators=[DataRequired()], default=2, render_kw={"class":"form-control"})

class CarForm(FlaskForm):
    max_capacity = FormField(SizeForm)
    departure_date_time = DateTimeField(label="Departure", validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    return_date_time = DateTimeField(label="Return", validators=[DataRequired()], format='%Y-%m-%d %H:%M')
    comments = TextAreaField("Any Comments?")
    submit = SubmitField(('Submit'))
