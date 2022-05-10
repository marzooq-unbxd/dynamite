from qcs import app, init

if __name__ == "__main__":
    
    init()
    app.run(host='0.0.0.0', port=8080, debug=True,use_reloader=False)