import os
from flask import Flask
from flask_restful import Api

container_status_app = Flask(__name__)
container_status_app.config.from_object(os.environ.get('app_env'))
api = Api(container_status_app, prefix='/v1')
from container_status_app.container_status import ContainerStatus
from container_status_app.update_container_status import UpdateContainer


container_status_view = ContainerStatus.as_view(name='container_status')
update_container_view = UpdateContainer.as_view(name='update_container')

container_status_app.add_url_rule('/cstatus', view_func=container_status_view, methods=['GET'])
container_status_app.add_url_rule('/nas_status', view_func=container_status_view, methods=['GET'])
# container_status_app.add_url_rule('/cstatus_update', view_func=update_container_view, methods=['GET', 'POST'])

