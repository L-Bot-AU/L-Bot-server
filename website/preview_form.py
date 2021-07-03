from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class PreviewForm(FlaskForm):
    start_date = DateField("Start Date",
                           render_kw={"placeholder": "start date"},
                           validators=[DataRequired()],
                           format='%d/%m/%y'
                           )
    end_date = DateField("End Date",
                         render_kw={"placeholder": "end date"},
                         validators=[DataRequired()],
                         format='%d/%m/%y'
                         )
    submit = SubmitField("Generate preview")
