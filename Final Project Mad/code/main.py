"""Since there were a lot of issues when making the program come from different files, I have saved all of them in one file. However for better clarity i have divided them into the App and Database to better seperate the two"""

#Application Imports and initialisation
from datetime import datetime
from flask import Flask, render_template, request
from werkzeug.utils import redirect
app = Flask(__name__)

#Database Link and Initialisation
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
db=SQLAlchemy(app)

#Models for the Project

#User table: Stores username and password for verification
class User(db.Model):
    __tablename__='User'
    userid=db.Column(db.Integer,autoincrement=True,primary_key=True)
    username=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)

#Master HTML database for extra feature: importing
class HTML(db.Model):
    __tablename__='HTML'
    s_no=db.Column(db.Integer,autoincrement=True,primary_key=True)
    name =db.Column(db.String)
    description=db.Column(db.String)

#Decks table : contains info on Decks , connects to User by foreign key username
class Decks(db.Model):
    __tablename__='Decks'
    deck_id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    username=db.Column(db.String,db.ForeignKey('User.username'),nullable=False)
    deck_name=db.Column(db.String,nullable=False)
    cardlist=db.Column(db.String,nullable=False)
    time=db.Column(db.String)
    scorelist=db.Column(db.String)

#Cards table: contains info on Cards , connects to User by foreign key username
class Cards(db.Model):
    __tablename__='Cards'
    c_no=db.Column(db.Integer,primary_key=True,autoincrement=True)
    c_name=db.Column(db.String,nullable=False)
    c_description=db.Column(db.String,unique=True,nullable=False)
    username=db.Column(db.String,db.ForeignKey('User.username'),nullable=False)

#Function to convert a list of strings into a string to input into the database
def convert_stringlist(x):
    xstring=""
    for i in x:
        if xstring=="":
            xstring=xstring+i
        else:
            xstring=xstring+","+i
    return xstring

#function to convert a list of strings to a list of float values for calculations
def convert_floatlist(x):
    x1=[]
    for i in x:
        b=float(i)
        x1.append(b)
    return(x1)

#main route. Checks if username password is valid and redirects to dashboard. Else returns a custom error HTML page.
@app.route('/',methods=['GET','POST'])
def loginpage():
    if request.method=='GET':
        return render_template('loginpage.html')
    elif request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        validlogin=db.session.query(User).filter(User.username==username,User.password==password).first()
        if validlogin:
                return redirect('/{}/dashboard'.format(username))
        return render_template('invalidpassword.html')

#sign up page. Checks if username is duplicate and prints custom error HTML page if so, else redirects to login page and saves to User database.
@app.route('/signup',methods=['GET','POST'])
def signinpage():
    if request.method=='GET':
        return render_template('signuppage.html')
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        userexists=db.session.query(User).filter(User.username==username).first()
        if userexists:
            return render_template('invalidusername.html')
        user=User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')

#dashboard page. Displays List of Decks with related info regarding score and time. Allows options to view cards,create a deck or log out. If there are no Decks a custom HTML page with the message and options to create a deck are shown.
@app.route('/<string:username>/dashboard',methods=['GET','POST'])
def dashboard(username):
    user=db.session.query(User).filter(User.username==username).first()
    deck_exists=db.session.query(Decks).filter(Decks.username==username).all()
    if deck_exists==[]:
        return render_template('nodecksyet.html',user=user)
    else:
        score_list=[]
        avglist=[]
        for deck in deck_exists:
            if deck.scorelist!=None :
                temp_score_list=deck.scorelist.split(',')
                temp_score_list=convert_floatlist(temp_score_list)
                avg=(round(sum(temp_score_list)/len(temp_score_list),2)*100)
                score_list.append(temp_score_list[-1]*100)
                avglist.append(avg)
            else:
                score_list.append('Not attempted')
                avglist.append('Not attempted')
        return render_template('dashboard.html',user=user,data=deck_exists,avglist=avglist,score_list=score_list)
   
#page to view the cards. Each card can be updated or deleted. There are also options to create a card, import cards from the master database or go back. If there are no cards, a custom HTML page is displayed.
@app.route('/<string:username>/cards')
def viewcards(username):
    user=db.session.query(User).filter(User.username==username).first()
    cards=db.session.query(Cards).filter(Cards.username==username).all()   
    if cards:
        return render_template('cards.html',user=user,cards=cards)
    else:
        return render_template('no_cards_yet.html',user=user)

# Page to create a card. All form details are required in HTML. If Card Exists, a custom Error message is displayed.
@app.route('/<string:username>/createcard',methods=['GET','POST'])
def createcard(username):
    user=db.session.query(User).filter(User.username==username).first()
    if request.method=='GET':
        return render_template('createcard.html',user=user)
    if request.method=='POST':
        card_name=request.form['card_name']
        card_exists=db.session.query(Cards).filter(Cards.c_name==card_name,Cards.username==username).all()
        print(card_exists)
        if card_exists:
            return render_template('card_exists.html',user=user)
        else:
            card_description=request.form['card_description']
            newcard=Cards(c_name=card_name,c_description=card_description,username=username)
            db.session.add(newcard)
            db.session.commit()
            return redirect('/{}/cards'.format(username))

#Get request that deletes the card and redirects to the view cards page.
@app.route('/<string:username>/deletecard/<int:c_no>')
def deletecard(username,c_no):
        card=db.session.query(Cards).filter(Cards.c_no==c_no).first()
        db.session.delete(card)
        db.session.commit()
        return redirect('/{}/cards'.format(username))

#Page to update a card. If the card name already exists, a custom Error Message is displayed. All form fields are required.
@app.route('/<string:username>/updatecard/<int:c_no>',methods=['GET','POST'])
def updatecard(username,c_no):
    user=db.session.query(User).filter(User.username==username).first()
    card=db.session.query(Cards).filter(Cards.c_no==c_no).first()
    if request.method=='GET':
        return render_template('updatecard.html',user=user,card=card)
    if request.method=='POST':
        card_name=request.form['card_name']
        card_exists=db.session.query(Cards).filter(Cards.c_name==card_name,Cards.username==username).first()
        if card_exists:
            return(render_template('card_exists.html',user=user))
        card_description=request.form['card_description']
        if (card_name !=None and card_name != ""):
            db.session.query(Cards).filter(Cards.c_no==c_no).update({Cards.c_name:card_name})
        if (card_description !=None and card_description !=""):
            db.session.query(Cards).filter(Cards.c_no==c_no).update({Cards.c_description:card_description})
        db.session.commit()
        return redirect('/{}/cards'.format(username))

#Page to import cards from a table consisting of all 131 HTML Attributes. Implemented as a unique feature in my application.
@app.route('/<string:username>/importcards',methods=['GET','POST'])
def importcards(username):
    user=db.session.query(User).filter(User.username==username).first()
    cards=db.session.query(HTML).all()
    if request.method=='GET':
        return render_template('importcards.html',user=user,cards=cards)
    if request.method=='POST':
        cardlist=request.form.getlist('cardlist')
        cardlist=convert_floatlist(cardlist)
        for i in range(len(cardlist)):
            imported_card=db.session.query(HTML).filter(HTML.s_no==cardlist[i]).first()
            exists=db.session.query(Cards).filter(Cards.username==username,Cards.c_name==imported_card.name).first()
            if not exists:
                card_to_insert=Cards(c_name=imported_card.name,c_description=imported_card.description,username=username)
                db.session.add(card_to_insert)
        db.session.commit()
        return redirect('/{}/cards'.format(username))


#Route to create a deck. if there are no cards, a HTML error message is displayed. If the deckname already exists, a custom HTML error is displayed.
@app.route('/<string:username>/createdeck',methods=['GET','POST'])
def createdeck(username):
    user=db.session.query(User).filter(User.username==username).first()
    if request.method=='GET':
       cards=db.session.query(Cards).filter(Cards.username==username).all()
       if cards:
        return render_template('createdeck.html',user=user,cards=cards)
       else:
        return render_template('no_cards_yet.html',user=user)
    if request.method=='POST':
        deckname=request.form['deckname']
        deck_exists=db.session.query(Decks).filter(Decks.username==username,Decks.deck_name==deckname).first()
        if deck_exists:
            return render_template('deck_exists.html',user=user)
        else:
            cardlist=request.form.getlist('cardlist')
            cardlist=convert_stringlist(cardlist)
            newdeck=Decks(username=username,deck_name=deckname,cardlist=cardlist)
            db.session.add(newdeck)
            db.session.commit()
            return redirect('/{}/dashboard'.format(username))

#Get request that deletes the deck and redirects to the dashboard.
@app.route('/<string:username>/deletedeck/<string:deck_name>')
def deletedeck(username,deck_name):
        deck=db.session.query(Decks).filter(Decks.deck_name==deck_name).first()
        db.session.delete(deck)
        db.session.commit()
        return redirect('/{}/dashboard'.format(username))

#route that updates the card of a deck.
@app.route('/<string:username>/updatedeck/<string:deck_name>',methods=['GET','POST'])
def updatedeck(username,deck_name):
    user=db.session.query(User).filter(User.username==username).first()
    cards=db.session.query(Cards).filter(Cards.username==username).all()
    if request.method=='GET':
        return render_template('updatedeck.html',user=user,cards=cards,deck_name=deck_name)
    if request.method=='POST':
        cardlist=request.form.getlist('cardlist')
        if cardlist !=[]:
            cardlist=convert_stringlist(cardlist)
            db.session.query(Decks).filter(Decks.deck_name==deck_name).update({Decks.cardlist:cardlist})
            db.session.commit()
        return redirect('/{}/dashboard'.format(username))

#route to see the cards of the deck, to learn the cards before the review process. If there were no cards added initially, and is still the case, a custom error HTML message is shown.
@app.route('/<string:username>/viewdeck/<string:deck_name>',methods=['GET','POST'])
def viewdeck(username,deck_name):
    if request.method=='GET':
        user=db.session.query(User).filter(User.username==username).first()
        deck=db.session.query(Decks).filter(Decks.deck_name==deck_name).first()
        print (deck.cardlist)
        if deck.cardlist !="":
            cards=deck.cardlist.split(',')
            cards=convert_floatlist(cards)
            finalcards=[]
            for i in range(len(cards)):
                card=db.session.query(Cards).filter(Cards.c_no==cards[i]).first()
                finalcards.append(card)
            return render_template('viewdeck.html',deck=deck,cards=finalcards,user=user)
        else:
            return render_template('no_cards_yet.html',user=user)


#route to review the cards on their own, and checking whether they are easy, medium or hard. Notes the time and the score when sent as a POST request and updates into the database
@app.route('/<string:username>/viewdeck/<string:deck_name>/review',methods=['GET','POST'])
def reviewdeck(username,deck_name):
    if request.method=='GET':
        QAdict={}
        user=db.session.query(User).filter(User.username==username).first()
        deck=db.session.query(Decks).filter(Decks.deck_name==deck_name,Decks.username==username).first()
        listofcards=deck.cardlist.split(',')
        for i in range(len(listofcards)):
            card=db.session.query(Cards).filter(Cards.username==username,Cards.c_no==listofcards[i]).first()
            if card:
                QAdict[card.c_name]=card.c_description
            else:
                return render_template('no_cards_yet.html',user=user)
        return render_template('reviewdeck.html',cards=QAdict,deck=deck,user=user)
    if request.method=='POST':
        a=request.form.getlist('answer')
        b=request.form.getlist('question')
        c=datetime.now()
        score=(round(a.count('1')/len(a),2))
        deck1=db.session.query(Decks).filter(Decks.deck_name==deck_name).first()
        if deck1.scorelist==None:
            scorelist=[str(score)]
            scorelist=convert_stringlist(scorelist)
        else:
            scorelist=deck1.scorelist.split(',')
            scorelist.append(str(score))
            scorelist=convert_stringlist(scorelist)
        db.session.query(Decks).filter(Decks.deck_name==deck_name).update({Decks.time:c,Decks.scorelist:scorelist})
        db.session.commit()
        return redirect('/{}/dashboard'.format(username))


#runs the app on host='0.0.0.0'

if __name__=='__main__':
    app.run(host='0.0.0.0')