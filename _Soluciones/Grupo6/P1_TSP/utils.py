# utils.py — versión geoespacial
import math

def haversine(coord1, coord2):
    """Distancia real en km entre dos puntos (lon, lat)"""
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371  # Radio de la Tierra en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def generar_distancias_geo(ciudades: dict) -> dict:
    """ciudades = {nombre: (lon, lat)}"""
    distancias = {}
    for c1, coord1 in ciudades.items():
        for c2, coord2 in ciudades.items():
            if c1 != c2:
                distancias[(c1, c2)] = haversine(coord1, coord2)
    return distancias