from app import app, db, Client

with app.app_context():
    # Insertar clientes de prueba con coordenadas de Panamá
    c1 = Client(name="Alexis Rangel", address="Ciudad de Panamá", lat=8.983, lng=-79.517)
    c2 = Client(name="Roger Herrera", address="Costa del Este", lat=9.015, lng=-79.467)
    
    db.session.add_all([c1, c2])
    db.session.commit()
    print("Clientes de prueba creados.")