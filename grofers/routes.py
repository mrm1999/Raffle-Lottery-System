from flask.helpers import flash, url_for
from sqlalchemy.orm import query
from grofers import app, db
from .models import ParticipatingIds, Ticket, User, Lottery
from datetime import date, datetime, timedelta, time
from flask import request, jsonify, render_template, redirect
import json
import random


@app.route("/dummy")
def dummy():

  try:    
    PrizeList = ["AC", "Washing Machine", "Television", "Refrigerator", "Mobile Phone", "Speaker", "Laptop", "Holiday Trip", "Earphones", "Desktop", "Car", "Motor-Bike", "Watch ", "KeyBoard", "Tablet", "Iphone", "Bicycle", "T-shirt"]
    EmailList = ["mohitrajmunot1999@gmail.com","mohitrajmunot113@gmail.com", "mems180005017@gmail.com", "ayush@gmail.com" , "harsh@gmail.com", "vineet@gmail.com", "lakshya@gmail.com", "mukul@gmail.com", "aditya@gmail.com" ]
    UserNameList = [ "Mohit Raj Munot","Mohit Raj ","Mohit ", "ayush", "harsh", "vineet", "lakshya", "mukul", "aditya" ]
    
    for i in range(9):
      db.session.add(User(User_Name = UserNameList[i], User_Email = EmailList[i]))
    
    for i in range(18):
      if i+8 <= 15 :
        db.session.add(Lottery(Date = date(2021, 4 , 8+i), Prizes = PrizeList[i], Winner_Email = EmailList[i]))
      else:
        db.session.add(Lottery(Date = date(2021, 4 , 8+i), Prizes = PrizeList[i]))

    for i in range(7):
      db.session.add(Ticket(Email = EmailList[i]))
    for i in range(7):
      db.session.add(Ticket(Email = EmailList[i]))

    for i in range(6):
      ticket = Ticket.query.filter_by(Email = EmailList[i]).first()
      db.session.add(ParticipatingIds(Ticket_Id = ticket.id))
      
    db.session.commit()
    return "Dummy Date"
  except Exception as err:
    print(err)
    return err
 
@app.route("/")
def index():
  today = date.today()
  hr = datetime.now().hour
  dateandprizes = []
  for i in range(7):
    if hr < 20:
      entry = Lottery.query.filter_by(Date = today + timedelta(days= i)).first()
    else:
      entry = Lottery.query.filter_by(Date = today + timedelta(days= i+1)).first()
    dateandprizes.append({
      "Date" : f'{entry.Date.day}-{entry.Date.month}-{entry.Date.year}', 
      "Prize" : entry.Prizes
    })

  return render_template('home.html', dateandprizes = dateandprizes)

@app.route("/reset")
def resetData():
  db.drop_all()
  db.create_all()
  return "Data Reseted Successfully"

@app.route("/register-user", methods = ['GET','POST'])
def registerUser():
  if(request.method == 'GET'):
    return render_template('user_registration.html')
  else:
    data = request.form
    if data == None:
      return render_template('user_registration.html', message = "Data Not Recieved")
    elif (User.query.filter_by(User_Email = data["email"]).first() is None):
      db.session.add(User(User_Email = data["email"] , User_Name = data["username"]))
      db.session.commit()
      return render_template('user_registration.html', message = "User Registered Successfully")  
    else:
      return render_template('user_registration.html', message = "User Already Registered")

@app.route("/show-prizes")
def showPrizes():
  today = date.today()
  dateandprizes = []
  for i in range(7):
    entry = Lottery.query.filter_by(Date = today + timedelta(days= i)).first()
    dateandprizes.append({
      "Date" : f'{entry.Date.day}-{entry.Date.month}-{entry.Date.year}', 
      "Prize" : entry.Prizes
    })
  return json.dumps(dateandprizes)

@app.route("/get-ticket", methods = ['GET', 'POST'])
def getTicket():
  if(request.method == 'GET'):
    return render_template('buy_ticket.html')

  else:
    data = request.form
    
    if data == None:
      return render_template('buy_ticket.html' , message = "Data Not Recieved")
    
    elif (User.query.filter_by(User_Email = data["email"]).first() is None):
      return render_template('buy_ticket.html' , message = "E-mail Id is not Registered")
    
    else:
      e_mail = data["email"]
      ticket = Ticket(Email = e_mail)
      db.session.add(ticket)
      db.session.commit()
      return render_template('buy_ticket.html' , message = f'Your Ticket Number is {ticket.id}')

@app.route("/lottery-registration", methods = ['GET','POST'])
def LotteryRegistration():
  if(request.method == 'GET'):
    return render_template("participate_lottery.html")
  else:
    data = request.form
    
    if data == None:
      return render_template("participate_lottery.html", message = "Data Not Recieved")
    else:
      if (User.query.filter_by(User_Email = data["email"]).first() is None):
        return render_template("participate_lottery.html", message = "E-mail Id is not Registered")
      else:
        ticket = Ticket.query.filter_by(Email = data["email"]).first()
      
        if(ticket is None):
          return render_template("participate_lottery.html", message = "Users Does not have tickets. Please buy them")

        elif(ParticipatingIds.query.filter_by(Ticket_Id = ticket.id).first() is None):
          db.session.add(ParticipatingIds(Ticket_Id = ticket.id ))
          db.session.commit()
          return render_template("participate_lottery.html", message = "You have successfully registered for the Lottery Event. Best of luck for that!!")
       
        else:
          return render_template("participate_lottery.html", message = "You have already participated for Lottery Event. Maximum One time is Allowed")

@app.route("/winners-list")
def WinnerList():
  today = date.today()
  hr = datetime.now().hour
  winners = []
  for i in range(7):
    if hr < 20:
      entry = Lottery.query.filter_by(Date = today - timedelta(days= i+1 )).first()
    else:
      entry = Lottery.query.filter_by(Date = today - timedelta(days= i)).first()
    winners.append({
      "Date" : f'{entry.Date.day}-{entry.Date.month}-{entry.Date.year}', 
      "Prize" : entry.Prizes,
      "Email Id" : entry.Winner_Email 
    })
  return render_template('winners.html', Winners = winners)

@app.route("/open-lottery")
def OpenLottery():
  participatingcount = db.session.query(ParticipatingIds).count()
  today = date.today()
  winingLotteryNumber = random.randint(1, participatingcount)
  winingField = ParticipatingIds.query.filter_by(id = winingLotteryNumber).first()
  winingTicketNumber = winingField.Ticket_Id
  winingEmail = Ticket.query.filter_by(id = winingTicketNumber).first().Email  
  lotteryfield = Lottery.query.filter_by(Date = today).first()
  lotteryfield.Winner_Email = winingEmail
  db.session.commit()
  participatingIds = ParticipatingIds.query.all()
  for element in participatingIds :
    db.session.delete(element)
  db.session.commit()
  return f"Winner is {winingEmail} "


