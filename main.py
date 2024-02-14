from app import create_app

app, socketio = create_app()

if __name__ == '__main__':
    # DEBUG is SET to TRUE. CHANGE FOR PROD
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
