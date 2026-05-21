from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "panadero_con_el_pan"

url = "mongodb+srv://Angel17:171009Ang@clusrob1.xaujcjr.mongodb.net/"

cliente = MongoClient(url)

db = cliente["supermercado"]

usuarios = db["usuarios"]
tareas_db = db["tareas"]
productos = db["productos"]

print("Conectado correctamente a MongoDB")

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
        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        if not usuario or not contraseña:
            return "Completa todos los campos"
        usuario_existente = usuarios.find_one({
            "usuario": usuario
        })

        if usuario_existente:
            return """
                <h2>El usuario ya existe</h2>
                <a href="/registro">
                    Intentar nuevamente
                </a>
            """

        usuarios.insert_one({
            "nombre": nombre,
            "apellidos": apellidos,
            "dia": dia,
            "mes": mes,
            "año": año,
            "genero": genero,
            "usuario": usuario,
            "contraseña": contraseña
        })
        return redirect("/")
    return render_template("registro.html")


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        usuario = request.form["usuario"]
        user = usuarios.find_one({
            "usuario": usuario
        })
        if user:
            return f"""
                <h2>
                    Tu contraseña es:
                    {user['contraseña']}
                </h2>
                <a href="/">
                    Volver
                </a>
            """

        else:
            return """
                <h2>Usuario no encontrado</h2>
                <a href="/recuperar">
                    Intentar otra vez
                </a>
            """
    return render_template("recuperar.html")


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