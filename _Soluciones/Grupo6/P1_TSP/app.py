# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from TSP import TSP
from utils import generar_distancias_geo

app = Flask(__name__)
CORS(app)

@app.route("/solve-tsp", methods=["POST"])
def solve_tsp():
    """
    Recibe: {"ciudades": {"Quito": [-78.5, -0.22], "Guayaquil": [-79.9, -2.15], ...}}
    Retorna: ruta ordenada + distancia total en km
    """
    data = request.json
    ciudades = {k: tuple(v) for k, v in data["ciudades"].items()}
    distancias = generar_distancias_geo(ciudades)
    tsp = TSP(ciudades, distancias)
    ruta = tsp.encontrar_la_ruta_mas_corta()
    return jsonify(tsp.resultado_para_api(ruta))

if __name__ == "__main__":
    app.run(debug=True, port=5000)