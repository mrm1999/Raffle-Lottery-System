from enum import unique
from grofers import db


class User(db.Model):
  User_Name = db.Column(db.String())
  User_Email = db.Column(db.String(), unique = True, primary_key = True)
# default =  db.Sequence('sequence_id', start= 10 , increment = 1)
  def __repr__(self):
    return '<UserName %r>' % self.UserName

class Lottery(db.Model):
  Date = db.Column(db.Date, unique = True, primary_key = True )
  Prizes = db.Column(db.String())
  Winner_Email = db.Column(db.String(), default = "")

  def __repr__(self):
    return f'{self.Date} -> {self.Prizes}'

class Ticket(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  Email = db.Column(db.String())

  def __repr__(self):
    return '<TicketNumbet %r>' % self.Ticket

class ParticipatingIds(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  Ticket_Id = db.Column(db.Integer, db.ForeignKey(Ticket.id))

  ticket = db.relationship('Ticket', cascade = 'all , delete')

  def __repr__(self):
    return self.id
  
