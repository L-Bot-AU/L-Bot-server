from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class GraphForm(FlaskForm):
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
    data_frequency = SelectField("Time Interval",
                                 validators=[DataRequired()],
                                 choices=[("min1", "1 minute"),
                                          ("min15", "15 minutes"),
                                          ("period", "period"),
                                          ("day", "day"),
                                          ("week", "week"),
                                          ("term", "term")]
                                 )
    submit = SubmitField("Submit")
