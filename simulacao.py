"""Simulação em terminal de agentes aspirador de pó.

Uso:
    python simulacao.py <tipo_agente> [seed]

Tipos aceitos:
    "Agente Simples"    ou  reflexo_simples
    "Agente com Modelo" ou  reflexo_com_modelo
"""
import os
import random
import sys
import time
from collections import deque

from agents import (
    DIRT,
    OBSTACLE,
    ModelBasedReflexAgent,
    SimpleReflexAgent,
    VacuumEnvironment,
)

# Mapeamento: argumento da CLI -> classe do agente
AGENTES = {
    "Agente Simples": SimpleReflexAgent,
    "Agente com Modelo": ModelBasedReflexAgent,
}

# Símbolos exibidos no terminal
SIMBOLO_LIMPO = "_"
SIMBOLO_SUJEIRA = "S"
SIMBOLO_OBSTACULO = "O"
SIMBOLO_AGENTE = "R"

# Parâmetros da simulação
LINHAS, COLUNAS = 6, 6
INTERVALO_MS = 500  # pausa entre iterações, em milissegundos
MAX_PASSOS = 500


def reachable_cells(rows, cols, obstacle_cells, start):
    """Células alcançáveis a partir de 'start' (BFS), respeitando obstáculos."""
    obstaculos = set(obstacle_cells)
    visitadas = {start}
    fila = deque([start])
    while fila:
        r, c = fila.popleft()
        for dr, dc in VacuumEnvironment.MOVES.values():
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in obstaculos and (nr, nc) not in visitadas):
                visitadas.add((nr, nc))
                fila.append((nr, nc))
    return visitadas


def generate_configs(rows, cols, n_configs, dirt_ratio=0.3, obstacle_ratio=0.15, seed=0):
    """
    Gera várias configurações iniciais (sujeira, obstáculos, posição do agente).
    A sujeira é sempre colocada apenas em células alcançáveis pelo agente,
    garantindo que o ambiente possa ser totalmente limpo.
    """
    rng = random.Random(seed)
    todas_as_celulas = [(r, c) for r in range(rows) for c in range(cols)]
    configs = []

    for _ in range(n_configs):
        celulas = todas_as_celulas.copy()
        rng.shuffle(celulas)

        n_obs = int(len(celulas) * obstacle_ratio)
        obstacle_cells = celulas[:n_obs]
        agent_pos = celulas[n_obs]  # primeira célula livre

        alcancaveis = sorted(reachable_cells(rows, cols, obstacle_cells, agent_pos))
        n_dirt = max(1, int(len(alcancaveis) * dirt_ratio))
        dirt_cells = rng.sample(alcancaveis, n_dirt)

        configs.append({
            "dirt_cells": dirt_cells,
            "obstacle_cells": obstacle_cells,
            "agent_pos": agent_pos,
        })
    return configs


def criar_ambiente(seed=None):
    """Gera uma configuração aleatória e cria o ambiente correspondente."""
    cfg = generate_configs(LINHAS, COLUNAS, 1, seed=seed)[0]
    return VacuumEnvironment(
        LINHAS, COLUNAS,
        cfg["dirt_cells"], cfg["obstacle_cells"], cfg["agent_pos"],
    )


def limpar_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def renderizar(env, passo):
    """Limpa o terminal e imprime a matriz atualizada."""
    limpar_terminal()
    print(f"Passo {passo}\n")
    for r in range(env.rows):
        linha = []
        for c in range(env.cols):
            if (r, c) == env.agent_pos:
                linha.append(SIMBOLO_AGENTE)
            elif env.grid[r, c] == DIRT:
                linha.append(SIMBOLO_SUJEIRA)
            elif env.grid[r, c] == OBSTACLE:
                linha.append(SIMBOLO_OBSTACULO)
            else:
                linha.append(SIMBOLO_LIMPO)
        print(" ".join(linha))
    print(f"\nSujeira restante: {env.dirt_count()}")


def simular(classe_agente, seed=None):
    env = criar_ambiente(seed)
    agente = classe_agente()
    passo = 0

    renderizar(env, passo)
    # Encerra quando não houver sujeira ou ao atingir o limite de passos
    while not env.is_clean() and passo < MAX_PASSOS:
        time.sleep(INTERVALO_MS / 1000)
        acao = agente.act(env.percept())
        env.step(acao)
        passo += 1
        renderizar(env, passo)

    print("\nAmbiente limpo." if env.is_clean() else "\nLimite de passos atingido.")


def main():
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in AGENTES:
        opcoes = ", ".join(f'"{nome}"' for nome in AGENTES)
        sys.exit(f"Uso: python simulacao.py <tipo_agente> [seed]\nTipos: {opcoes}")
    seed = int(sys.argv[2]) if len(sys.argv) == 3 else None
    simular(AGENTES[sys.argv[1]], seed)


if __name__ == "__main__":
    main()
