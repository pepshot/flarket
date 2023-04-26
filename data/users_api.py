import flask
from flask import jsonify, request
from . import db_session
from .users import User


blueprint = flask.Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'surname', 'name', 'city', 'address',
                                    'email', 'modified_date'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:users_id>', methods=['GET'])
def get_one_user(users_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(users_id)
    if not users:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': users.to_dict(only=('id', 'surname', 'name', 'city', 'address',
                                        'email', 'modified_date'))
        }
    )


@blueprint.route('/api/users', methods=['POST'])
def create_user():
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})

    elif not all(key in request.json for key in
                 ['name', 'city', 'email']):
        return jsonify({'error': 'Bad request'})

    user = User(
        surname=request.json['surname'],
        name=request.json['name'],
        city=request.json['city'],
        address=request.json['address'],
        email=request.json['email'],
    )
    db_sess.add(user)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PUT'])
def edit_user(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not any(key in request.json for key in
                 ['name', 'city', 'email']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if not user:
        return jsonify({'error': 'Not found'})

    user.surname = request.json['surname'] if request.json.get('surname') else user.surname
    user.name = request.json['name'] if request.json.get('name') else user.name
    user.city = request.json['city'] if request.json.get('city') else user.city
    user.address = request.json['address'] if request.json.get('address') else user.address
    user.email = request.json['email'] if request.json.get('email') else user.email
    db_sess.commit()
    return jsonify({'success': 'add - OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        return jsonify({'error': 'Not found'})
    db_sess.delete(users)
    db_sess.commit()
    return jsonify({'success': 'OK'})
