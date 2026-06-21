# proyecto_propio/src/benchmark.py

import subprocess
import time
import csv
import os
import sys

# Agregar la ruta de las implementaciones de referencia
sys.path.append(os.path.join(os.path.dirname(__file__), 'E:\UNSAAC\Algoritmos Avansados\algoritmos-avanzados-sssp\proyecto_propio\src'))

def ejecutar_algoritmo(dataset, algoritmo='v2', repeticiones=3):
    """
    Ejecuta el algoritmo en un dataset y retorna los tiempos.
    
    Args:
        dataset: 'rome', 'google', 'livejournal'
        algoritmo: 'v1' (educativo), 'v2' (optimizado), 'dijkstra'
        repeticiones: número de veces a ejecutar
    
    Returns:
        dict: tiempos, distancia, nodos
    """
    resultados = {
        'tiempos': [],
        'distancias': [],
        'nodos': [],
        'errores': []
    }
    
    for i in range(repeticiones):
        print(f"  Ejecución {i+1}/{repeticiones}...")
        
        # Construir el comando
        cmd = ['python', 'main.py', '--data', dataset]
        
        if algoritmo.startswith('v'):
            cmd.extend(['--solver', algoritmo])
        
        # Ejecutar y capturar salida
        try:
            start = time.perf_counter()
            resultado = subprocess.run(
                cmd,
                cwd=os.path.join(os.path.dirname(__file__), '../../implementaciones_referencia/bmssp-python'),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos máximo
            )
            end = time.perf_counter()
            
            tiempo = end - start
            resultados['tiempos'].append(tiempo)
            
            # Extraer distancia y nodos de la salida
            if resultado.stdout:
                for linea in resultado.stdout.split('\n'):
                    if 'Distance =' in linea:
                        dist = float(linea.split('Distance =')[1].split(',')[0].strip())
                        resultados['distancias'].append(dist)
                    elif 'Path length =' in linea:
                        nodos = int(linea.split('Path length =')[1].split('nodes')[0].strip())
                        resultados['nodos'].append(nodos)
            
            print(f"    Tiempo: {tiempo:.4f}s")
            
        except subprocess.TimeoutExpired:
            resultados['errores'].append('Timeout')
            print(f"    ⚠️ Timeout")
        except Exception as e:
            resultados['errores'].append(str(e))
            print(f"    ❌ Error: {e}")
    
    return resultados

def guardar_resultados(dataset, resultados, algoritmo):
    """
    Guarda los resultados en un archivo CSV.
    
    Args:
        dataset: nombre del dataset
        resultados: diccionario con tiempos, distancias, nodos
        algoritmo: nombre del algoritmo
    """
    # Crear carpeta results si no existe
    os.makedirs('../results', exist_ok=True)
    
    filename = f'../results/{dataset}_{algoritmo}.csv'
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Dataset', 'Algoritmo', 'Ejecucion', 'Tiempo(s)', 'Distancia', 'Nodos', 'Error'])
        
        for i in range(len(resultados['tiempos'])):
            writer.writerow([
                dataset,
                algoritmo,
                i+1,
                f"{resultados['tiempos'][i]:.4f}",
                resultados['distancias'][i] if i < len(resultados['distancias']) else 'N/A',
                resultados['nodos'][i] if i < len(resultados['nodos']) else 'N/A',
                resultados['errores'][i] if i < len(resultados['errores']) else ''
            ])
    
    print(f"✅ Resultados guardados en {filename}")

def main():
    """Función principal que ejecuta todas las pruebas."""
    
    # Configuración
    datasets = ['rome', 'google', 'livejournal']
    algoritmos = ['v1', 'v2', 'dijkstra']
    repeticiones = 3
    
    print("=" * 60)
    print("BENCHMARK: Dijkstra vs BMSSP")
    print("=" * 60)
    print(f"Datasets: {datasets}")
    print(f"Algoritmos: {algoritmos}")
    print(f"Repeticiones por prueba: {repeticiones}")
    print("=" * 60)
    
    resultados_totales = []
    
    for dataset in datasets:
        for algoritmo in algoritmos:
            print(f"\n📊 Probando {algoritmo} en {dataset}...")
            
            resultados = ejecutar_algoritmo(dataset, algoritmo, repeticiones)
            
            if resultados['tiempos']:
                guardar_resultados(dataset, resultados, algoritmo)
                
                # Guardar resumen
                tiempo_promedio = sum(resultados['tiempos']) / len(resultados['tiempos'])
                resultados_totales.append({
                    'dataset': dataset,
                    'algoritmo': algoritmo,
                    'promedio': tiempo_promedio,
                    'min': min(resultados['tiempos']),
                    'max': max(resultados['tiempos']),
                    'distancia': resultados['distancias'][0] if resultados['distancias'] else 'N/A',
                    'nodos': resultados['nodos'][0] if resultados['nodos'] else 'N/A'
                })
    
    # Guardar resumen general
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    
    with open('../results/resumen_general.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Dataset', 'Algoritmo', 'Promedio(s)', 'Min(s)', 'Max(s)', 'Distancia', 'Nodos'])
        for r in resultados_totales:
            writer.writerow([
                r['dataset'],
                r['algoritmo'],
                f"{r['promedio']:.4f}",
                f"{r['min']:.4f}",
                f"{r['max']:.4f}",
                r['distancia'],
                r['nodos']
            ])
            print(f"{r['dataset']:15} {r['algoritmo']:10} {r['promedio']:.4f}s")
    
    print("\n✅ Todos los resultados guardados en carpeta 'results/'")
    print("=" * 60)

if __name__ == "__main__":
    main()