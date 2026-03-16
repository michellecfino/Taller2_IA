from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from algorithms.problems_csp import DroneAssignmentCSP


def backtracking_search(csp: DroneAssignmentCSP) -> dict[str, str] | None:
    """
    Basic backtracking search without optimizations.

    Tips:
    - An assignment is a dictionary mapping variables to values (e.g. {X1: Cell(1,2), X2: Cell(3,4)}).
    - Use csp.assign(var, value, assignment) to assign a value to a variable.
    - Use csp.unassign(var, assignment) to unassign a variable.
    - Use csp.is_consistent(var, value, assignment) to check if an assignment is consistent with the constraints.
    - Use csp.is_complete(assignment) to check if the assignment is complete (all variables assigned).
    - Use csp.get_unassigned_variables(assignment) to get a list of unassigned variables.
    - Use csp.domains[var] to get the list of possible values for a variable.
    - Use csp.get_neighbors(var) to get the list of variables that share a constraint with var.
    - Add logs to measure how good your implementation is (e.g. number of assignments, backtracks).

    You can find inspiration in the textbook's pseudocode:
    Artificial Intelligence: A Modern Approach (4th Edition) by Russell and Norvig, Chapter 5: Constraint Satisfaction Problems
    """
    # TODO: Implement your code here
    #Pongo este contador para poder mostrar estadísticas chéveres para el informe:D
    contador = {"Decisión":0}
    
    #Pongo esto aquí para hacerlo recursivo :p
    def solucion(diccionario):
        if csp.is_complete(diccionario):
            print(f"🐮🌿[Backtracking Simple] Total de asignaciones: {contador['Decisión']}")
            return diccionario
        seleccionada = csp.get_unassigned_variables(diccionario)[0]

        for valor in csp.domains[seleccionada]:
            contador["Decisión"] += 1
            if csp.is_consistent(seleccionada, valor, diccionario):
                csp.assign(seleccionada,valor, diccionario)
                #aquí nos ponemos recursivos jiji
                resultado = solucion(diccionario)
                if resultado is not None:
                    return resultado
                csp.unassign(seleccionada, diccionario)

        return None
    return solucion({})



def backtracking_fc(csp: DroneAssignmentCSP) -> dict[str, str] | None:
    """
    Backtracking search with Forward Checking.

    Tips:
    - Forward checking: After assigning a value to a variable, eliminate inconsistent values from
      the domains of unassigned neighbors. If any neighbor's domain becomes empty, backtrack immediately.
    - Save domains before forward checking so you can restore them on backtrack.
    - Use csp.get_neighbors(var) to get variables that share constraints with var.
    - Use csp.is_consistent(neighbor, val, assignment) to check if a value is still consistent.
    - Forward checking reduces the search space by detecting failures earlier than basic backtracking.
    """
    # TODO: Implement your code here
    contador = {"Decisión":0}
    def solucion_fc(diccionario):
        if csp.is_complete(diccionario):
            print(f"🐮🌿[Forward Checking] Total de asignaciones: {contador['Decisión']}")
            return diccionario
        
        seleccionada = csp.get_unassigned_variables(diccionario)[0]

        for valor in csp.domains[seleccionada]:
            contador["Decisión"] += 1
            if csp.is_consistent(seleccionada, valor, diccionario):
                csp.assign(seleccionada, valor, diccionario)

                viejos_dominios = {v: list(csp.domains[v]) for v in csp.domains}

                poda_exitosa = True
                for vecino in csp.get_neighbors(seleccionada):
                    if vecino not in diccionario:
                        for v_valor in list(csp.domains[vecino]):
                            if not csp.is_consistent(vecino, v_valor, diccionario):
                                csp.domains[vecino].remove(v_valor)
                        
                        if not csp.domains[vecino]:
                            poda_exitosa = False
                            break
                if poda_exitosa:
                    resultado = solucion_fc(diccionario)
                    if resultado is not None:
                        return resultado

                csp.domains = viejos_dominios
                csp.unassign(seleccionada, diccionario)

        return None
    return solucion_fc({})


def backtracking_ac3(csp: DroneAssignmentCSP) -> dict[str, str] | None:
    """
    Backtracking search with AC-3 arc consistency.

    Tips:
    - AC-3 enforces arc consistency: for every pair of constrained variables (Xi, Xj), every value
      in Xi's domain must have at least one supporting value in Xj's domain.
    - Run AC-3 before starting backtracking to reduce domains globally.
    - After each assignment, run AC-3 on arcs involving the assigned variable's neighbors.
    - If AC-3 empties any domain, the current assignment is inconsistent - backtrack.
    - You can create helper functions such as:
      - a values_compatible function to check if two variable-value pairs are consistent with the constraints.
      - a revise function that removes unsupported values from one variable's domain.
      - an ac3 function that manages the queue of arcs to check and calls revise.
      - a backtrack function that integrates AC-3 into the search process.
    """
    # TODO: Implement your code here
    contador = {"Decisión":0}
    def ac3(assignment, queue):
        """Algoritmo AC-3 para mantener consistencia de arco."""
        while queue:
            (xi, xj) = queue.pop(0)
            revised = False
            for x_val in list(csp.domains[xi]):
                """
                if not any(csp.is_consistent(xi, x_val, {**assignment, xj: y_val}) for y_val in csp.domains[xj]):
                    csp.domains[xi].remove(x_val)
                    revised = True
                    """
            
            if revised:
                if not csp.domains[xi]:
                    return False
                for xk in csp.get_neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def solucion_ac3(assignment):
        if csp.is_complete(assignment):
            print(f"🐮🌿 [AC-3] Total de asignaciones: {contador['Decisión']}")
            return assignment
        
        var = csp.get_unassigned_variables(assignment)[0]

        for valor in csp.domains[var]:
            contador["Decisión"] += 1
            if csp.is_consistent(var, valor, assignment):
                csp.assign(var, valor, assignment)
                old_domains = {v: list(csp.domains[v]) for v in csp.domains}
                
                csp.domains[var] = [valor]
                queue = [(neighbor, var) for neighbor in csp.get_neighbors(var) if neighbor not in assignment]
                
                if ac3(assignment, queue):
                    resultado = solucion_ac3(assignment)
                    if resultado is not None:
                        return resultado

                csp.domains = old_domains
                csp.unassign(var, assignment)
        return None

    initial_queue = [(v, n) for v in csp.domains for n in csp.get_neighbors(v)]
    if not ac3({}, initial_queue):
        print(f"[AC-3] Falló en consistencia inicial.")
        return None
        
    return solucion_ac3({})


    return None


def backtracking_mrv_lcv(csp: DroneAssignmentCSP) -> dict[str, str] | None:
    """
    Backtracking with Forward Checking + MRV + LCV.

    Tips:
    - Combine the techniques from backtracking_fc, mrv_heuristic, and lcv_heuristic.
    - MRV (Minimum Remaining Values): Select the unassigned variable with the fewest legal values.
      Tie-break by degree: prefer the variable with the most unassigned neighbors.
    - LCV (Least Constraining Value): When ordering values for a variable, prefer
      values that rule out the fewest choices for neighboring variables.
    - Use csp.get_num_conflicts(var, value, assignment) to count how many values would be ruled out for neighbors if var=value is assigned.
    """
    # TODO: Implement your code here (BONUS)
    contador = {"Decisión":0}

    def get_mrv_variable(assignment):
        
        unassigned = csp.get_unassigned_variables(assignment)
        return min(unassigned, key=lambda v: (len(csp.domains[v]), -len(csp.get_neighbors(v))))

    def get_lcv_ordered_values(var, assignment):
        return sorted(csp.domains[var], key=lambda val: csp.get_num_conflicts(var, val, assignment))

    def solucion_mrv_lcv(assignment):
        if csp.is_complete(assignment):
            print(f"🐮🌿 [MRV+LCV] Total de asignaciones: {contador['Decisión']}")
            return assignment
        
        var = get_mrv_variable(assignment)

        for valor in get_lcv_ordered_values(var, assignment):
            contador["Decisión"] += 1
            if csp.is_consistent(var, valor, assignment):
                csp.assign(var, valor, assignment)
                old_domains = {v: list(csp.domains[v]) for v in csp.domains}
                
                poda_exitosa = True
                for vecino in csp.get_neighbors(var):
                    if vecino not in assignment:
                        for v_val in list(csp.domains[vecino]):
                            if not csp.is_consistent(vecino, v_val, assignment):
                                csp.domains[vecino].remove(v_val)
                        if not csp.domains[vecino]:
                            poda_exitosa = False
                            break
                
                if poda_exitosa:
                    resultado = solucion_mrv_lcv(assignment)
                    if resultado is not None:
                        return resultado

                csp.domains = old_domains
                csp.unassign(var, assignment)
            return None
    final_assignment = solucion_mrv_lcv({})

    if final_assignment:
        print(f"Sí hay solución 🐮🌿")
    else:
        print(f"No hay solución 🐮🥩 ")
        print(f"Total de asignaciones intentadas: {contador['Decisión']}")
            
    return final_assignment    

