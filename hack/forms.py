from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, IntegerField, EmailField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Log in")

class RegForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    image = FileField('Upload a profile picture', validators=[FileAllowed('png', 'jpg')])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Register")

class SearchForm(FlaskForm):
    query = StringField('search', validators=[DataRequired()])
