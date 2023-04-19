from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('El. pašto adresas', validators=[DataRequired(), Email()])
    password = PasswordField('Slaptažodis', validators=[DataRequired()])
    submit = SubmitField('Prisijungti')

class RegisterForm(FlaskForm):
    email = StringField('El. pašto adresas', validators=[DataRequired(), Email()])
    password = PasswordField('Slaptažodis', validators=[DataRequired()])
    password_confirm = PasswordField('Patvirtinti slaptažodį', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registruotis')

class CategoryForm(FlaskForm):
    title = StringField('Kategorijos pavadinimas', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Sukurti')
    
class EditCategoryForm(FlaskForm):
    name = StringField('Kategorijos pavadinimas', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Redaguoti')


class NoteForm(FlaskForm):
    title = StringField('Užrašo pavadinimas', validators=[DataRequired(), Length(max=255)])
    content = TextAreaField('Užrašo tekstas', validators=[DataRequired()])
    category = SelectField('Kategorija', choices=[], coerce=int)
    image = FileField('Nuotrauka (neprivaloma)')
    submit = SubmitField('Sukurti')

class SearchForm(FlaskForm):
    search_query = StringField('Paieškos užklausa', validators=[DataRequired()])
    submit = SubmitField('Ieškoti')

class FilterForm(FlaskForm):
    category = SelectField('Filtruoti pagal kategoriją', choices=[], coerce=int)
    submit = SubmitField('Filtruoti')
