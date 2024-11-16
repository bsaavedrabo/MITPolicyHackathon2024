from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired  

app = Flask(__name__)

# Create Form class 

# note: CSRF token 
app.config['SECRET_KEY']= "" # ADD in gitignore 

class NameForm(FlaskForm):
    name = StringField("State", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/")

def hello():
    return "Hello, World!"
    
# create name page 

@app.route('/intro', methods=['GET', 'POST'])
def intro():
    return render_template(../apps/general-stakeholder/templates/intro.html)