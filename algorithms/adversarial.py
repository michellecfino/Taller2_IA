from __future__ import annotations

import random
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

import algorithms.evaluation as evaluation
from world.game import Agent, Directions

if TYPE_CHECKING:
    from world.game_state import GameState


class MultiAgentSearchAgent(Agent, ABC):
    """
    Base class for multi-agent search agents (Minimax, AlphaBeta, Expectimax).
    """

    def __init__(self, depth: str = "2", _index: int = 0, prob: str = "0.0") -> None:
        self.index = 0  # Drone is always agent 0
        self.depth = int(depth)
        self.prob = float(
            prob
        )  # Probability that each hunter acts randomly (0=greedy, 1=random)
        self.evaluation_function = evaluation.evaluation_function

    @abstractmethod
    def get_action(self, state: GameState) -> Directions | None:
        """
        Returns the best action for the drone from the current GameState.
        """
        contador = {"Decisión":0}
        movimientosValidos = state.get_legal_actions(0)
        if not movimientosValidos:
            return None
        mejorValor = -float("-inf")
        mejorAccion = None

        for accion in movimientosValidos:
            succesor = state.generate_successor(0, accion)
            

        pass


class RandomAgent(MultiAgentSearchAgent):
    """
    Agent that chooses a legal action uniformly at random.
    """

    def get_action(self, state: GameState) -> Directions | None:
        """
        Get a random legal action for the drone.
        """
        legal_actions = state.get_legal_actions(self.index)
        return random.choice(legal_actions) if legal_actions else None


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Minimax agent for the drone (MAX) vs hunters (MIN) game.
    """

    def get_action(self, state: GameState) -> Directions | None:
        """
        Returns the best action for the drone using minimax.

        Tips:
        - The game tree alternates: drone (MAX) -> hunter1 (MIN) -> hunter2 (MIN) -> ... -> drone (MAX) -> ...
        - Use self.depth to control the search depth. depth=1 means the drone moves once and each hunter moves once.
        - Use state.get_legal_actions(agent_index) to get legal actions for a specific agent.
        - Use state.generate_successor(agent_index, action) to get the successor state after an action.
        - Use state.is_win() and state.is_lose() to check terminal states.
        - Use state.get_num_agents() to get the total number of agents.
        - Use self.evaluation_function(state) to evaluate leaf/terminal states.
        - The next agent is (agent_index + 1) % num_agents. Depth decreases after all agents have moved (full ply).
        - Return the ACTION (not the value) that maximizes the minimax value for the drone.
        """
        # TODO: Implement your code here

        contador = {"Decisión":0}
        profundidadInicial = self.depth
        evaluacionFinal = self.evaluation_function
        numAgentes = state.get_num_agents()

        def minMaxRecursivo(estado, agente, d):

            contador["Decisión"] += 1

            if d == 0 or estado.is_win() or estado.is_lose():
                # Added: pequeño ruido para romper empates en estados con mismo valor
                return evaluacionFinal(estado) + random.uniform(-0.0001, 0.0001)

            proximo = (agente + 1) % numAgentes
            nuevaProfundidad = d - 1 if proximo == 0 else d
            acciones = estado.get_legal_actions(agente)

            if not acciones:
                return evaluacionFinal(estado)
            
            sucesoresEstados = [
                minMaxRecursivo(
                    estado.generate_successor(agente, accion),
                    proximo,
                    nuevaProfundidad
                )
                for accion in acciones
            ]

            return max(sucesoresEstados) if agente == 0 else min(sucesoresEstados)
            
        accionesDron = state.get_legal_actions(0)

        if not accionesDron:
            return None
        
        accionesDron = state.get_legal_actions(0)

        if not accionesDron:
            return None
        
        # Added: romper simetría del árbol de búsqueda
        random.shuffle(accionesDron)

        mejorValor = -float('inf')
        mejorAccion = None

        for accion in accionesDron:

            sucesor = state.generate_successor(0, accion)
            
            valorActual = minMaxRecursivo(sucesor, 1, profundidadInicial)
            
            if valorActual > mejorValor:
                mejorValor = valorActual
                mejorAccion = accion

        return mejorAccion
    

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Alpha-Beta pruning agent. Same as Minimax but with alpha-beta pruning.
    MAX node: prune when value > beta (strict).
    MIN node: prune when value < alpha (strict).
    """

    def get_action(self, state: GameState) -> Directions | None:
        """
        Returns the best action for the drone using alpha-beta pruning.

        Tips:
        - Same structure as MinimaxAgent, but with alpha-beta pruning.
        - Alpha: best value MAX can guarantee (initially -inf).
        - Beta: best value MIN can guarantee (initially +inf).
        - MAX node: prune when value > beta (strict inequality, do NOT prune on equality).
        - MIN node: prune when value < alpha (strict inequality, do NOT prune on equality).
        - Update alpha at MAX nodes: alpha = max(alpha, value).
        - Update beta at MIN nodes: beta = min(beta, value).
        - Pass alpha and beta through the recursive calls.
        """
        # TODO: Implement your code here (BONUS)
        if state.is_win() or state.is_lose():
            return None

        profundidadInicial = self.depth
        evaluacionFinal = self.evaluation_function
        numAgentes = state.get_num_agents()
        
        def alphaBetaRecursivo(estado, agente, d, alpha, beta):
            # Caso base
            if d == 0 or estado.is_win() or estado.is_lose():
                if estado.is_win():
                    return 1000.0
                if estado.is_lose():
                    return -1000.0
                return evaluacionFinal(estado)
            
            # Determinar siguiente agente y profundidad
            proximo = (agente + 1) % numAgentes
            nuevaProfundidad = d - 1 if proximo == 0 else d
            acciones = estado.get_legal_actions(agente)
            
            if not acciones:
                return evaluacionFinal(estado)
            
            if agente == 0:  # MAX (dron)
                valor = -float('inf')
                for accion in acciones:
                    sucesor = estado.generate_successor(agente, accion)
                    valor = max(valor, alphaBetaRecursivo(sucesor, proximo, nuevaProfundidad, alpha, beta))
                    if valor > beta:  # Poda (strict)
                        return valor
                    alpha = max(alpha, valor)
                return valor
            else:  # MIN (cazadores)
                valor = float('inf')
                for accion in acciones:
                    sucesor = estado.generate_successor(agente, accion)
                    valor = min(valor, alphaBetaRecursivo(sucesor, proximo, nuevaProfundidad, alpha, beta))
                    if valor < alpha:  # Poda (strict)
                        return valor
                    beta = min(beta, valor)
                return valor
        
        # Encontrar mejor acción para el dron
        accionesDron = state.get_legal_actions(0)
        if not accionesDron:
            return None
        
        mejorValor = -float('inf')
        mejorAccion = None
        alpha = -float('inf')
        beta = float('inf')
        
        print(f"Evaluando acciones con Alpha-Beta (profundidad {profundidadInicial})...")
        
        for accion in accionesDron:
            sucesor = state.generate_successor(0, accion)
            valorActual = alphaBetaRecursivo(sucesor, 1, profundidadInicial, alpha, beta)
            
            print(f"  {accion}: {valorActual:.2f}")
            
            if valorActual > mejorValor:
                mejorValor = valorActual
                mejorAccion = accion
            
            alpha = max(alpha, mejorValor)
        
        print(f"Mejor acción: {mejorAccion} (valor: {mejorValor:.2f})")
        return mejorAccion

        return None


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    Expectimax agent with a mixed hunter model.

    Each hunter acts randomly with probability self.prob and greedily
    (worst-case / MIN) with probability 1 - self.prob.

    * When prob = 0:  behaves like Minimax (hunters always play optimally).
    * When prob = 1:  pure expectimax (hunters always play uniformly at random).
    * When 0 < prob < 1: weighted combination that correctly models the
      actual MixedHunterAgent used at game-play time.

    Chance node formula:
        value = (1 - p) * min(child_values) + p * mean(child_values)
    """

    def get_action(self, state: GameState) -> Directions | None:
        """
        Returns the best action for the drone using expectimax with mixed hunter model.

        Tips:
        - Drone nodes are MAX (same as Minimax).
        - Hunter nodes are CHANCE with mixed model: the hunter acts greedily with
          probability (1 - self.prob) and uniformly at random with probability self.prob.
        - Mixed expected value = (1-p) * min(child_values) + p * mean(child_values).
        - When p=0 this reduces to Minimax; when p=1 it is pure uniform expectimax.
        - Do NOT prune in expectimax (unlike alpha-beta).
        - self.prob is set via the constructor argument prob.
        """
        # TODO: Implement your code here

        if state.is_win() or state.is_lose():
            return None

        best_action = None
        max_v = float('-inf')
        legal_actions = state.get_legal_actions(0)

        for action in legal_actions:
            successor = state.generate_successor(0, action)
            
            if successor.is_win():
                return action
            
            v = self.expectimax_value(successor, 1, 0)
            
            if v > max_v:
                max_v = v
                best_action = action
                
        return best_action

    def expectimax_value(self, state, agent_index, depth):
        """
        Función recursiva única que maneja tanto los turnos MAX (dron) como los CHANCE (cazadores).
        """
        
        if state.is_win() or state.is_lose() or depth == self.depth:
            return self.evaluation_function(state)

        legal_actions = state.get_legal_actions(agent_index)
        if not legal_actions:
            return self.evaluation_function(state)

        num_agents = state.get_num_agents()
        next_agent = agent_index + 1
        next_depth = depth
        
        if next_agent >= num_agents:
            next_agent = 0
            next_depth += 1

        child_values = []
        for action in legal_actions:
            successor = state.generate_successor(agent_index, action)
            child_values.append(self.expectimax_value(successor, next_agent, next_depth))

        
        if agent_index == 0:
            return max(child_values)
            
        
        else:
            min_val = min(child_values)
            mean_val = sum(child_values) / len(child_values)
            return (1 - self.prob) * min_val + self.prob * mean_val