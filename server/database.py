from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    username = Column("username", String(20), primary_key=True)
    password = Column("password", String(20))
    wins = Column("wins", Integer)

    def __init__(self, username, password, wins):
        self.username = username
        self.password = password
        self.wins = wins


# --making a connection to database--
engine = create_engine('sqlite:///mydb.db', echo=True)
Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()


# ----------------------------------------------------------------------------------------------------------------

# --function to load data into database--
def DB_SignIn(username, password):
    count = session.query(User).filter(User.username == username).count()
    # --checking if a user with this name already exists--
    if count == 0:
        session.add(User(username, password, 0))
        session.commit()
        return True
    return False


# --function to get data out of database--
def DB_LogIn(username, password):
    count = session.query(User).filter(User.username == username).count()
    # --checking if there is one user with this username--
    if count == 1:
        data = session.query(User).filter(User.username == username).first()
    else:
        return [False, False]
        # --checking if the password is correct--
    if data.password == password:
        return [True, data.wins]
    return [False, True]


# --function to add a win to a user--
def DB_GetWin(username):
    session.query(User).filter(User.username == username).update({'wins': User.wins + 1})
    session.commit()

#--function to get all usernames--
def DB_GetAllUsers():
    return [user.username for user in session.query(User)]

#--function to get all usernames--
def DB_GetAllUsers():
    return [user.username for user in session.query(User)]

#--function to get all usernames--
def DB_GetAllUsers():
    return [user.username for user in session.query(User)]

#--function to get all usernames--
def DB_GetAllUsers():
    return [user.username for user in session.query(User)]