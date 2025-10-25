from flask import Flask, render_template, request, jsonify

cardapio = [
    'portuguesa',
    'calabresa',
    'quatro queijos',
    'atum com mussarela',
    'mussarela',
    'alho'
]

#app = Flask(__name__)
app = Flask(__name__, static_folder='static', template_folder='templates')


@app.route('/chatSAC')
def chatSAC():
    #lógica de resposta verificando se há cardápio no sistema
    data = request.get_json()

@app.route('/')
def index():
    return render_template('index.html', title='ChatSAC')

if __name__ == '__main__':    
    app.run(debug=True)

