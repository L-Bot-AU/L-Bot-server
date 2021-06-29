from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError


class LoginForm(FlaskForm):
    password = PasswordField("Password:",
                             render_kw={"placeholder": "Password"},
                             validators=[DataRequired(message="This field cannot be empty"),
                                         ]
                             )
    submit = SubmitField()
