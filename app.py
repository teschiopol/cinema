from flask import *
# from sqlalchemy import *
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from models import *
from datetime import date, datetime
import datetime
import math
import re

# declare app
app = Flask(__name__)

# global variable
app.jinja_env.globals['today'] = date.today().strftime("%d-%m-%Y")

# installation parameters
position = 'localhost'
passwordDB = 'admin'
username = 'postgres'

# creation and db connection
engine = create_engine('postgresql+psycopg2://postgres:' + passwordDB + '@' + position + '/postgres')
connection = engine.connect()
connection.execute("commit")
try:
    connection.execute("create database movie")
except Exception:
    print("nothing")
connection.close()
uri = 'postgresql+psycopg2://' + username + ':' + passwordDB + '@' + position + '/movie'
engine = create_engine(uri, echo=True)
metadata = MetaData()

# configuration flask-login
app.config['SECRET_KEY'] = 'super-secret'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "prelogin"


# extension of user to authenticate
class User(UserMixin):
    def __init__(self, id_user, name, surname, email, pwd, id_role):
        self.id = id_user
        self.email = email
        self.pwd = pwd
        self.name = name
        self.surname = surname
        self.id_role = id_role

    def get_id(self):
        return str(self.id)

    def get_role(self):
        return self.id_role


def user_by_email(email):
    connect = engine.connect()
    rs = connect.execute('SELECT * FROM users WHERE email = %s', email)
    user = rs.fetchone()
    connect.close()
    return User(user.id, user.name, user.surname, user.email, user.pwd, user.idRuolo)


@login_manager.user_loader
def load_user(id_user):
    connect = engine.connect()
    rs = connect.execute('SELECT * FROM users WHERE id = %s', id_user)
    user = rs.fetchone()
    connect.close()
    return User(user.id, user.name, user.surname, user.email, user.pwd, user.idRuolo)


# error page doesn't exist
@app.errorhandler(404)
def invalid_url():
    return redirect(url_for('home'))


# error page access forbidden
@app.errorhandler(400)
def invalid_url():
    return redirect(url_for('privateArea'))


# Declaration Route

# Homepage
@app.route('/')
def home():
    connect = engine.connect()
    films = connect.execute('SELECT film.name as film, film.id as id,  film.durata as durata, genere.name as '
                            'genere, autori.name as autore FROM film JOIN autori on film.idregista = autori.id '
                            'JOIN genere on genere.id = film.idgenere order by film.name')
    gen = connect.execute('SELECT * from genere order by name')
    reg = connect.execute('SELECT * FROM autori order by name')
    connect.close()
    return render_template('index.html', films=films, gen=gen, reg=reg)


# Query Cerca Film
@app.route('/cerca', methods=['GET', 'POST'])
def ricerca():
    connect = engine.connect()
    if request.form['genere'] != '' and request.form['regista'] != '':
        s = select([film.c.name.label('film'), film.c.id.label('id'), film.c.durata.label('durata'),
                    genere.c.name.label('genere'), autori.c.name.label('autore')]). \
            where(
            and_(film.c.idregista == autori.c.id, genere.c.id == film.c.idgenere, genere.c.name == bindparam('gen'),
                 autori.c.name == bindparam('reg')))
        films = connect.execute(s, gen=request.form['genere'], reg=request.form['regista'])
    elif request.form['regista'] != '':
        s = select([film.c.name.label('film'), film.c.id.label('id'), film.c.durata.label('durata'),
                    genere.c.name.label('genere'), autori.c.name.label('autore')]). \
            where(
            and_(film.c.idregista == autori.c.id, genere.c.id == film.c.idgenere, autori.c.name == bindparam('reg')))
        films = connect.execute(s, reg=request.form['regista'])
    elif request.form['genere'] != '':
        s = select([film.c.name.label('film'), film.c.id.label('id'), film.c.durata.label('durata'),
                    genere.c.name.label('genere'), autori.c.name.label('autore')]). \
            where(
            and_(film.c.idregista == autori.c.id, genere.c.id == film.c.idgenere, genere.c.name == bindparam('gen')))
        films = connect.execute(s, gen=request.form['genere'])
    else:
        s = select([film.c.name.label('film'), film.c.id.label('id'), film.c.durata.label('durata'),
                    genere.c.name.label('genere'), autori.c.name.label('autore')]). \
            where(and_(film.c.idregista == autori.c.id, genere.c.id == film.c.idgenere)).order_by('film')
        films = connect.execute(s)
    gen = connect.execute('SELECT * from genere')
    regista = connect.execute('SELECT * FROM autori')
    connect.close()
    return render_template('index.html', films=films, genere=request.form['genere'], regista=request.form['regista'],
                           gen=gen, reg=regista)


# Area Private
@app.route('/user')
def pre_login():
    if current_user.is_authenticated:
        return redirect(url_for('privateArea'))
    else:
        return render_template('user.html')


# Lista show film
@app.route('/acquista', methods=['GET', 'POST'])
@login_required
def compra():
    connect = engine.connect()
    ticket = connect.execute(
        'SELECT * FROM spettacoli WHERE idfilm = %s and %s <= data  group by data, spettacoli.id order by data, ora',
        request.form["idfilm"], datetime.date.today())
    film_data = connect.execute('SELECT * FROM film WHERE id = %s', request.form["idfilm"]).fetchone()
    name = film_data['name']
    film_id = film_data['id']
    connect.close()
    result = ticket.fetchall()
    final_result = [list(i) for i in result]
    return render_template('compra.html', ticket=final_result, l=len(final_result), name=name, id=film_id)


# Gestione richiesta login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # regex per evitare input malevoli o con formati non corretti
    if request.method == 'POST':
        addressToVerify = request.form['email']
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
        match1 = re.match("^[A-Za-z0-9_!?-]+$", request.form['pwd'])
        if match is None or match1 is None:
            return render_template('user.html', successo='no')
        connect = engine.connect()
        rs = connect.execute('SELECT pwd FROM users WHERE email = %s', [request.form['email']])
        controllo = rs.fetchone()
        if controllo is not None:
            real_pwd = controllo['pwd']
            connect.close()
            if request.form['pwd'] == real_pwd:
                user = user_by_email(request.form['email'])
                login_user(user)
                return redirect(url_for('home'))
            else:
                return render_template('user.html', successo='no')
        else:
            return render_template('user.html', successo='no')
    else:
        return render_template('user.html', successo='no')


# Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for('home'))


# Area Private Admin
@app.route('/private', methods=['GET', 'POST'])
@login_required
def private_area():
    if current_user.get_role() == 2:
        return redirect(url_for('testpp'))
    else:
        connect = engine.connect()
        films = connect.execute(
            'SELECT film.name as film, film.id as id,  film.durata as durata, genere.name as genere, autori.name as '
            'autore FROM film JOIN autori on film.idregista = autori.id JOIN genere on genere.id = film.idgenere order '
            'by film.name')
        gen = connect.execute('SELECT * from genere order by name')
        reg = connect.execute('SELECT * FROM autori order by name')
        user = connect.execute('SELECT * FROM users order by id')
        moneyF = connect.execute('SELECT sum(prezzo*quantita) as ticket, name, sum(quantita) as n '
                                 'from incassi i join spettacoli s on i.idspettacoli = s.id join film on'
                                 ' s.idfilm = film.id group by name order by ticket desc')
        moneyG = connect.execute('SELECT sum(prezzo*quantita) as ticket, genere.name as name, sum(quantita) as n  '
                                 'from incassi i join spettacoli s on i.idspettacoli = s.id join film on s.idfilm = '
                                 'film.id join genere on film.idgenere = genere.id  group by genere.name  order by '
                                 'ticket desc')
        moneyR = connect.execute('SELECT sum(prezzo*quantita) as ticket, autori.name as name, sum(quantita) as n  '
                                 'from incassi i join spettacoli s on i.idspettacoli = s.id join film on s.idfilm = '
                                 'film.id join autori on film.idregista = autori.id  group by autori.name  order by '
                                 'ticket desc')
        filmN = connect.execute('SELECT * from film order by film.name')
        spet = connect.execute(
            'SELECT spettacoli.*, film.name from spettacoli join film on film.id = spettacoli.idfilm where %s <= data '
            'order by film.name',
            datetime.date.today())
        connect.close()
        return render_template('gestione.html', films=films, gen=gen, reg=reg, utenti=user, moneyF=moneyF,
                               moneyR=moneyR, moneyG=moneyG, filmsN=filmN, spet=spet)


# Sign up
@app.route('/signup')
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('privateArea'))
    else:
        return render_template('registra.html')


# Handler SignUp
@app.route('/registrato', methods=['GET', 'POST'])
def registrato():
    connect = engine.connect()
    # controllo formato mail
    addressToVerify = request.form['email']
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
    if match is None:
        return render_template('registra.html', errore='e')
    # controllo input corretto
    if not re.match("^[A-Za-z0-9_!?-]+$", request.form['pwd']) \
            or not re.match("^[A-Za-z0-9]+$", request.form['name']) \
            or not re.match("^[A-Za-z0-9]+$", request.form['surname']):
        return render_template('registra.html', errore='d')
    # controllo esistenza mail
    rs = connect.execute('SELECT name from users where email = %s', request.form['email'])
    rs = rs.fetchone()
    if rs is None:
        connect.execute('INSERT INTO users(pwd,email,name,surname,idRuolo) VALUES (%s, %s, %s, %s, %s)',
                        [request.form['pwd'], request.form['email'], request.form['name'],
                         request.form['surname'],
                         request.form['idRuolo']])
    else:
        return render_template('registra.html', errore='si')
    connect.close()
    return render_template('user.html', successo='si')


# Richiesta elimina Film
@app.route('/eliminaFilm', methods=['GET', 'POST'])
@login_required
def eliminafilm():
    connect = engine.connect()
    ch = connect.execute('SELECT * FROM incassi i join spettacoli s on i.idspettacoli = s.id WHERE s.idfilm = %s',
                         request.form['idfilm']).fetchall()
    ch = list(ch)
    if len(ch) > 0:
        connect.close()
        return render_template('insertError.html')
    else:
        connect.execute('DELETE FROM spettacoli WHERE idfilm = %s', request.form['idfilm'])
        connect.execute('DELETE FROM film WHERE id = %s', request.form['idfilm'])
        connect.close()
        return render_template('confirmedOperation.html')


# Richiesta elimina spettacolo
@app.route('/eliminaSpettacolo', methods=['GET', 'POST'])
@login_required
def eliminaspettacolo():
    connect = engine.connect()
    ch = connect.execute('SELECT * from incassi WHERE idspettacoli = %s', request.form['idspett']).fetchall()
    ch = list(ch)
    if len(ch) > 0:
        connect.close()
        return render_template('insertError.html')
    else:
        connect.execute('DELETE FROM spettacoli WHERE id = %s', request.form['idspett'])
        connect.close()
        return render_template('confirmedOperation.html')


# Richiesta inserisci Film
@app.route('/filmInserito', methods=['GET', 'POST'])
@login_required
def ins_film():
    duration = request.form['durata']
    if int(duration) < 1:
        return render_template('insertError.html')
    connect = engine.connect()
    rs = connect.execute('SELECT * from film WHERE name = %s', request.form['name'])
    if rs.fetchone() is None:
        connect.execute('INSERT INTO film(name,idregista,durata,idgenere) VALUES (%s, %s, %s, %s)',
                        [request.form['name'], request.form['regista'], duration, request.form['genere']])
    connect.close()
    return render_template('confirmedOperation.html')


# Insert show
def insert_show(dt, hr, ns, idf):
    connect = engine.connect()
    connect.execute('INSERT INTO spettacoli(data,ora,nsala,idfilm) '
                    'VALUES (%s, %s, %s, %s)', [dt, hr, ns, idf])


# Richiesta inserisci spettacolo
@app.route('/spettacoloInserito', methods=['GET', 'POST'])
@login_required
def ins_show():
    connect = engine.connect()
    date_sel = datetime.datetime.strptime(request.form['datepicker'], "%d-%m-%Y")
    if date_sel <= datetime.datetime.today():
        return render_template('insertError.html')
    ora = request.form['orario']
    nl = connect.execute('SELECT durata from film where film.id = %s', request.form['filmIns']).fetchone()[0]
    # controllo di non sovrapposizione con data, ore e sale di altri film
    rs = connect.execute(
        'SELECT ora, durata from spettacoli join film on spettacoli.idfilm = film.id WHERE nsala = %s and data = %s '
        'order by ora',
        request.form['sala'], date_sel)
    rs = list(rs.fetchall())
    if len(rs) > 0:
        mylist = [15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0,
                  23.5, 24.0, 24.5, 25.0, 25.5, 26.0, 26.5, 27.0]
        for r in rs:
            v = float(r[0].strftime('%-H.%-M'))
            left = str(v)[-2:]
            if left == 30:
                v = v + 0.2
            mylist.remove(v)
            dur = math.ceil(float(r[1]) / 30)
            for a in range(1, dur):
                v = v + 0.5
                mylist.remove(v)
        n = float(ora)
        if n in mylist:
            c = 1
            dur = math.ceil(float(nl) / 30)
            for b in range(1, dur):
                n = n + 0.5
                if n not in mylist:
                    c = 0
            if c == 1:
                if ora[3:5] == '50':
                    m = 30
                else:
                    m = 00
                h = int(ora[:2])
                ora = datetime.datetime.today().replace(hour=h, minute=m).strftime("%H:%M:%s")
                insert_show(date_sel.strftime("%Y-%m-%d"), str(ora)[:6] + '00', request.form['sala'],
                            request.form['filmIns'])
                return render_template('confirmedOperation.html')
    else:
        if ora[3:5] == '50':
            m = 30
        else:
            m = 00
        h = int(ora[:2])
        ora = datetime.datetime.today().replace(hour=h, minute=m).strftime("%H:%M:%s")
        insert_show(date_sel.strftime("%Y-%m-%d"), str(ora)[:6] + '00', request.form['sala'], request.form['filmIns'])
        return render_template('confirmedOperation.html')
    connect.close()
    return render_template('insertError.html')


# Update dati utente
@app.route('/aggUtente', methods=['GET', 'POST'])
@login_required
def up_user():
    connect = engine.connect()
    # parsing input
    addressToVerify = request.form['email']
    match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addressToVerify)
    match1 = re.match("^[A-Za-z0-9_!?-]+$", request.form['pwd'])
    match2 = re.match("^[A-Za-z0-9]+$", request.form['name'])
    match3 = re.match("^[A-Za-z0-9]+$", request.form['surname'])
    utente = connect.execute('SELECT * from users WHERE id = %s', current_user.get_id()).fetchone()
    acq = connect.execute('select sala.posto, spettacoli.data, spettacoli.ora, film.name '
                          'from sala join spettacoli on sala.idspettacoli = spettacoli.id join film on film.id = '
                          'spettacoli.idfilm where idutente = %s order by film.name, spettacoli.data, spettacoli.ora, '
                          'sala.posto',
                          current_user.get_id())
    acq = list(acq.fetchall())
    if match is None or match1 is None or match2 is None or match3 is None:
        return render_template('private.html', successo='no', utente=utente, acquisto=acq, l=len(acq))
    connect.execute("UPDATE users SET pwd = %s , name = %s, surname = %s WHERE email = %s ",
                    [request.form['pwd'], request.form['name'], request.form['surname'], request.form['email']])
    user = connect.execute('SELECT * from users WHERE id = %s', current_user.get_id()).fetchone()
    connect.close()
    return render_template('private.html', successo='si', utente=user, acquisto=acq, l=len(acq))


# Selezione posto da acquistare per lo spettacolo
@app.route('/prenotaPosto', methods=['GET', 'POST'])
@login_required
def book_place():
    spettacolo = request.form['spettacolo']
    films = request.form['film']
    connect = engine.connect()
    presi = connect.execute('SELECT posto FROM sala WHERE idspettacoli = %s', spettacolo)
    sal = request.form['sala']
    connect.close()
    booked = list(presi.fetchall())
    return render_template('posto.html', spettacolo=spettacolo, film=films, presi=booked, len=len(booked), sala=sal)


# Richiesta acquisto biglietto
@app.route('/acquistaPosto', methods=['GET', 'POST'])
@login_required
def acquisto():
    c = -2
    pos = []
    for s in request.form:
        pos.append(s)
        c = c + 1
    pos = pos[2:]
    connect = engine.connect()
    connect.execute('INSERT INTO incassi(prezzo, idspettacoli, quantita) VALUES (5, %s, %s)',
                    [int(request.form["idspettacoli"]), c])
    for e in pos:
        connect.execute('INSERT INTO sala(posto, idspettacoli, idutente) VALUES (%s, %s, %s)',
                        [int(e), int(request.form["idspettacoli"]), current_user.get_id()])
    connect.close()
    return render_template('pagato.html', acq=c)


# Richiesta elimina utente
@app.route('/gestUtente', methods=['GET', 'POST'])
@login_required
def gest_user():
    connect = engine.connect()
    ch = connect.execute(
        'SELECT * from sala join spettacoli on sala.idspettacoli = spettacoli.id where idutente = %s and  %s <= data ',
        request.form['idutente'], datetime.date.today()).fetchall()
    ch = list(ch)
    if len(ch) > 0:
        return render_template('insertError.html')
    else:
        connect.execute('DELETE from sala where idutente = %s', request.form['idutente'])
        connect.execute('DELETE FROM users WHERE id = %s and id NOT IN (select idutente from sala ) ',
                        request.form['idutente'])
        connect.close()
        return render_template('confirmedOperation.html')


# Richiesta modifica ruolo utente
@app.route('/promuoviAdmin/<index>')
@login_required
def promote_admin(index):
    connect = engine.connect()
    index = int(index)
    ruolo = connect.execute('SELECT idRuolo from users where id = %s', index).fetchone()['idRuolo']
    if ruolo == 1:
        ruolo = 2
    else:
        ruolo = 1
    connect.execute('UPDATE users SET idRuolo = %s WHERE id = %s', [ruolo, index])
    connect.close()
    return render_template('confirmedOperation.html')


# Area Privata utente
@app.route('/pp', methods=['GET', 'POST'])
@login_required
def testpp():
    connect = engine.connect()
    utente = connect.execute('SELECT * from users WHERE id = %s', current_user.get_id()).fetchone()
    acq = connect.execute('select distinct sala.posto, spettacoli.data, spettacoli.ora, film.name, spettacoli.nsala '
                          'from sala join spettacoli on sala.idspettacoli = spettacoli.id join film on'
                          'film.id = spettacoli.idfilm where idutente = %s order by spettacoli.data, spettacoli.ora, '
                          'sala.posto, spettacoli.nsala, film.name',
                          current_user.get_id())
    connect.close()
    acq = list(acq.fetchall())
    return render_template('private.html', utente=utente, acquisto=acq, l=len(acq))


# TODO: manage debug mode from terminal options
# main
if __name__ == '__main__':
    app.run(debug=True)
