# TSP.py
from typing import List, Dict, Tuple

class TSP:
    def __init__(self, ciudades: Dict[str, Tuple], distancias: Dict):
        self.ciudades = ciudades
        self.distancias = distancias

    def _distancia_ruta(self, ruta: List[str]) -> float:
        total = 0
        n = len(ruta)
        for i in range(n):
            total += self.distancias[(ruta[i], ruta[(i+1) % n])]
        return total

    def nearest_neighbor(self, inicio: str = None) -> List[str]:
        """Heurística greedy O(n²) — buen punto de partida"""
        no_visitadas = list(self.ciudades.keys())
        inicio = inicio or no_visitadas[0]
        ruta = [inicio]
        no_visitadas.remove(inicio)

        while no_visitadas:
            actual = ruta[-1]
            siguiente = min(
                no_visitadas,
                key=lambda c: self.distancias[(actual, c)]
            )
            ruta.append(siguiente)
            no_visitadas.remove(siguiente)
        return ruta

    def two_opt(self, ruta: List[str], max_iter: int = 1000) -> List[str]:
        """Mejora local 2-opt — invierte segmentos para reducir cruces"""
        mejor = ruta[:]
        mejorado = True
        iteracion = 0

        while mejorado and iteracion < max_iter:
            mejorado = False
            iteracion += 1
            for i in range(1, len(mejor) - 1):
                for j in range(i + 1, len(mejor)):
                    nueva = mejor[:i] + mejor[i:j+1][::-1] + mejor[j+1:]
                    if self._distancia_ruta(nueva) < self._distancia_ruta(mejor):
                        mejor = nueva
                        mejorado = True
        return mejor

    def encontrar_la_ruta_mas_corta(self) -> List[str]:
        """Pipeline: Nearest Neighbor → 2-opt"""
        ruta_inicial = self.nearest_neighbor()
        ruta_optima  = self.two_opt(ruta_inicial)
        return ruta_optima

    def resultado_para_api(self, ruta: List[str]) -> dict:
        """Serializa para el frontend ArcGIS"""
        return {
            "ruta": ruta,
            "distancia_total_km": round(self._distancia_ruta(ruta), 2),
            "coordenadas": [
                {"nombre": c, "lon": self.ciudades[c][0], "lat": self.ciudades[c][1]}
                for c in ruta
            ]
        }