from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class SQ(db.Model):
    __tablename__ = "science_questions"
    __searchable__ = ['QUESTION', 'A','B','C','D'];

    id = db.Column(db.Integer,primary_key=1);
    QUESTION = db.Column(db.Text)
    A = db.Column(db.Text)
    B = db.Column(db.Text)
    C = db.Column(db.Text)
    D = db.Column(db.Text)
    ANSWERTYPE = db.Column(db.Integer)
    ANSWER = db.Column(db.Text)
    TYPE = db.Column(db.Integer) # 1 for single , 2 for multiple
    CHAPTER = db.Column(db.Integer)
    SUBJECT = db.Column(db.Integer)
    IMAGENUM = db.Column(db.Text)

class AQ(db.Model):
    __tablename__ = "art_questions"
    __searchable__ = ['QUESTION', 'A','B','C','D'];
    id = db.Column(db.Integer,primary_key=1);
    QUESTION = db.Column(db.Text)
    A = db.Column(db.Text)
    B = db.Column(db.Text)
    C = db.Column(db.Text)
    D = db.Column(db.Text)
    ANSWERTYPE = db.Column(db.Integer)
    ANSWER = db.Column(db.Text)
    TYPE = db.Column(db.Integer)
    CHAPTER = db.Column(db.Integer)
    SUBJECT = db.Column(db.Integer)
    IMAGENUM = db.Column(db.Text)

sci_w = db.Table(
    "sci_w",
    db.Column('q_id',db.Integer,db.ForeignKey('science_questions.id')),
    db.Column('u_id',db.Integer,db.ForeignKey('user.id')),
    # db.UniqueConstraint("q_id","u_id",name="sciw")
);

art_w = db.Table(
    "art_w",
    db.Column('q_id',db.Integer,db.ForeignKey('art_questions.id')),
    db.Column('u_id',db.Integer,db.ForeignKey('user.id')),
    # db.UniqueConstraint("q_id","u_id",name="artw")
);

sci_h = db.Table(
    "sci_h",
    db.Column('q_id',db.Integer,db.ForeignKey('science_questions.id')),
    db.Column('u_id',db.Integer,db.ForeignKey('user.id')),
    # db.UniqueConstraint("q_id","u_id",name="scih")
);

art_h = db.Table(
    "art_h",
    db.Column('q_id',db.Integer,db.ForeignKey('art_questions.id')),
    db.Column('u_id',db.Integer,db.ForeignKey('user.id')),
    # db.UniqueConstraint("q_id","u_id",name="arth")
);

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=1)
    name = db.Column(db.String(20),unique=1)
    pwd_hash = db.Column(db.String(127))
    art_has_done = db.relationship('AQ',secondary=art_h,backref='done_user_ids')
    art_wrong = db.relationship('AQ',secondary=art_w,backref='wrong_user_ids')
    sci_has_done = db.relationship('SQ',secondary=sci_h,backref='done_user_ids')
    sci_wrong = db.relationship('SQ',secondary=sci_w,backref='wrong_user_ids')
