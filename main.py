from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import desc
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired
import requests
import sqlite3
from MovieSearch import MovieSearch

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)
con = sqlite3.connect('movies.db', check_same_thread=False)


class addMovie(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    rating = FloatField('Rating', validators=[DataRequired()])
    ranking = IntegerField('Ranking', validators=[DataRequired()])
    review = StringField('Description', validators=[DataRequired()])
    img_url = StringField('Image Url', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchMovie(FlaskForm):
    title = StringField('Search by Movie Title', validators=[DataRequired()])
    submit = SubmitField('Search')


class editMovie(FlaskForm):
    rating = FloatField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])

    submit = SubmitField('Done')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=False)
    rating = db.Column(db.Float, unique=False, nullable=False)
    ranking = db.Column(db.Integer, unique=False, nullable=False)
    review = db.Column(db.String(500), unique=False, nullable=False)
    img_url = db.Column(db.String(500), unique=False, nullable=False)


db.create_all()


def getMovie(title):
    headers = {
        "api_key": "ce05435310831a2489105985436c7edb"
    }

    params = {
        "api_key": "ce05435310831a2489105985436c7edb",
        "query": {title}

    }
    url = 'https://api.themoviedb.org/3/search/movie'

    search = requests.get(url=url, params=params, headers=headers)
    search_results = search.json()['results']
    search_results_list = []
    for result in search_results:
        if result['poster_path'] is not None:
            year = (result['release_date']).split('-')
            poster = 'https://image.tmdb.org/t/p/w500' + result['poster_path']
            print(poster)
            print(result['poster_path'])
            search_results_list.append(MovieSearch(title=result['original_title'], year=int(year[0]),
                                                   description=result['overview'], img_url=poster))

    return search_results_list


def insert_movie(_title, _year, _description, _rating, _ranking, _review, _img_url):
    new_movie = Movie(title=_title,
                      year=_year,
                      description=_description,
                      rating=_rating,
                      ranking=_ranking,
                      review=_review,
                      img_url=_img_url
                      )
    db.session.add(new_movie)
    db.session.commit()


def delete_movie(_id):
    del_movie = Movie.query.filter_by(id=_id).first()
    db.session.delete(del_movie)
    db.session.commit()


def edit_movie(_id, _rating, _review):
    mod_movie = Movie.query.filter_by(id=_id).first()
    mod_movie.rating = _rating
    mod_movie.review = _review
    db.session.commit()


@app.route("/edit", methods=['POST', 'GET'])
def edit():
    form = editMovie()
    if request.method == 'POST':
        print(request.form['book_id'], request.form['rating'])
        edit_movie(request.form['book_id'], request.form['rating'], request.form['review'])

        return redirect(url_for("home"))

    return render_template("edit.html", form=form, book_id=request.args.get('id'))


@app.route("/delete", methods=['POST', 'GET'])
def delete():
    delete_movie(request.args.get('id'))
    return redirect(url_for("home"))


@app.route("/")
def home():
    # insert_movie()
    # cur = con.cursor()
    # query = 'select * from Movie order by rating ASC'
    # x = cur.execute(query)
    # for p in x :
    #     print(p)

    all_movies = Movie.query.order_by(desc(Movie.rating)).all()

    for x in range(len(all_movies)):
        print(x)
        all_movies[x].ranking = x + 1
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route("/add2", methods=['POST', 'GET'])
def add2():
    form = SearchMovie()
    print("hello")
    print(request.method)
    if request.method == 'POST':
        print(request.form['title'])
        results = getMovie(request.form['title'])
        for result in results:
            print(result.title)
            print(result.year)
            print(result.description)
            print(result.img_url)

        return render_template("add2.html", results=getMovie(request.form['title']), form=form)

    return render_template("add2.html", form=form)


@app.route("/insert", methods=['POST', 'GET'])
def insert():
    if request.method == 'GET':
        print(request.args.get('title'))
        print(request.args.get('year'))
        print(request.args.get('description'))
        print(request.args.get('img_url'))

        insert_movie(request.args.get('title'), int(request.args.get('year')), request.args.get('description'),
                     0, 0, 'None',
                     request.args.get('img_url'))
        return redirect(url_for("home"))


@app.route("/add", methods=['POST', 'GET'])
def add():
    form = addMovie()
    print(request.method)
    if request.method == 'POST':
        insert_movie(request.form['title'], int(request.form['year']), request.form['description'],
                     float(request.form['rating']), int(request.form['ranking']), request.form['review'],
                     request.form['img_url'])
        return redirect(url_for("home"))

    return render_template("add.html", form=form)


if __name__ == '__main__':
    app.run(debug=True, port=9002)
