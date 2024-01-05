class CreateProductForm(Form):
    product_name = StringField('Product Name:', [validators.Length(min=1, max=150),validators.DataRequired()])
    category = SelectField('Category:', [validators.DataRequired()], choices=[('','Select'),('Coasters', 'Coasters'),
                                                                             ('Tote bags', 'Tote bags'),('Pouches', 'Pouches')],default='')
    stock = StringField('Stock:', [validators.Length(min=1, max=150), validators.DataRequired()])
                                                                             ('Tote bags', 'Tote bags'),('Pouches',
                                                                                            'Pouches')], default='')
    stock = StringField('Stockssssss:', [validators.Length(min=1, max=150), validators.DataRequired()])
    price = StringField('Price:', [validators.Length(min=1, max=150), validators.DataRequired()])
    description = TextAreaField('Description:',[validators.Optional()])
    description = TextAreaField('Description:', [validators.Optional()])