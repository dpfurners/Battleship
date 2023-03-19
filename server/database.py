import typing
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

if typing.TYPE_CHECKING:
    from sqlalchemy.engine import Engine
    from sqlalchemy.orm.session import Session

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    username = Column("username", String(20), primary_key=True)
    password = Column("password", String(20))
    games = Column("games", Integer, default=0)
    wins = Column("wins", Integer, default=0)
    loses = Column("loses", Integer, default=0)

    def __init__(self, username, password, wins):
        self.username = username
        self.password = password
        self.wins = wins


class DBInterface:
    def __init__(self, db_url: str = 'sqlite:///mydb.db'):
        print(f"[{'DATABASE':<15}] Initializing database...")
        self.db_url = db_url
        self.engine: Engine = create_engine(self.db_url)
        self.session: Session = sessionmaker(bind=self.engine)()

        Base.metadata.create_all(bind=self.engine)

    def Close(self):
        print(f"[{'DATABASE':<15}] Closing database connection...")
        self.session.close()
        self.engine.dispose()

    def DB_SignIn(self, username, password):
        count = self.session.query(User).filter(User.username == username).count()
        # --checking if a user with this name already exists--
        if count == 0:
            self.session.add(User(username, password, 0))
            self.session.commit()
            return True
        return False

    # --function to get data out of database--
    def DB_LogIn(self, username, password):
        count = self.session.query(User).filter(User.username == username).count()
        # --checking if there is one user with this username--
        if count == 1:
            data = self.session.query(User).filter(User.username == username).first()
        else:
            return [False, False]
            # --checking if the password is correct--
        if data.password == password:
            return [True, data.wins]
        return [False, True]


    def DB_AddWin(self, username):
        self.session.query(User).filter(User.username == username).update({'wins': User.wins + 1})
        self.session.commit()

    def DB_AddLoss(self, username):
        self.session.query(User).filter(User.username == username).update({'loses': User.loses + 1})
        self.session.commit()

    def DB_AddGame(self, username):
        self.session.query(User).filter(User.username == username).update({'games': User.games + 1})
        self.session.commit()

    def DB_GetUser(self, username):
        return self.session.query(User).filter(User.username == username).first()

    # --function to get all usernames--
    def DB_GetAllUsers(self):
        return [user for user in self.session.query(User)]