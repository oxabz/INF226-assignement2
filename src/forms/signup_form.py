from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators

class SignupForm(FlaskForm):
    
    username = StringField('Username')
    password = PasswordField(
        'Password',
        [
            validators.Length(min=8, message="Password must be at least 8 characters long"),
            validators.InputRequired(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])
    confirm = PasswordField('Repeat password')
    submit = SubmitField('Sign up')