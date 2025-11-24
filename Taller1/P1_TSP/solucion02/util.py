# --- FUNCIÓN AUXILIAR PARA IMPRESIÓN VISUAL ---
def imprimir_detalle_ruta(distancias, ruta, costo_total):
    print("\n" + "="*40)
    print("       RESULTADO DETALLADO TSP")
    print("="*40)
    
    # 1. Dibujo de flechas
    camino_visual = " -> ".join(map(str, ruta))
    print(f"\n🗺️  Ruta Óptima:  {camino_visual}")
    
    print("\n📉  Desglose de Costos:")
    print("-" * 30)
    
    acumulado = 0
    for i in range(len(ruta) - 1):
        origen = ruta[i]
        destino = ruta[i+1]
        peso = distancias[origen][destino]
        acumulado += peso
        print(f"   • De nodo {origen} a {destino}: \tCosto {peso}")
    
    print("-" * 30)
    print(f"✅  COSTO TOTAL: \t{acumulado}")
    
    # Verificación
    if acumulado == costo_total:
        print("   (Verificación correcta)")
    else:
        print("   (Error de verificación)")
    print("="*40 + "\n")
