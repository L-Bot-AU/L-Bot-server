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
<<<<<<< HEAD:website/download_form.py
<<<<<<< HEAD:website/download_form.py
    data_frequency = SelectField("Time Interval:",
=======
    data_frequency = SelectField("Show Average Every:",
>>>>>>> parent of 0be170e (Added download and preview interfaces):website/graph_form.py
                                 validators=[DataRequired()],
                                 choices=[("min1", "1 minute"),
                                          ("min15", "15 minutes"),
                                          ("period", "period"),
                                          ("day", "day"),
                                          ("week", "week"),
                                          ("term", "term")]
                                 )
<<<<<<< HEAD:website/download_form.py
    submit = SubmitField("Download")
=======
    # data_frequency = SelectField("Data Frequency",
    #                              validators=[DataRequired()],
    #                              choices=[("")])
=======
>>>>>>> parent of 0be170e (Added download and preview interfaces):website/graph_form.py
    periods = BooleanField("Periods")
    morning = BooleanField("Morning")
    lunch = BooleanField("Lunch")
    recess = BooleanField("Recess")
    submit = SubmitField("Submit")
<<<<<<< HEAD:website/download_form.py
>>>>>>> parent of 8cf8371 (minor changes):website/graph_form.py
=======
>>>>>>> parent of 0be170e (Added download and preview interfaces):website/graph_form.py
