from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Зчитування даних з файлу
def read_options_from_file():
    options = {}
    with open('options.txt', 'r') as file:
        for line in file:
            key, name = line.strip().split(' - ')
            options[key] = name
    return options

@app.route('/')
def index():
    options = read_options_from_file()
    return render_template('index.html', options=options)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    # Обробка даних...
    # Можете зберегти у файл або використати якось інакше
    print(data)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
