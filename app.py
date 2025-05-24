from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Store tasks in memory (for now)
tasks = []

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task:
        tasks.append(task)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
