from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_mail import Mail, Message
import random

app = Flask(__name__)
mail = Mail(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'tu_correo@gmail.com'
app.config['MAIL_PASSWORD'] = 'tu_password_de_aplicacion'
app.secret_key = "panadero_con_el_pan"

url = "mongodb+srv://Angel17:171009Ang@clusrob1.xaujcjr.mongodb.net/?appName=ClusRob1"

cliente = MongoClient(url)

db = cliente["supermercado"]

usuarios = db["usuarios"]
tareas_db = db["tareas"]
productos = db["productos"]

print("Conectado correctamente a MongoDB Atlas")

if productos.count_documents({"nombre": "Leche"}) == 0:
    productos.insert_one({
        "nombre": "Leche",
        "precio": 32
    })
    print("Producto agregado")


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    contraseña = request.form["contraseña"]
    user = usuarios.find_one({
        "usuario": usuario,
        "contraseña": contraseña

    })
    if user:
        session["usuario"] = usuario
        return redirect("/gestor")

    else:
        return """
            <h2>Usuario o contraseña incorrectos</h2>
            <a href="/">
                Volver al login
            </a>
        """


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")


@app.route("/registro", methods=["GET", "POST"])
def registro():

    if request.method == "POST":

        nombre = request.form["nombre"]
        apellidos = request.form["apellidos"]
        dia = request.form["dia"]
        mes = request.form["mes"]
        año = request.form["año"]
        genero = request.form["genero"]

        correo = request.form["correo"]

        contraseña = request.form["contraseña"]

        usuario_existente = usuarios.find_one({
            "correo": correo
        })

        if usuario_existente:

            return "Ese correo ya existe"

        usuarios.insert_one({

            "nombre": nombre,
            "apellidos": apellidos,
            "dia": dia,
            "mes": mes,
            "año": año,
            "genero": genero,

            "correo": correo,

            "contraseña": contraseña
        })

        return redirect("/")

    return render_template("registro.html")


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":

        correo = request.form["correo"]

        user = usuarios.find_one({
            "correo": correo
        })

        if user:

            codigo = random.randint(100000, 999999)

            session["codigo_recuperacion"] = str(codigo)
            session["correo_recuperacion"] = correo

            mensaje = Message(
                "Recuperación de contraseña",
                sender=app.config['MAIL_USERNAME'],
                recipients=[correo]
            )

            mensaje.body = f"""
Tu código de recuperación es:

{codigo}
"""

            mail.send(mensaje)

            return redirect("/verificar")

        else:

            return """
                <h2>Correo no encontrado</h2>
                <a href="/recuperar">Intentar otra vez</a>
            """

    return render_template("recuperar.html")

@app.route("/verificar_codigo", methods=["GET", "POST"])
def verificar_codigo():

    if request.method == "POST":

        codigo = request.form["codigo"]

        if codigo == session.get("codigo_recuperacion"):

            return redirect("/nueva_password")

        else:

            return """
                <h2>Código incorrecto</h2>

                <a href="/verificar_codigo">
                    Intentar otra vez
                </a>
            """

    return render_template("verificar_codigo.html")

@app.route("/nueva_password", methods=["GET", "POST"])
def nueva_password():

    if request.method == "POST":

        nueva_password = request.form["nueva_password"]

        usuarios.update_one(
            {
                "correo": session["correo_recuperacion"]
            },
            {
                "$set": {
                    "contraseña": nueva_password
                }
            }
        )

        session.pop("codigo_recuperacion", None)
        session.pop("correo_recuperacion", None)

        return """
            <h2>Contraseña actualizada correctamente</h2>

            <a href="/">
                Iniciar sesión
            </a>
        """

    return render_template("nueva_password.html")


@app.route("/gestor")
def gestor():
    if "usuario" not in session:
        return redirect("/")
    lista_tareas = list(
        tareas_db.find({
            "usuario": session["usuario"]
        })
    )
    return render_template(
        "gestion_productos.html",
        tareas=lista_tareas,
        usuario=session["usuario"]
    )


@app.route("/agregar", methods=["POST"])
def agregar():
    if "usuario" not in session:
        return redirect("/")
    tarea = request.form["tarea"]

    if tarea:
        tareas_db.insert_one({
            "usuario": session["usuario"],
            "tarea": tarea
        })
    return redirect("/gestor")


@app.route("/eliminar/<id>")
def eliminar(id):
    if "usuario" not in session:
        return redirect("/")
    tareas_db.delete_one({
        "_id": ObjectId(id)
    })
    return redirect("/gestor")


if __name__ == "__main__":

    app.run(debug=True)