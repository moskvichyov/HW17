# app.py

from flask import Flask, request, jsonify, make_response
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db?charset=utf8'
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MOVIES_PER_PAGE = 10

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.Str()
    director_id = fields.Int()
    director = fields.Str()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        director_id = request.args.get('director_id', type=int)
        genre_id = request.args.get('genre_id', type=int)
        if not director_id:
            all_movies = Movie.query.paginate(page=page, per_page=MOVIES_PER_PAGE)
        else:
            all_movies = Movie.query.filter(Movie.director_id == director_id).paginate(page=page, per_page=MOVIES_PER_PAGE)
        if genre_id:
            all_movies = Movie.query.filter(Movie.genre_id == genre_id).paginate(page=page, per_page=MOVIES_PER_PAGE)
        return jsonify(movies_schema.dump(all_movies.items))


@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        one_movie = Movie.query.get(mid)
        return jsonify(movie_schema.dump(one_movie))


@director_ns.route('/')
class DirectorPost(Resource):
    def get(self):
        all_directors = Director.query.all()
        return jsonify(directors_schema.dump(all_directors))

    def post(self):
        rj = request.json
        new_director = Director(**rj)
        with db.session.begin():
            db.session.add(new_director)
        return '',200


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did: int):
        director = Director.query.get(did)
        return jsonify(director_schema.dump(director))

    def put(self, did: int):
        director = Director.query.get(did)
        if not director:
            return '', 404
        rj = request.json
        director.name = rj.get('name')
        db.session.add(director)
        db.session.commit()
        return '', 200

    def patch(self, did: int):
        director = Director.query.get(did)
        if not director:
            return '', 404
        rj = request.json
        if 'name' in rj:
            director.name = rj.get('name')
        db.session.add(director)
        db.session.commit()
        return '', 200

    def delete(self, did: int):
        director = Director.query.get(did)
        if not director:
            return '', 404
        db.session.delete(director)
        db.session.commit()
        return '', 200


@genre_ns.route('/')
class GenresPost(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return jsonify(genres_schema.dump(all_genres))

    def post(self):
        rj = request.json
        new_genre = Genre(**rj)
        with db.session.begin():
            db.session.add(new_genre)
        return '',200


@genre_ns.route('/<int:did>')
class GenresPost(Resource):
    def get(self, did: int):
        genre = Genre.query.get(did)
        return jsonify(genre_schema.dump(genre))

    def put(self, did: int):
        genre = Genre.query.get(did)
        if not genre:
            return '', 404
        rj = request.json
        genre.name = rj.get('name')
        db.session.add(genre)
        db.session.commit()
        return '', 200

    def patch(self, did: int):
        genre = Genre.query.get(did)
        if not genre:
            return '', 404
        rj = request.json
        if 'name' in rj:
            genre.name = rj.get('name')
        db.session.add(genre)
        db.session.commit()
        return '', 200

    def delete(self, did: int):
        genre = Genre.query.get(did)
        if not genre:
            return '', 404
        db.session.delete(genre)
        db.session.commit()
        return '', 200


if __name__ == '__main__':
    app.run(debug=True)
