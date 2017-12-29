from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity


class Authenticate(Resource):
    @staticmethod
    def post():
        """
        Method to create both access and refresh tokens.

        The create_access_token() creates the JWT access token which has a short lifespan. The create_refresh_token()
        creates a refresh token with a longer life span so that users can refresh their access token when it expires.

        Test using following cURL command after obtain JWT from login method:
            curl -H "content-type: application/json" -X POST -d '{"username":"test","password":"test"}' http://localhost:5000/jwt_simple/login
        :return:
        """
        if not request.is_json:
            response = jsonify({'msg': 'Missing JSON in request'})
            response.status_code = 400
            return response

        params = request.get_json()
        username = params.get('username')
        password = params.get('password')

        if not username:
            response = jsonify({'msg': 'Missing username parameter'})
            response.status_code = 400
            return response
        if not password:
            response = jsonify({'msg': 'Missing password parameter'})
            response.status_code = 400
            return response

        if username != 'test' or password != 'test':
            response = jsonify({'msg': 'Bad username or password'})
            response.status_code = 401
            return response

        # Identity can be any data that is json serializable
        art = {
            'access_token': create_access_token(identity=username),
            'refresh_token': create_refresh_token(identity=username)
        }
        print(art)
        response = jsonify(art)
        response.status_code = 200
        return response

    @jwt_refresh_token_required
    def refresh(self):
        """

        :return:
        """
        current_user = get_jwt_identity()
        nat = {
            'access_token': create_access_token(identity=current_user)
        }

        response = jsonify(nat)
        response.status_code = 200
        return response
