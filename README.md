<img src="/Taller1/images/usfq-red.png" alt="Alt Text" width="400">

# WorkShop-USFQ
## Inteligencia artificial

- **Nombre del grupo**: Grupo 3
- **Integrantes del grupo**:
  - Cristian Calderon (ej 3)
  - Juan Pazmino (ej 1)
  - Wilson Lopez (ej 2)

## Resumen
### Taller 1

### TSP Travelling salesman problem – Problema del vendedor viajante

- **Algoritmo Principal:** 2-OPT.
- **Concepto:** El 2-OPT es un algoritmo de búsqueda local diseñado para optimizar rutas. Funciona mediante intercambios iterativos de aristas, buscando eliminar cruces en la ruta hasta alcanzar una solución localmente óptima (heurística).
- **Desafío del TSP:** Encontrar la ruta más corta (solución globalmente óptima) se vuelve computacionalmente inviable a medida que el número de ciudades aumenta (ej. hasta 100 ciudades), justificando el uso de heurísticas como 2-OPT.
    
    ### Funcionamiento del Algoritmo 2-Opt
    El 2-Opt optimiza rutas a través de **intercambios iterativos**, eliminando cruces y desorden en el camino.

  1.  **Comenzar:** Se inicia con una ruta inicial arbitraria.
  2.  **Buscar Cruces:** Se escanea la ruta en busca de dos segmentos ($A \rightarrow B$ y $C \rightarrow D$) que puedan ser intercambiados.
  3.  **Verificar:** Se comprueba si reemplazar las conexiones por ($A \rightarrow C$ y $B \rightarrow D$) resulta en una distancia total más corta.
  4.  **Invertir:** Si se encuentra una mejora, se **invierte el segmento** del camino entre los dos puntos de intercambio para acortar la ruta.
  5.  **Repetir:** El proceso se repite hasta que no se encuentra ningún intercambio adicional que mejore la ruta, alcanzando un **óptimo local**.


### **P2 El acertijo del granjero y el bote**

### **P3 La torre de Hanoi**


### Planificación del proyecto

La planificación del proyecto se encuentra siguiendo el [Link a Notion](https://www.notion.so/juanpin/2babb7e62c6e808faae8cf13f1051af5?v=2babb7e62c6e81c0b7c1000c4df51a33&source=copy_link)




