from collections import Counter
from flask import Flask, flash, json, redirect, render_template, request, jsonify, url_for
from matplotlib import pyplot as plt
import matplotlib
import tensorflow as tf
import numpy as np
import cv2
import os
from datetime import datetime
import json as json_module
import flask_login as login_manager
from models.prediccion import Prediccion
import models.usuario as usuario_model
from flask_sqlalchemy import SQLAlchemy
from configbd.bd import Config
from werkzeug.security import check_password_hash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash
from configbd.bd import db


app = Flask(__name__)
app.config.from_object(Config) 
db.init_app(app)
login_manager = login_manager.LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


matplotlib.use('Agg')  # Para no abrir ventana gráfica
model = tf.keras.models.load_model("modelo_alzheimer.h5")

CLASES = ['NonDemented', 'VeryMildDemented', 'MildDemented', 'ModerateDemented']
COLORES = ['#00ffcc', '#00ccff', '#cc00ff', '#ffcc00']

# Crear carpetas necesarias
if not os.path.exists("static/plots"):
    os.makedirs("static/plots")
if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")


@login_manager.user_loader
def load_user(user_id):
    return usuario_model.Usuario.query.get(int(user_id))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        usuario = usuario_model.Usuario.query.filter_by(correo=correo).first()
                
        if usuario and check_password_hash(usuario.contraseña, contraseña):
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('home'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        correo = request.form['correo']
        nombre = request.form['nombre']
        contraseña = request.form['contraseña']


        contraseña_hash = generate_password_hash(contraseña)
        nuevo_usuario = usuario_model.Usuario(correo=correo, nombre=nombre, contraseña=contraseña_hash)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Registro exitoso', 'success')
        return redirect(url_for('login'))

    return render_template("registro.html")

@app.route('/nosotros')
@login_required
def nosotros():
    return render_template("nosotros.html")

@app.route('/')
@login_required
def home():
    nombre_usuario = current_user.nombre if hasattr(current_user, 'nombre') else current_user.correo
    return render_template("index.html", nombre_usuario=nombre_usuario)

@app.route('/gallery')
@login_required
def gallery():
    folder = f'static/uploads/{current_user.id}'
    os.makedirs(folder, exist_ok=True)
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg'))]
    images = [f"uploads/{current_user.id}/{f}" for f in files]
    return render_template('gallery.html', images=images)


@app.route("/stats")
@login_required
def stats():
    
    preds = Prediccion.query.filter_by(usuario_id=current_user.id)\
                             .order_by(Prediccion.fecha).all()

    if not preds:
        return render_template("stats.html",
                               imagen1=None,
                               imagen2=None,
                               imagen3=None,
                               imagen4=None,
                               tabla_html="<p>No hay datos estadísticos disponibles</p>")


    fechas = [p.fecha.strftime('%Y-%m-%d') for p in preds]
    clases = [p.resultado for p in preds]

   
    conteo = Counter(clases)

    
    plt.figure(figsize=(10, 6))
    plt.bar(conteo.keys(), conteo.values(), color=COLORES)
    plt.xlabel("Clases")
    plt.ylabel("Número de predicciones")
    plt.title("Predicciones por clase")
    plt.tight_layout()
    plt.savefig("static/plots/predicciones.png")
    plt.close()

    
    plt.figure(figsize=(8, 8))
    plt.pie(conteo.values(),
            labels=conteo.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=COLORES,
            textprops={'color': 'white'})
    plt.axis('equal')
    plt.title("Distribución porcentual", color='white')
    plt.savefig("static/plots/porcentajes.png", transparent=True)
    plt.close()

   
    fechas_count = Counter(fechas)
    fechas_ordenadas = sorted(fechas_count.items(),
                              key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
    fechas_lista = [f[0] for f in fechas_ordenadas]
    valores_lista = [f[1] for f in fechas_ordenadas]

    plt.figure(figsize=(12, 6), facecolor='#0f0f0f')
    ax = plt.gca()
    ax.set_facecolor('#0f0f0f')
    for spine in ax.spines.values():
        spine.set_color('white')
    ax.tick_params(colors='white')
    ax.set_yticks(np.arange(min(valores_lista), max(valores_lista)+1, 1))

    plt.plot(fechas_lista, valores_lista,
             marker='o', linestyle='-', color=COLORES[1])
    plt.xlabel('Fecha', color='white')
    plt.ylabel('Predicciones', color='white')
    plt.title('Evolución diaria de predicciones', color='white')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("static/plots/evolucion.png", transparent=True)
    plt.close()

    
    datos_apilados = {c: [] for c in CLASES}
    for fecha in fechas_lista:
        for clase in CLASES:
            cnt = sum(1 for p in preds
                      if p.resultado == clase and p.fecha.strftime('%Y-%m-%d') == fecha)
            datos_apilados[clase].append(cnt)

    plt.figure(figsize=(12, 6), facecolor='#0f0f0f')
    ax = plt.gca()
    ax.set_facecolor('#0f0f0f')
    for spine in ax.spines.values():
        spine.set_color('white')
    ax.tick_params(colors='white')
   
    bottom = np.zeros(len(fechas_lista))
    for i, clase in enumerate(CLASES):
        plt.bar(fechas_lista, datos_apilados[clase],
                bottom=bottom, color=COLORES[i], label=clase)
        bottom += np.array(datos_apilados[clase])
    plt.xlabel('Fecha', color='white')
    plt.ylabel('Predicciones', color='white')
    plt.title('Distribución por clase y día', color='white')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("static/plots/apiladas.png", transparent=True)
    plt.close()

    
    total = sum(conteo.values())
    rows = "".join(
        f"<tr><td>{cl}</td><td>{conteo.get(cl,0)}</td><td>{(conteo.get(cl,0)/total*100):.1f}%</td></tr>"
        for cl in CLASES
    )
    tabla_html = (
        '<table class="stats-table">'
        '<tr><th>Clase</th><th>Predicciones</th><th>Porcentaje</th></tr>'
        + rows +
        f"<tr class='total'><td><strong>TOTAL</strong></td>"
        f"<td><strong>{total}</strong></td>"
        f"<td><strong>100%</strong></td></tr>"
        "</table>"
    )
    nota = (
        f"<div class='data-note'>"
        f"<p><strong>Nota:</strong> Datos actualizados al "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}</p>"
        "</div>"
    )

    return render_template(
        "stats.html",
        imagen1="plots/predicciones.png",
        imagen2="plots/porcentajes.png",
        imagen3="plots/evolucion.png",
        imagen4="plots/apiladas.png",
        tabla_html=tabla_html + nota
    )

@app.route('/prediccion', methods=['POST'])
@login_required
def prediccion():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se envió imagen'})

    imagen = request.files['imagen']
    
    carpeta_usuario = os.path.join('static', 'uploads', str(current_user.id))
    os.makedirs(carpeta_usuario, exist_ok=True)
    ruta = os.path.join(carpeta_usuario, imagen.filename)
    imagen.save(ruta)

    
    img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (64, 64))
    img = img.reshape(1, 64, 64, 1) / 255.0

    
    pred = model.predict(img)
    clase = CLASES[np.argmax(pred)]

    
    nueva_pred = Prediccion(
        usuario_id    = current_user.id,
        resultado     = clase,
        imagen_nombre = imagen.filename
    )
    db.session.add(nueva_pred)
    db.session.commit()

    return jsonify({'resultado': clase})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
