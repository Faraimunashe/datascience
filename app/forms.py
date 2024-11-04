from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, IntegerField, SelectField, DateField, DateTimeField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Regexp, Optional, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import datetime, date, time, timedelta

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "example@company.com", "autofocus": True, "class": "form-control"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "Password", "class": "form-control"})
    submit = SubmitField('Login Account')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
