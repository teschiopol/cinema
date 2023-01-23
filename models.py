from sqlalchemy import *
from app import engine, metadata

# Tables creation
users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String),
              Column('surname', String),
              Column('pwd', String),
              Column('email', String, unique=True),
              Column('idruolo', Integer, ForeignKey('ruoli.id'))
              )

film = Table('film', metadata,
             Column('id', Integer, primary_key=True),
             Column('name', String, unique=True),
             Column('idregista', Integer, ForeignKey('autori.id')),
             Column('durata', Integer),
             Column('idgenere', Integer, ForeignKey('genere.id'))
             )

ruoli = Table('ruoli', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String, unique=True)
              )

spettacoli = Table('spettacoli', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('data', Date),
                   Column('ora', Time),
                   Column('nsala', Integer),
                   Column('idfilm', Integer, ForeignKey('film.id'))
                   )

genere = Table('genere', metadata,
               Column('id', Integer, primary_key=True),
               Column('name', String, unique=True)
               )

autori = Table('autori', metadata,
               Column('id', Integer, primary_key=True),
               Column('name', String, unique=True)
               )

incassi = Table('incassi', metadata,
                Column('id', Integer, primary_key=True),
                Column('prezzo', Integer, default=5),
                Column('idspettacoli', Integer, ForeignKey('spettacoli.id')),
                Column('quantita', Integer)
                )

sala = Table('sala', metadata,
             Column('id', Integer, primary_key=True),
             Column('posto', Integer),
             Column('idspettacoli', Integer, ForeignKey('spettacoli.id')),
             Column('idutente', Integer, ForeignKey('users.id'))
             )

# inizializzo database e creo tabelle
metadata.drop_all(engine)
metadata.create_all(engine)

# popolo il database con le insert
ins = users.insert()
insF = film.insert()
insR = ruoli.insert()
insA = autori.insert()
insG = genere.insert()
insS = spettacoli.insert()
insI = incassi.insert()
insP = sala.insert()
conn = engine.connect()

# insert
conn.execute(insG, [
    {'name': 'Animazione'},
    {'name': 'Avventura'},
    {'name': 'Biografico'},
    {'name': 'Commedia'},
    {'name': 'Documentario'},
    {'name': 'Drammatico'},
    {'name': 'Fantascienza'},
    {'name': 'Fantasy'},
    {'name': 'Guerra'},
    {'name': 'Horror'},
    {'name': 'Thriller'},
    {'name': 'Western'}
])

conn.execute(insA, [
    {'name': 'James Cameron'},
    {'name': 'Quentin Tarantino'},
    {'name': 'Martin Scorsese'},
    {'name': 'Steven Spielberg'},
    {'name': 'Woody Allen'},
    {'name': 'Tim Burton'},
    {'name': 'Roman Polański'},
    {'name': 'Sergio Leone'},
    {'name': 'Christopher Nolan'},
    {'name': 'Clint Eastwood'},
    {'name': 'Paolo Sorrentino'},
    {'name': 'Bryan Singer'},
    {'name': 'Stanley Kubrick'},
    {'name': 'Morgan Matthews'}
])

conn.execute(insR, [
    {'name': 'Gestore'},
    {'name': 'Cliente'}
])

conn.execute(ins, [
    {'name': 'Paolo', 'surname': 'Concolato', 'pwd': 'dev', 'email': 'dev@test.it', 'idruolo': 1},
    {'name': 'Francesco', 'surname': 'Angiolini', 'pwd': 'test', 'email': 'test@test.it', 'idruolo': 2}
])

conn.execute(insF, [
    {'name': 'Avatar', 'idregista': 1, 'durata': 178, 'idgenere': 7},
    {'name': 'Titanic', 'idregista': 1, 'durata': 210, 'idgenere': 6},
    {'name': 'The Irishman', 'idregista': 3, 'durata': 210, 'idgenere': 6},
    {'name': 'Quei bravi ragazzi', 'idregista': 3, 'durata': 148, 'idgenere': 6},
    {'name': 'E. T.', 'idregista': 4, 'durata': 121, 'idgenere': 7},
    {'name': 'Jurassic Park', 'idregista': 4, 'durata': 127, 'idgenere': 2},
    {'name': 'Bastardi senza gloria', 'idregista': 2, 'durata': 153, 'idgenere': 9},
    {'name': 'Django Unchained', 'idregista': 2, 'durata': 165, 'idgenere': 12},
    {'name': 'Midnight in Paris', 'idregista': 5, 'durata': 100, 'idgenere': 8},
    {'name': 'Alice in Wonderland', 'idregista': 6, 'durata': 108, 'idgenere': 8},
    {'name': 'La sposa cadavere', 'idregista': 6, 'durata': 78, 'idgenere': 1},
    {'name': 'Il pianista', 'idregista': 7, 'durata': 150, 'idgenere': 9},
    {'name': 'Per un pugno di dollari', 'idregista': 8, 'durata': 99, 'idgenere': 12},
    {'name': 'La grande bellezza', 'idregista': 11, 'durata': 172, 'idgenere': 4},
    {'name': 'Gran Torino', 'idregista': 10, 'durata': 120, 'idgenere': 11},
    {'name': 'Inception', 'idregista': 9, 'durata': 162, 'idgenere': 11},
    {'name': 'Bohemian Rhapsody', 'idregista': 12, 'durata': 133, 'idgenere': 3},
    {'name': 'Williams', 'idregista': 14, 'durata': 109, 'idgenere': 5},
    {'name': 'Shining', 'idregista': 13, 'durata': 146, 'idgenere': 10}
])

conn.execute(insS, [
    {'data': '2020-08-18', 'ora': '21:00:00', 'idfilm': 1, 'nsala': 1},
    {'data': '2020-09-13', 'ora': '21:00:00', 'idfilm': 1, 'nsala': 1},
    {'data': '2020-09-13', 'ora': '17:00:00', 'idfilm': 1, 'nsala': 1},
    {'data': '2020-09-13', 'ora': '17:00:00', 'idfilm': 1, 'nsala': 2},
    {'data': '2020-08-30', 'ora': '17:00:00', 'idfilm': 3, 'nsala': 2},
    {'data': '2020-08-31', 'ora': '17:00:00', 'idfilm': 8, 'nsala': 1},
    {'data': '2020-09-11', 'ora': '19:30:00', 'idfilm': 4, 'nsala': 2},
    {'data': '2020-09-11', 'ora': '19:30:00', 'idfilm': 1, 'nsala': 1}
])

conn.execute(insI, [
    {'idspettacoli': 1, 'quantita': 1},
    {'idspettacoli': 2, 'quantita': 1},
    {'idspettacoli': 5, 'quantita': 2},
    {'idspettacoli': 5, 'quantita': 1},
    {'idspettacoli': 6, 'quantita': 7},
    {'idspettacoli': 2, 'quantita': 3},
    {'idspettacoli': 7, 'quantita': 3}
])

conn.execute(insP, [
    {'posto': 1, 'idspettacoli': 1, 'idutente': 1},
    {'posto': 5, 'idspettacoli': 2, 'idutente': 2}
])

conn.close()
