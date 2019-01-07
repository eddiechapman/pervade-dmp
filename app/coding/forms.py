from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField, TextAreaField

class CodingForm(FlaskForm):
    """The form for recording coding information about an award."""
    pervasive_data = BooleanField('Pervasive Data')
    review = BooleanField('Review')
    comments = TextAreaField('Comments')
    submit = SubmitField('Submit')

    def validate(self):
        """This should have something more useful but it doesn't work otherwise."""
        return True