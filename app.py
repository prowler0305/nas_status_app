from container_status_app import container_status_app


if __name__ == '__main__':

    container_status_app.run(debug=container_status_app.config.get('DEBUG'),
                             threaded=container_status_app.config.get('THREADED'),
                             port=container_status_app.config.get('PORT'),
                             host=container_status_app.config.get('HOST'))
