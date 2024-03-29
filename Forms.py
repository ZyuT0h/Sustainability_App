from wtforms import Form, StringField, IntegerField, SelectField, TextAreaField, validators
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
    cust_id = IntegerField('Customer ID: ', validators=[validators.DataRequired()])
    pts_collected = IntegerField('Points Collected: ', validators=[validators.DataRequired()])
    pts_redeemed = IntegerField('Points Redeemed', validators=[validators.DataRequired()])
    pts_left = IntegerField('Points Left', validators=[validators.DataRequired()])
