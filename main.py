
from flask import Flask,render_template,request,url_for,redirect
from model import db
from model import User,Librarian,Books,Fines
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///D:\\Paul\\database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)
@app.route("/")
def index():
    return render_template('index.html')
@app.route("/register")
def register():
    return render_template('register.html')
@app.route("/register_db",methods=["POST"])
def register_db():
    print(request.form)
    user=User(u_username=request.form["username"],u_email=request.form["email"],u_password=request.form["password"])
    print(user)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("index"))
@app.route("/login_db")
def login_db():
    pass
if __name__ == "__main__":
    app.run(debug=True)
    
