from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import session

app = Flask(__name__)

app.secret_key = "panadero_con_el_pan"

client = MongoClient("mongodb://localhost:27017/")
db = client["mi_app"]
usuarios = db["usuarios"]
tareas_db = db["tareas"]

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
        session["usuario"] = usuario  # 🔥 GUARDAR SESIÓN
        return redirect("/tareas")
    else:
        return "Datos incorrectos"

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect("/")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]

        if not usuario or not contraseña:
            return "Completa todos los campos"

        if usuarios.find_one({"usuario": usuario}):
            return "El usuario ya existe"

        usuarios.insert_one({
            "usuario": usuario,
            "contraseña": contraseña
        })

        return redirect("/")

    return render_template("registro.html")

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        usuario = request.form["usuario"]

        user = usuarios.find_one({"usuario": usuario})

        if user:
            return f"Tu contraseña es: {user['contraseña']}"
        else:
            return "Usuario no encontrado"

    return render_template("recuperar.html")

@app.route("/tareas")
def tareas():
    if "usuario" not in session:
        return redirect("/")

    lista_tareas = list(tareas_db.find({"usuario": session["usuario"]}))
    return render_template("tareas.html", tareas=lista_tareas)


@app.route("/eliminar/<id>")
def eliminar(id):
    tareas_db.delete_one({"_id": ObjectId(id)})
    return redirect("/tareas")

@app.route("/agregar", methods=["POST"])
def agregar():
    if "usuario" not in session:
        return redirect("/")

    tarea = request.form["tarea"]

    tareas_db.insert_one({
        "usuario": session["usuario"],
        "tarea": tarea
    })

    return redirect("/tareas")

if __name__ == "__main__":
    app.run(debug=True)