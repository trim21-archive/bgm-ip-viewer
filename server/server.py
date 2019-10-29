from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    return render_template('subject.html', subject_id=subject_id)


print('server finish initialization')
if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
