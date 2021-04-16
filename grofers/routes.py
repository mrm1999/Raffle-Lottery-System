from sqlalchemy.orm import query
from grofers import app, db
from .models import ParticipatingIds, Ticket, User, Lottery
from datetime import date, timedelta
from flask import request, jsonify, render_template
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
  except Exception as err:
    print(err)

  return "Dummy Date"

@app.route("/")
def index():
  today = date.today()
  dateandprizes = []
  for i in range(7):
    entry = Lottery.query.filter_by(Date = today + timedelta(days= i)).first()
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

@app.route("/register-user", methods = ['POST'])
def registerUser():
  try:
    data = request.json
    if data == None:
      return "DataNotRecieved"
    elif (User.query.filter_by(User_Email = data["email"]).first() is None):
      db.session.add(User(User_Email = data["email"] , User_Name = data["username"]))
      db.session.commit()
      return "User Data Successfully Added"
    else:
      return "User Already Registered"

  except Exception as err:
    print(err)

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

@app.route("/get-ticket", methods = ['POST'])
def getTicket():
  try:
    data = request.json

    if data == None:
      return "Data Not Recieved"

    elif (User.query.filter_by(User_Email = data["email"]).first() is None):
      return "E-mail id Not Registered"

    else:
      e_mail = data["email"]
      ticket = Ticket(Email = e_mail)
      db.session.add(ticket)
      db.session.commit()
      return jsonify(Ticket = ticket.id)

  except Exception as err:
    print(err)

@app.route("/lottery-registration", methods = ['POST'])
def LotteryRegistration():
  try:
    data = request.json
    
    if data == None:
      return "DataNotRecieved"
    else:
      if (User.query.filter_by(User_Email = data["email"]).first() is None):
        return "E-mail id Not Registered"
      else:
        ticket = Ticket.query.filter_by(Email = data["email"]).first()
      
        if(ticket is None):
          return "User does not have tickets"

        elif(ParticipatingIds.query.filter_by(Ticket_Id = ticket.id).first() is None):
          db.session.add(ParticipatingIds(Ticket_Id = ticket.id ))
          db.session.commit()
          return "Your Event Registration is Successfull, Best of Lucks for Lottery"
       
        else:
          return "You have already Participated in Event. Max one time is allowed"

  except Exception as err:
    print(err)

@app.route("/winners-list")
def WinnerList():
  today = date.today()
  winners = []
  for i in range(7):
    entry = Lottery.query.filter_by(Date = today - timedelta(days= i+1 )).first()
    winners.append({
      "Date" : f'{entry.Date.day}-{entry.Date.month}-{entry.Date.year}', 
      "Prize" : entry.Prizes,
      "Email Id" : entry.Winner_Email 
    })
  return render_template('winners.html', Winners = winners)

@app.route("/open-lottery")
def OpenLottery():
  participatingcount = db.session.query(ParticipatingIds).count()
  print(participatingcount)
  today = date.today()
  winingLotteryNumber = random.randint(1, participatingcount)
  print(winingLotteryNumber)
  winingField = ParticipatingIds.query.filter_by(id = winingLotteryNumber).first()
  print(type(winingField))
  winingTicketNumber = winingField.Ticket_Id
  winingEmail = Ticket.query.filter_by(id = winingTicketNumber).first().Email  
  print(winingEmail)
  lotteryfield = Lottery.query.filter_by(Date = today).first()
  lotteryfield.Winner_Email = winingEmail
  db.session.commit()
  ## Yaha tak sahi chal rha hai code
  participatingIds = ParticipatingIds.query.all()
  for element in participatingIds :
    db.session.delete(element)
  db.session.commit()
  return f"Winner is {winingEmail} "
