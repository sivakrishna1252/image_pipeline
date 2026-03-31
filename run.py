from app import create_app

app=create_app()

if __name__=='__main__':
    app.run(debug=True,port=8703)            #this is deployment mode