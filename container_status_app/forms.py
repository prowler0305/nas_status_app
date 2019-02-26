from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, RadioField, BooleanField


class ContainerForm(FlaskForm):
    container_name = RadioField('', choices=[('dev_container_1', 'Dev Container 1'), ('dev_container_2', 'Dev Container 2'), ('dev_container_3', 'Dev Container 3')])
    open_check = BooleanField(default=False)
    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    poc_name = StringField('Name')
    poc_email = StringField('Email')
    submit = SubmitField('Submit')
