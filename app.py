from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

# Port 8080 for openshift
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
