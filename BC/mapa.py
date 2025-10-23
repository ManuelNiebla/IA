"""
CSP para colorear mapa de Baja California - Versión corregida con OpenCV
"""

from collections import deque
import time
import cv2
import numpy as np
import os

VARIABLES = ["Tijuana", "Rosarito", "Tecate", "Ensenada",
             "Mexicali", "San Felipe", "San Quintin"]

CONSTRAINTS = [
    ("Ensenada", "Mexicali"),
    ("Ensenada", "Tecate"),
    ("Ensenada", "Tijuana"),
    ("Ensenada", "Rosarito"),
    ("Ensenada", "San Quintin"),
    ("Ensenada", "San Felipe"),
    ("Mexicali", "Ensenada"),
    ("Mexicali", "Tecate"),
    ("Mexicali", "San Felipe"),
    ("Tecate", "Ensenada"),
    ("Tecate", "Mexicali"),
    ("Tecate", "Tijuana"),
    ("Tijuana", "Ensenada"),
    ("Tijuana", "Tecate"),
    ("Tijuana", "Rosarito"),
    ("Rosarito", "Ensenada"),
    ("Rosarito", "Tijuana"),
    ("San Quintin", "Ensenada"),
    ("San Quintin", "San Felipe"),
    ("San Felipe", "Ensenada"),
    ("San Felipe", "Mexicali"),
    ("San Felipe", "San Quintin"),
]

COLORS = ["Verde", "Azul", "Amarillo"]

stats = {
    'steps': 0,
    'backtracks': 0,
    'assignments': 0
}

def build_neighbors():
    neighbors = {var: [] for var in VARIABLES}
    for (x, y) in CONSTRAINTS:
        if y not in neighbors[x]:
            neighbors[x].append(y)
        if x not in neighbors[y]:
            neighbors[y].append(x)
    return neighbors

NEIGHBORS = build_neighbors()

def initialize_domains():
    return {var: COLORS.copy() for var in VARIABLES}

def arc3(domains):
    queue = deque()
    for (x, y) in CONSTRAINTS:
        queue.append((x, y))
        queue.append((y, x))

    while queue:
        (xi, xj) = queue.popleft()
        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False
            for xk in NEIGHBORS[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def revise(domains, xi, xj):
    revised = False
    to_remove = []
    for x in domains[xi]:
        satisfies = False
        for y in domains[xj]:
            if x != y:
                satisfies = True
                break
        if not satisfies:
            to_remove.append(x)
            revised = True
    for val in to_remove:
        domains[xi].remove(val)
    return revised

def maintain_arc_consistency(var, value, assignment, domains):
    inferences = {}
    queue = deque()

    for neighbor in NEIGHBORS[var]:
        if neighbor not in assignment:
            queue.append((neighbor, var))

    while queue:
        (xi, xj) = queue.popleft()
        if revise_with_assignment(domains, xi, xj, assignment, inferences):
            if len(domains[xi]) == 0:
                return False
            for xk in NEIGHBORS[xi]:
                if xk != xj and xk not in assignment:
                    queue.append((xk, xi))

    return inferences

def revise_with_assignment(domains, xi, xj, assignment, inferences):
    revised = False
    to_remove = []
    for x in list(domains[xi]):
        satisfies = False
        if xj in assignment:
            if x != assignment[xj]:
                satisfies = True
        else:
            for y in domains[xj]:
                if x != y:
                    satisfies = True
                    break
        if not satisfies:
            to_remove.append(x)
            revised = True
    for val in to_remove:
        if val in domains[xi]:
            domains[xi].remove(val)
            if xi not in inferences:
                inferences[xi] = []
            inferences[xi].append(val)
    return revised

def select_unassigned_variable(assignment, heuristic="none", domains=None):
    unassigned = [v for v in VARIABLES if v not in assignment]
    if not unassigned:
        return None
    if heuristic == "none":
        return unassigned[0]
    elif heuristic == "mrv":
        return minimum_remaining_values(unassigned, assignment, domains)
    elif heuristic == "degree":
        return degree_heuristic(unassigned, assignment)
    return unassigned[0]

def minimum_remaining_values(unassigned, assignment, domains):
    def count_legal_values(var):
        count = 0
        for value in domains[var]:
            test_assignment = assignment.copy()
            test_assignment[var] = value
            if consistent(test_assignment):
                count += 1
        return count
    return min(unassigned, key=count_legal_values)

def degree_heuristic(unassigned, assignment):
    def count_unassigned_neighbors(var):
        return sum(1 for n in NEIGHBORS[var] if n not in assignment)
    return max(unassigned, key=count_unassigned_neighbors)

def order_domain_values(var, assignment, heuristic="none", domains=None):
    if heuristic == "none":
        return domains[var] if domains else COLORS
    elif heuristic == "lcv":
        return least_constraining_value(var, assignment, domains)
    return domains[var] if domains else COLORS

def least_constraining_value(var, assignment, domains):
    def count_conflicts(value):
        conflicts = 0
        for neighbor in NEIGHBORS[var]:
            if neighbor not in assignment:
                if value in domains[neighbor]:
                    conflicts += 1
        return conflicts
    return sorted(domains[var], key=count_conflicts)

def consistent(assignment):
    for (x, y) in CONSTRAINTS:
        if x not in assignment or y not in assignment:
            continue
        if assignment[x] == assignment[y]:
            return False
    return True

def backtrack(assignment, var_heuristic="none", val_heuristic="none", domains=None, use_mac=True):
    stats['steps'] += 1

    if len(assignment) == len(VARIABLES):
        return assignment

    var = select_unassigned_variable(assignment, var_heuristic, domains)

    values = order_domain_values(var, assignment, val_heuristic, domains)

    for value in list(values):
        stats['assignments'] += 1

        if not is_value_consistent_with_assignment(var, value, assignment):
            stats['backtracks'] += 1
            continue

        saved_domains = {v: domains[v].copy() for v in domains}

        assignment[var] = value

        inference_ok = True
        inferences = {}
        if use_mac:
            inferences = maintain_arc_consistency(var, value, assignment, domains)
            if inferences is False:
                inference_ok = False

        if inference_ok:
            result = backtrack(assignment, var_heuristic, val_heuristic, domains, use_mac)
            if result is not None:
                return result

        del assignment[var]

        for v in saved_domains:
            domains[v] = saved_domains[v]

        stats['backtracks'] += 1

    return None

def is_value_consistent_with_assignment(var, value, assignment):
    for neighbor in NEIGHBORS[var]:
        if neighbor in assignment and assignment[neighbor] == value:
            return False
    return True

def visualize_solution(solution, image_path, seed_points=None):
    """Colorea el mapa real de Baja California usando floodFill"""
    try:
        if not os.path.exists(image_path):
            print(f"Error: No se encontró la imagen en '{image_path}'")
            print("Asegúrate de tener el archivo 'mapa2.png' en la carpeta 'assets'")
            return

        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: No se pudo leer la imagen en '{image_path}'")
            return

        height, width = img.shape[:2]
        print(f"Imagen cargada: {width}x{height} píxeles")

        colored_img = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Colores BGR (OpenCV usa BGR, no RGB)
        color_map = {
            "Verde": (0, 255, 0),      # Verde brillante
            "Azul": (255, 0, 0),       # Azul brillante
            "Amarillo": (0, 255, 255)  # Amarillo brillante
        }

        # Puntos semilla para cada municipio (ajústalo según tu imagen)
        if seed_points is None:
            seed_points = {
                "Tijuana": [
                    (int(width * 0.08), int(height * 0.05)),
                    (int(width * 0.09), int(height * 0.08)),
                    (int(width * 0.10), int(height * 0.07)),
                ],
                "Rosarito": [
                    (int(width * 0.08), int(height * 0.12)),
                    (int(width * 0.09), int(height * 0.15)),
                    (int(width * 0.07), int(height * 0.14)),
                ],
                "Tecate": [
                    (int(width * 0.20), int(height * 0.08)),
                    (int(width * 0.22), int(height * 0.10)),
                    (int(width * 0.18), int(height * 0.09)),
                ],
                "Ensenada": [
                    (int(width * 0.12), int(height * 0.25)),
                    (int(width * 0.15), int(height * 0.30)),
                    (int(width * 0.10), int(height * 0.28)),
                    (int(width * 0.13), int(height * 0.35)),
                ],
                "Mexicali": [
                    (int(width * 0.40), int(height * 0.08)),
                    (int(width * 0.45), int(height * 0.10)),
                    (int(width * 0.42), int(height * 0.12)),
                    (int(width * 0.38), int(height * 0.11)),
                ],
                "San Felipe": [
                    (int(width * 0.45), int(height * 0.35)),
                    (int(width * 0.47), int(height * 0.38)),
                    (int(width * 0.43), int(height * 0.33)),
                ],
                "San Quintin": [
                    (int(width * 0.18), int(height * 0.60)),
                    (int(width * 0.20), int(height * 0.65)),
                    (int(width * 0.16), int(height * 0.62)),
                ]
            }

        print("\nColoreando regiones:")
        for region, color_name in solution.items():
            if region in seed_points:
                color = color_map.get(color_name, (0, 0, 0))
                points_colored = 0

                print(f"  {region} -> {color_name}", end=" ")

                for seed in seed_points[region]:
                    x, y = seed
                    if 0 <= x < width and 0 <= y < height:
                        # Verificar si el píxel es blanco (parte del mapa)
                        pixel_value = gray[y, x]
                        if pixel_value > 200:  # Píxel blanco
                            mask = np.zeros((height + 2, width + 2), np.uint8)
                            try:
                                cv2.floodFill(
                                    colored_img,
                                    mask,
                                    (x, y),
                                    color,
                                    loDiff=(30, 30, 30),
                                    upDiff=(30, 30, 30),
                                    flags=cv2.FLOODFILL_FIXED_RANGE
                                )
                                points_colored += 1
                            except Exception as e:
                                pass

                print(f"({points_colored} puntos aplicados)")

        output_path = os.path.splitext(image_path)[0] + "_coloreado.png"
        cv2.imwrite(output_path, colored_img)
        print(f"\n✓ Imagen guardada exitosamente: {output_path}")

    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        import traceback
        traceback.print_exc()

def solve_csp(algorithm="backtrack", var_heuristic="none", val_heuristic="none",
              use_arc3=False, use_mac=True, image_path=None):
    global stats
    stats = {'steps': 0, 'backtracks': 0, 'assignments': 0}

    print("="*60)
    print("RESOLVIENDO CSP - COLORACIÓN DE MAPA DE BAJA CALIFORNIA")
    print("="*60)

    domains = initialize_domains()

    if use_arc3:
        print("\n1. Aplicando AC-3 (Arc Consistency)...")
        start_arc3 = time.time()
        if not arc3(domains):
            print("   ✗ AC-3 detectó que no hay solución")
            return None
        end_arc3 = time.time()
        print(f"   ✓ AC-3 completado en {end_arc3 - start_arc3:.4f} segundos")
        print("\n   Dominios después de AC-3:")
        for var in VARIABLES:
            print(f"     {var}: {domains[var]}")

    print(f"\n2. Configuración del algoritmo:")
    print(f"   - Algoritmo: {algorithm}")
    print(f"   - Heurística de variables: {var_heuristic}")
    print(f"   - Heurística de valores: {val_heuristic}")
    print(f"   - AC-3 inicial: {use_arc3}")
    print(f"   - MAC (Maintaining Arc Consistency): {use_mac}")

    print("\n3. Iniciando búsqueda backtracking...")
    start_time = time.time()

    solution = backtrack(dict(), var_heuristic, val_heuristic, domains, use_mac)

    end_time = time.time()

    print("\n" + "="*60)
    if solution:
        print("✓ SOLUCIÓN ENCONTRADA!")
        print("="*60)
        print("\nAsignación de colores:")
        for city in VARIABLES:
            print(f"  {city:15} -> {solution[city]}")

        print(f"\nEstadísticas de ejecución:")
        print(f"  Pasos totales:        {stats['steps']}")
        print(f"  Retrocesos:           {stats['backtracks']}")
        print(f"  Asignaciones:         {stats['assignments']}")
        print(f"  Tiempo de búsqueda:   {end_time - start_time:.4f} segundos")

        # Verificar que la solución es consistente
        if consistent(solution):
            print("\n  ✓ La solución es consistente (ningún vecino tiene el mismo color)")

        if image_path:
            print("\n4. Generando imagen coloreada...")
            visualize_solution(solution, image_path)
    else:
        print("✗ NO SE ENCONTRÓ SOLUCIÓN")
        print("="*60)

    return solution

if __name__ == "__main__":
    # Obtener la ruta del directorio donde está este script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Ruta de la imagen - busca en el mismo directorio del script
    IMAGE_PATH = os.path.join(script_dir, "BC.png")

    # Intenta con diferentes rutas comunes
    if not os.path.exists(IMAGE_PATH):
        possible_paths = [
            os.path.join(script_dir, "assets", "BC.png"),
            os.path.join(script_dir, "..", "BC.png"),
            "BC.png",
            "assets/BC.png",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                IMAGE_PATH = path
                break

    if not os.path.exists(IMAGE_PATH):
        print(f"❌ ERROR: No se encontró la imagen 'BC.png'")
        print(f"\nRuta del script: {script_dir}")
        print(f"\nBuscando en: {IMAGE_PATH}")
        print("\nPor favor, coloca 'BC.png' en la misma carpeta que 'mapa.py'")
        print(f"Ruta actual de trabajo: {os.getcwd()}")

        # Intenta buscar el archivo en todo el directorio actual
        print("\n🔍 Buscando archivos .png en la carpeta actual...")
        for file in os.listdir(script_dir):
            if file.endswith('.png'):
                print(f"   Encontrado: {file}")
        exit(1)

    print(f"✓ Imagen encontrada en: {IMAGE_PATH}")

    solution = solve_csp(
        algorithm="backtrack",
        var_heuristic="mrv",       # Minimum Remaining Values
        val_heuristic="lcv",       # Least Constraining Value
        use_arc3=True,             # Usar AC-3 antes de buscar
        use_mac=True,              # Maintaining Arc Consistency
        image_path=IMAGE_PATH
    )

    if not solution:
        print("\n✗ No se encontró solución para colorear el mapa")