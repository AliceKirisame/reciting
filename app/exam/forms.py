from flask.ext.wtf import Form

from wtforms import StringField, SubmitField
from wtforms.validators import Required, Regexp


class WordForm(Form):
    group = StringField('group', validators=[Required(), Regexp('^[0-9]*$')])
    word = StringField('word', validators=[Required(), Regexp('^[A-Za-z\s\.]*$')])
    meaning = StringField('meaning', validators=[Required()])

    submit = SubmitField('submit')


class RespForm(Form):
    word1 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word2 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word3 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word4 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word5 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word6 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word7 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word8 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word9 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    word10 = StringField('', validators=[Required(), Regexp('^[A-Za-z]*$')])
    submit = SubmitField('submit')

    def __init__(self, nameli):
        word1 = StringField(str(nameli[0]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word2 = StringField(str(nameli[1]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word3 = StringField(str(nameli[2]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word4 = StringField(str(nameli[3]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word5 = StringField(str(nameli[4]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word6 = StringField(str(nameli[5]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word7 = StringField(str(nameli[6]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word8 = StringField(str(nameli[7]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word9 = StringField(str(nameli[8]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        word10 = StringField(str(nameli[9]), validators=[Required(), Regexp('^[A-Za-z]*$')])
        submit = SubmitField('submit')
