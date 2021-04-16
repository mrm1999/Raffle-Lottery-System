from enum import unique
from grofers import db

#For User Registeration
class User(db.Model):
  User_Name = db.Column(db.String())
  User_Email = db.Column(db.String(), unique = True, primary_key = True)

  def __repr__(self):
    return '<UserName %r>' % self.UserName

#This Table will contain all the data regarding ticket id and  whom that id is alloted    
class Ticket(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  Email = db.Column(db.String())

  def __repr__(self):
    return '<TicketNumbet %r>' % self.Ticket

#This Table will use to store the Details of that events
class Lottery(db.Model):
  Date = db.Column(db.Date, unique = True, primary_key = True )
  Prizes = db.Column(db.String())
  Winner_Email = db.Column(db.String(), default = "")

  def __repr__(self):
    return f'{self.Date} -> {self.Prizes}'

#This table contains the detail that which ticket are going to participate in that particular event. All enteries will be removed after that lottery allotment
class ParticipatingIds(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  Ticket_Id = db.Column(db.Integer, db.ForeignKey(Ticket.id))

  ticket = db.relationship('Ticket', cascade = 'all , delete')

  def __repr__(self):
    return self.id
  
