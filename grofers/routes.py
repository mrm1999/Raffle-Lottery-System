from grofers import app, db
from .models import ParticipatingIds, Ticket, User, Lottery
from datetime import date, datetime, timedelta,
from flask import request, render_template
import random

#This API will be used to insert dummy data in Database. While in Production Mode, We have to remove this API
@app.route("/dummy")
def dummy():

  try:    
    PrizeList = ["AC", "Washing Machine", "Television", "Refrigerator", "Mobile Phone", "Speaker", "Laptop", "Holiday Trip", "Earphones", "Desktop", "Car", "Motor-Bike", "Watch ", "KeyBoard", "Tablet", "Iphone", "Bicycle", "T-shirt"]
    EmailList = ["mohitrajmunot1999@gmail.com","mohitrajmunot113@gmail.com", "mems180005017@gmail.com", "ayush@gmail.com" , "harsh@gmail.com", "vineet@gmail.com", "lakshya@gmail.com", "mukul@gmail.com", "aditya@gmail.com" ]
    UserNameList = [ "Mohit Raj Munot","Mohit Raj ","Mohit ", "ayush", "harsh", "vineet", "lakshya", "mukul", "aditya" ]
    
    day = date.today().day 
    
    for i in range(9):
      db.session.add(User(User_Name = UserNameList[i], User_Email = EmailList[i]))
    
    for i in range(18):
      if (i+8 < day ) :
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
    return "Error"

#This API will be used devlopment mode
@app.route("/reset")
def resetData():
  db.drop_all()
  db.create_all()
  return "Data Reseted Successfully"

#This will be front page of our services. It will return a page containing the upcoming prizes(7 days).
#Also It will render a page which contain currrent time and A Api will automatically tigger at 8PM for each day using javascript
@app.route("/")
def index():
  today = date.today()
  hr = datetime.now().hour
  print(hr)
  dateandprizes = []
  for i in range(7):
    if hr < 8:
      #if time is less than 8PM. It will show upcoming prizes(include that day also)
      entry = Lottery.query.filter_by(Date = today + timedelta(days= i)).first()
    else:
      entry = Lottery.query.filter_by(Date = today + timedelta(days= i+1)).first()
      #if time is greater than 8PM. It will show upcoming prizes(will not include that day)
    dateandprizes.append({
      "Date" : f'{entry.Date.day}-{entry.Date.month}-{entry.Date.year}', 
      "Prize" : entry.Prizes
    })
  return render_template('home.html', dateandprizes = dateandprizes)

#For the first time User have to register himself on Website. It will be only a one time process.
@app.route("/register-user", methods = ['GET','POST'])
def registerUser():
  if(request.method == 'GET'):
    #It is for opening form page
    return render_template('user_registration.html')
  else:
    #This is for registering the user
    data = request.form
    #Will check the data 
    if data == None:
      return render_template('user_registration.html', message = "Data Not Recieved")
    #The below query will check that user is already registered or not. If user is not registered, It will add it to database  
    #Otherwise It will a display a message that "User Already Registered"
    elif (User.query.filter_by(User_Email = data["email"]).first() is None):
      db.session.add(User(User_Email = data["email"] , User_Name = data["username"]))
      db.session.commit()
      return render_template('user_registration.html', message = "User Registered Successfully")  
    else:
      return render_template('user_registration.html', message = "User Already Registered")

#We are assuming that a User can purchase any number of Ticket and also for getting a Ticket he has to be registerded
#We are giving a unique code to user each time.
@app.route("/get-ticket", methods = ['GET', 'POST'])
def getTicket():
  if(request.method == 'GET'):
    #It is for opening buy_ticket form page
    return render_template('buy_ticket.html')

  else:
    #This is for getting the ticket
    data = request.form
    
    if data == None:
      #Will check the data
      return render_template('buy_ticket.html' , message = "Data Not Recieved")
    
    elif (User.query.filter_by(User_Email = data["email"]).first() is None):
      #Will check if user is registered or not
      return render_template('buy_ticket.html' , message = "E-mail Id is not Registered")
    
    else:
      #will take his email id and generate a ticket number corresponding to it
      e_mail = data["email"]
      ticket = Ticket(Email = e_mail)
      db.session.add(ticket)
      db.session.commit()
      #This will display Ticket no on Website that you have got
      return render_template('buy_ticket.html' , message = f'Your Ticket Number is {ticket.id}')

#This API is for participating in event. We have assumed that User can only Participate in the first Upcoming Event.
#He can only register for event before 24hrs 
@app.route("/participate-in-lottery", methods = ['GET','POST'])
def LotteryRegistration():
  if(request.method == 'GET'):
    return render_template("participate_lottery.html")
  else:
    data = request.form
    
    if data == None:
      return render_template("participate_lottery.html", message = "Data Not Recieved")
    else:
      if (User.query.filter_by(User_Email = data["email"]).first() is None):
        #First We will check that User is Registered or not
        return render_template("participate_lottery.html", message = "E-mail Id is not Registered")
      else:
        ticket = Ticket.query.filter_by(Email = data["email"]).first()
        #Then will check if the user has tickets or not.
        if(ticket is None):
          return render_template("participate_lottery.html", message = "Users Does not have tickets. Please buy them")

        #If a user have multiple tickets then his first ticket(t oneOldes) will be used to particpate in event.
        #Also from below query We are checking that User has participated in that event or not
        elif(ParticipatingIds.query.filter_by(Ticket_Id = ticket.id).first() is None):
          #Will add that ticket in to that partipating ticket datas for that particular event
          db.session.add(ParticipatingIds(Ticket_Id = ticket.id ))
          db.session.commit()
          return render_template("participate_lottery.html", message = "You have successfully registered for the Lottery Event. Best of luck for that!!")
       
        else:
          return render_template("participate_lottery.html", message = "You have already participated for Lottery Event. Maximum One time is Allowed")

#This Api is used for getting past 7 days Winners list
@app.route("/get-winners")
def WinnerList():
  today = date.today() 
  hr = datetime.now().hour
  winners = []
  for i in range(7):
    if hr < 2 :
      #if time is less than 8PM. It will show winners(not include that day )
      entry = Lottery.query.filter_by(Date = today - timedelta(days= i+1 )).first()
    else:
      #if time is greater than 8PM. It will show winners(included that day )
      entry = Lottery.query.filter_by(Date = today - timedelta(days= i)).first()
    winners.append({
      "Date" : f'{entry.Date.day}-{entry.Date.month}-{entry.Date.year}', 
      "Prize" : entry.Prizes,
      "Email Id" : entry.Winner_Email 
    })
  #Will send the list of winners to the page
  return render_template('winners.html', Winners = winners)

#This API is used to open the lottery and decide the winner for that.
#User will not have access to this api. This Api is triggering automatically by javascript at 8PM every day. 
#After we will get the winner, the participating datas will be deleted for that day.

@app.route("/open-lucky-draw")
def OpenLottery():
  participatingcount = db.session.query(ParticipatingIds).count()  #Will count the no of participation for that day
  today = date.today()                                                
  winingLotteryNumber = random.randint(1, participatingcount)      #for lottery allotment we will be selecting a random value from 1 to count
  winingField = ParticipatingIds.query.filter_by(id = winingLotteryNumber).first()
  winingTicketNumber = winingField.Ticket_Id                        #will get corresponding ticket no to that winning lottery no.
  winingEmail = Ticket.query.filter_by(id = winingTicketNumber).first().Email  #will get corresponding e_mail to that ticket number
  lotteryfield = Lottery.query.filter_by(Date = today).first()
  lotteryfield.Winner_Email = winingEmail                            #will update the wining email id in the data base
  db.session.commit()
  participatingIds = ParticipatingIds.query.all()
  for element in participatingIds :           #will delete all the participating ids for that particukar event.
    db.session.delete(element)                #Also as ticket id is foreign key for participating fields by cascading, the corresponding ticket will also dete in ticket table                        
  db.session.commit()
  return f"Winner is {winingEmail} "          #Will Send the winner


