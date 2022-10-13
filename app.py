from flask import Flask

# create app
app = Flask(__name__)

@app.route("/")
def home():
    return("Online!")

if __name__ == '__main__':
    app.run()
