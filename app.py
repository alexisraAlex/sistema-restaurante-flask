import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Client, Order, OrderItem
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurante.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    f_fecha = request.args.get('fecha')
    f_cliente = request.args.get('cliente')
    f_estado = request.args.get('estado')

    query = Order.query
    if f_fecha:
        try:
            query = query.filter(Order.date == datetime.strptime(f_fecha, '%Y-%m-%d').date())
        except: pass
    if f_estado:
        query = query.filter(Order.status == f_estado)
    if f_cliente:
        query = query.join(Client).filter(Client.name.contains(f_cliente))
    
    return render_template('index.html', ordenes=query.all())

@app.route('/clientes', methods=['GET', 'POST'])
def gestionar_clientes():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        lat = request.form.get('lat', 8.98)
        lng = request.form.get('lng', -79.51)
        
        nuevo = Client(name=nombre, address=direccion, lat=float(lat), lng=float(lng))
        db.session.add(nuevo)
        db.session.commit()
        flash("Cliente registrado. Ya puedes crear su orden.", "success")
        return redirect(url_for('ordenes'))
    return render_template('clientes.html')

@app.route('/ordenes', methods=['GET', 'POST'])
def ordenes():
    if request.method == 'POST':
        c_id = request.form.get('client_id')
        plato = request.form.get('plato')
        if not c_id or not plato:
            flash("Selecciona cliente y plato", "danger")
            return redirect(url_for('ordenes'))

        nueva_orden = Order(client_id=c_id, date=datetime.now().date(), total=12.50, status='Pendiente')
        db.session.add(nueva_orden)
        db.session.flush()

        item = OrderItem(order_id=nueva_orden.id, dish_name=plato, quantity=1, price=12.50)
        db.session.add(item)
        db.session.commit()
        flash("Orden registrada con éxito", "success")
        return redirect(url_for('index'))

    clientes = Client.query.all()
    return render_template('ordenes.html', clientes=clientes)

@app.route('/entregar/<int:id>')
def entregar_orden(id):
    orden = Order.query.get_or_404(id)
    orden.status = 'Entregado'
    db.session.commit()
    flash(f"Orden #{id} entregada correctamente", "success")
    return redirect(url_for('index'))

@app.route('/api/sugerencias')
def sugerencias():
    query = request.args.get('query')
    key = os.environ.get("SPOONACULAR_API_KEY")
    url = "https://api.spoonacular.com/recipes/autocomplete"
    try:
        r = requests.get(url, params={"apiKey": key, "number": 5, "query": query}, timeout=5)
        return jsonify(r.json())
    except: return jsonify([])

@app.route('/dashboard')
def dashboard():
    ventas = db.session.query(Client.name, db.func.sum(Order.total)).join(Order).group_by(Client.name).all()
    top = db.session.query(OrderItem.dish_name, db.func.sum(OrderItem.quantity)).group_by(OrderItem.dish_name).limit(5).all()
    return render_template('dashboard.html', ventas=ventas, platos=top)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)