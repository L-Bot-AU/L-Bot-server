from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError


class LoginForm(FlaskForm):
    librarian = RadioField("Librarian",
                         validators=[DataRequired()],
                         choices=[("Junior", "Junior"),
                                  ("Senior", "Senior")]
                         )
    password = PasswordField("Password:",
                             render_kw={"placeholder": "Password"},
                             validators=[DataRequired(message="This field cannot be empty")]
                             )
    submit = SubmitField()
