# import datetime
from flask import Flask
from flask_restful import Api
from resources.wng_api_manager import WngApiManager
# from resources.auth_kerb import AuthenticateKerberos
# from resources.auth import Authenticate
# from resources.refresh import Refresh
# from flask_jwt_extended import JWTManager


app = Flask(__name__)
# App configuration is for use with FLASK JWT authentication. Which is not in use currently as the HBASE API access uses
# the Kerboso authentication mechanism. Once the need for API Athentication via JWT is needed this code and the
# associated import statements will need to be uncommented.
# TODO: SECRET_KEY - digitally-sign for the JWT token. This needs to be more difficult. Maybe a random generated string?
# app.config['JWT_SECRET_KEY'] = 'super-secret'
# app.config['JWT_HEADER_TYPE'] = 'JWT'
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(seconds=20)
# jwt = JWTManager(app)
api = Api(app)


# Add resources via the add_resource method

# api.add_resource(Authenticate, '/login')
# api.add_resource(Refresh, '/refresh_token')
# api.add_resource(AuthenticateKerberos, '/auth')
api.add_resource(WngApiManager, '/wng_api')

if __name__ == '__main__':
    app.run(host='0.0.0.0')