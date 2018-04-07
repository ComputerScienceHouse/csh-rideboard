####################################
# File name: models.py             #
# Author: Fred Rybin               #
####################################
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, TextField, FormField, SelectField
from wtforms.validators import DataRequired, Length

class DateForm(FlaskForm):
    month_choice = [('1', ('January')), ('2', ('February')), ('3', ('March')),
                     ('4', ('April')), ('5', ('May')), ('6', ('June')),
                     ('7', ('July')), ('8', ('August')), ('9', ('September')),
                     ('10', ('October')), ('11', ('November')), ('12', ('December'))]
    day_choice = [('1', ('1')), ('2', ('2')), ('3', ('3')), ('4', ('4')),
                  ('5', ('5')), ('6', ('6')), ('7', ('7')),
                  ('8', ('8')), ('9', ('9')), ('10', ('10')), ('11', ('11')),
                  ('12', ('12')), ('13', ('13')), ('14', ('14')),
                  ('15', ('15')), ('16', ('16')), ('17', ('17')), ('18', ('18')),
                  ('19', ('19')), ('20', ('20')), ('21', ('21')),
                  ('22', ('22')), ('23', ('23')), ('24', ('24')), ('25', ('25')),
                  ('26', ('26')), ('27', ('27')), ('28', ('28')),
                  ('29', ('29')), ('30', ('30')), ('31', ('31'))]
    year_num = datetime.utcnow().year
    year_choice = []
    for i in range(year_num, year_num + 5, 1):
        year_tuple = (str(i), str(i))
        year_choice.append(year_tuple)
    month = SelectField(('Month'), choices=month_choice, validators=[DataRequired()],
            default=str(datetime.utcnow().month), render_kw={"class":"form-control"})
    day = SelectField(("Day"), choices=day_choice, validators=[DataRequired()],
        default=str(datetime.utcnow().day), render_kw={"class":"form-control"})
    year = SelectField(("Year"), choices=year_choice, validators=[DataRequired()], render_kw={"class":"form-control"})

class TimeForm(FlaskForm):
    time_choice = [('0', '00')]
    for i in range(1, 23):
        time_tuple = (str(i), str(i))
        time_choice.append(time_tuple)
    hour = SelectField(("Time"), choices=time_choice, validators=[DataRequired()], render_kw={"class":"form-control"})
    minute = SelectField(("Minute"), choices=[('0', '00'), ('15', '15'), ('30', '30'),
    ('45', '45')], validators=[DataRequired()], render_kw={"class":"form-control"})

class RideForm(FlaskForm):
    name = TextField(('What is the name of the event?'), validators=[DataRequired(), Length(min=1, max=140)])
    address = TextField(('Where is the event?'), validators=[DataRequired()])
    start_date = FormField(DateForm)
    start_time = FormField(TimeForm)
    end_date = FormField(DateForm)
    end_time = FormField(TimeForm)
    submit = SubmitField(('Submit'))

class SizeForm(FlaskForm):
    capacity_choice = []
    for i in range(1, 11):
        capacity_tuple = (str(i), str(i))
        capacity_choice.append(capacity_tuple)
    max_capacity = SelectField((""), choices=capacity_choice,
    validators=[DataRequired()], render_kw={"class":"form-control"})

class CarForm(FlaskForm):
    max_capacity = FormField(SizeForm)
    departure_date = FormField(DateForm)
    departure_time = FormField(TimeForm)
    return_date = FormField(DateForm)
    return_time = FormField(TimeForm)
    comments = TextAreaField("Any Comments?")
    submit = SubmitField(('Submit'))
