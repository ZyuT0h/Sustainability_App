from wtforms import Form, StringField, SelectField, TextAreaField, validators
from wtforms.fields import EmailField, DateField


class CreateProductForm(Form):
    product_name = StringField('Product Name:', [validators.Length(min=1, max=150), validators.DataRequired()])
    category = SelectField('Category:', [validators.DataRequired()],
                           choices=[('', 'Select'), ('Coasters', 'Coasters'), ('Tote bags', 'Tote bags'), ('Pouches',
                                                                                                           'Pouches')],
                           default='')
    stock = StringField('Stocks:', [validators.Length(min=1, max=150), validators.DataRequired()])
    price = StringField('Price:', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField('Description:', [validators.Optional()])


class CreatePointForm(Form):
    cust_id = StringField('Customer ID: ', validators=[validators.DataRequired()])
    pts_collected = StringField('Points Collected: ', validators=[validators.DataRequired()])
    pts_redeemed = StringField('Points Redeemed', validators=[validators.DataRequired()])
    pts_left = StringField('Points Left', validators=[validators.DataRequired()])
