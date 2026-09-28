import random

import numpy as np

EMPTY = 0
DIRT = 1
OBSTACLE = 2

class VacuumEnvironment:
    """
    Ambiente de grade determinístico e parcialmente observável.
    O agente NÃO conhece de antemão o tamanho/limites do grid, a posição
    dos obstáculos nem a distribuição inicial de sujeira. A cada passo,
    ele só percebe: (1) se a célula em que está é suja e (2) se a última
    tentativa de movimento bateu em um obstáculo ou no limite do grid.
    """

    ACTIONS = ["Suck", "Up", "Down", "Left", "Right", "NoOp"]
    MOVES = {
        "Up": (-1, 0),
        "Down": (1, 0),
        "Left": (0, -1),
        "Right": (0, 1),
    }

    def __init__(self, rows, cols, dirt_cells, obstacle_cells, agent_pos):
        self.rows = rows
        self.cols = cols
        self.grid = np.full((rows, cols), EMPTY, dtype=int)
        for (r, c) in obstacle_cells:
            self.grid[r, c] = OBSTACLE
        for (r, c) in dirt_cells:
            if self.grid[r, c] != OBSTACLE:
                self.grid[r, c] = DIRT
        self.agent_pos = agent_pos
        self.bumped = False  # resultado da última tentativa de movimento

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def percept(self):
        """Percepção local: sujeira na célula atual e se houve colisão."""
        r, c = self.agent_pos
        dirty = self.grid[r, c] == DIRT
        return {"dirty": dirty, "bump": self.bumped}

    def step(self, action):
        """
        Executa a ação do agente e atualiza o estado do ambiente.
        Retorna (moved, cleaned):
          moved   -> True se houve um movimento efetivo (custo de movimento)
          cleaned -> True se a ação limpou um quadrado que estava sujo
        """
        self.bumped = False
        moved = False
        cleaned = False
        r, c = self.agent_pos

        if action == "Suck":
            if self.grid[r, c] == DIRT:
                self.grid[r, c] = EMPTY
                cleaned = True
        elif action in self.MOVES:
            dr, dc = self.MOVES[action]
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc) and self.grid[nr, nc] != OBSTACLE:
                self.agent_pos = (nr, nc)
                moved = True
            else:
                self.bumped = True
        # NoOp: nenhuma alteração no ambiente

        return moved, cleaned

    def dirt_count(self):
        """Quantidade de quadrados ainda sujos."""
        return int(np.sum(self.grid == DIRT))

    def is_clean(self):
        """True quando não resta nenhum quadrado sujo."""
        return self.dirt_count() == 0

class SimpleReflexAgent:
    """
    Agente reativo simples (condição-ação).
    Decide a ação usando SOMENTE a percepção atual (sujeira, colisão),
    sem manter mapa ou histórico do ambiente. Ao colidir, escolhe uma
    nova direção aleatória; do contrário mantém a direção atual.
    """

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.direction = self.rng.choice(list(VacuumEnvironment.MOVES.keys()))

    def act(self, percept):
        # Regra 1: se a célula está suja, aspire
        if percept["dirty"]:
            return "Suck"
        # Regra 2: se bateu, escolha nova direção aleatória
        if percept["bump"]:
            self.direction = self.rng.choice(list(VacuumEnvironment.MOVES.keys()))
        # Regra 3: continue andando na direção atual
        return self.direction


class ModelBasedReflexAgent:
    """
    Agente reativo baseado em modelo.
    Mantém um modelo interno do ambiente: posição estimada (relativa ao
    ponto de partida, obtida por 'dead-reckoning' a partir das ações) e
    o estado conhecido de cada célula já visitada/detectada
    ('unknown', 'clean', 'dirty' ou 'obstacle'). Usa esse modelo para
    preferir explorar células desconhecidas ou sujas em vez de repetir
    células já limpas ou bater em obstáculos já conhecidos.
    """

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.pos = (0, 0)                    # posição estimada no referencial próprio
        self.known = {self.pos: "unknown"}   # modelo interno do mundo
        self.last_action = None

    def _update_model(self, percept):
        # Atualiza a posição estimada / registra obstáculos conforme o
        # resultado da última ação de movimento tentada
        if self.last_action in VacuumEnvironment.MOVES:
            dr, dc = VacuumEnvironment.MOVES[self.last_action]
            destino = (self.pos[0] + dr, self.pos[1] + dc)
            if percept["bump"]:
                self.known[destino] = "obstacle"
            else:
                self.pos = destino

        # Atualiza o estado conhecido da célula atual
        self.known[self.pos] = "dirty" if percept["dirty"] else "clean"

    def _choose_direction(self):
        """Prioriza mover para célula desconhecida > suja > limpa; evita obstáculo."""
        candidatos = []
        for direcao, (dr, dc) in VacuumEnvironment.MOVES.items():
            destino = (self.pos[0] + dr, self.pos[1] + dc)
            estado = self.known.get(destino, "unknown")
            if estado == "obstacle":
                continue
            prioridade = {"unknown": 0, "dirty": 1, "clean": 2}[estado]
            candidatos.append((prioridade, direcao))

        if not candidatos:
            return self.rng.choice(list(VacuumEnvironment.MOVES.keys()))

        melhor_prioridade = min(candidatos, key=lambda x: x[0])[0]
        melhores = [d for p, d in candidatos if p == melhor_prioridade]
        return self.rng.choice(melhores)

    def act(self, percept):
        self._update_model(percept)

        if percept["dirty"]:
            acao = "Suck"
        else:
            acao = self._choose_direction()

        self.last_action = acao
        return acao