from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, validators
from wtforms.fields import EmailField, DateField


class CreateProductForm(Form):
    product_name = StringField('Product Name:', [validators.Length(min=1, max=150),validators.DataRequired()])
    category = SelectField('Category:', [validators.DataRequired()], choices=[('','Select'),('Coasters', 'Coasters'),('Tote bags', 'Tote bags'),('Pouches',
                                                                                            'Pouches')], default='')
    stock = StringField('Stocks:', [validators.Length(min=1, max=150), validators.DataRequired()])
    price = StringField('Price:', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField('Description:', [validators.Optional()])
