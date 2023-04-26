import flask
import json
from flask import jsonify, request
from . import db_session
from .posts import Posts


blueprint = flask.Blueprint(
    'posts_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/posts')
def get_posts():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()
    js_file = jsonify({'posts':[item.to_dict(only=('id', 'author', 'category', 'name_post',
                                                   'content_post','publication_date', 'price',
                                                   'is_hidden')) for item in posts]})
    print(type(js_file))
    print(js_file.json['posts'][0]['id'])
    return jsonify(
        {
            'posts':
                [item.to_dict(only=('id', 'author', 'category', 'name_post', 'content_post',
                                    'publication_date', 'price', 'is_hidden'))
                 for item in posts]
        }
    )


@blueprint.route('/api/posts/<int:post_id>', methods=['GET'])
def get_one_post(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).filter(Posts.id == post_id).all()
    print([i for i in post])
    print(1)
    if not post:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'posts': post.to_dict(only=('id', 'author', 'category', 'name_post', 'content_post',
                                        'publication_date', 'price', 'is_hidden'))
        }
    )


@blueprint.route('/api/posts', methods=['POST'])
def create_post():
    if not request.json:
        return jsonify({'error': 'Empty request'})

    elif not all(key in request.json for key in
                 ['author', 'name_post']):
        return jsonify({'error': 'Bad request'})

    db_sess = db_session.create_session()
    all_id_posts = [item.id for item in db_sess.query(Posts).all()]
    if request.json['id'] in all_id_posts:
        return jsonify({'error': 'Id already exists'})

    jobs = Posts(
        author=request.json['author'],
        category=request.json['category'],
        name_post=request.json['name_post'],
        content_post=request.json['content_post'],
        price=request.json['price'],
        is_hidden=request.json['is_hidden']
    )
    db_sess.add(jobs)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/posts/<int:post_id>', methods=['PUT'])
def edit_post(post_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not any(key in request.json for key in
                 ['author', 'name_post']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).get(post_id)

    if not posts:
        return jsonify({'error': 'Not found'})
    posts.author = request.json['author'] if request.json.get('author') else posts.author
    posts.category = request.json['category'] if request.json.get('category') else posts.category
    posts.name_post = request.json['name_post'] if request.json.get('name_post') else posts.name_post
    posts.content_post = request.json['content_post'] if request.json.get('content_post') else posts.content_post
    posts.price = request.json['price'] if request.json.get('price') else posts.price
    posts.publication_date = request.json['publication_date'] if request.json.get('publication_date') else posts.publication_date
    posts.is_hidden = request.json['is_hidden'] if request.json.get('is_hidden') else posts.is_hidden
    db_sess.commit()
    return jsonify({'success': 'add - OK'})


@blueprint.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_news(post_id):
    db_sess = db_session.create_session()
    post = db_sess.query(Posts).get(post_id)
    if not post:
        return jsonify({'error': 'Not found'})
    db_sess.delete(post)
    db_sess.commit()
    return jsonify({'success': 'OK'})
