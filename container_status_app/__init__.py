import os
from flask import Flask
from flask_restful import Api
from container_status_app.views.container_status import ContainerStatus
from container_status_app.views.nas_notifications import NasNotifications
from container_status_app.views.nas_faqs import NasFaqs
from container_status_app.views.nas_add_faq import NasAddFaq
from container_status_app.services.set_config_maps import SetConfigMaps

container_status_app = Flask(__name__)
container_status_app.config.from_object(os.environ.get('app_env'))
api = Api(container_status_app, prefix='/v1')

if os.environ.get('hostname'.upper()) is not None:
    if 'container-status-app' in os.environ.get('hostname'.upper()):
        SetConfigMaps()

container_status_view = ContainerStatus.as_view(name='container_status')
# update_container_view = UpdateContainer.as_view(name='update_container')
generate_nas_notifications = NasNotifications.as_view(name='nas_notifications')
faqs = NasFaqs.as_view(name='nas_faqs')
add_faq = NasAddFaq.as_view(name='add_faq')

# container_status_app.add_url_rule('/cstatus', view_func=container_status_view, methods=['GET'])
container_status_app.add_url_rule('/nas_status', view_func=container_status_view, methods=['GET', 'POST'])
container_status_app.add_url_rule('/', view_func=container_status_view, methods=['GET', 'POST'])
container_status_app.add_url_rule('/nas/notify', view_func=generate_nas_notifications, methods=['GET', 'POST'])
container_status_app.add_url_rule('/nas/faqs', view_func=faqs, methods={'GET'})
container_status_app.add_url_rule('/nas/add/faq', view_func=add_faq, methods={'GET', 'POST'})
# container_status_app.add_url_rule('/cstatus_update', view_func=update_container_view, methods=['GET', 'POST'])

