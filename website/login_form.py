from flask_wtf import FlaskForm
from wtforms import SelectField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    librarian = SelectField("Library",
                         validators=[DataRequired()],
                         choices=[("Junior", "Junior"),
                                  ("Senior", "Senior")]
                         )
    password = PasswordField("Password",
                             render_kw={"placeholder": "Password"},
                             validators=[DataRequired()]
                             )
    submit = SubmitField("Login")
