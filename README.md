# IC-Projeto1 — Avaliação Experimental de Agentes Inteligentes

Simulação e avaliação experimental de dois tipos de agente aspirador de pó em um ambiente de grade determinístico e parcialmente observável, desenvolvida como projeto da disciplina de Inteligência Computacional.

## 1. Descrição do projeto

O projeto implementa e compara dois agentes que operam no clássico problema do "mundo do aspirador de pó": uma grade retangular contendo células limpas, sujas e obstáculos, na qual um agente deve se mover e aspirar toda a sujeira. O ambiente é determinístico (as ações sempre produzem o mesmo efeito) e parcialmente observável: o agente não conhece de antemão o tamanho do grid, a posição dos obstáculos nem a distribuição inicial da sujeira. A cada passo, ele percebe apenas se a célula em que está é suja e se a última tentativa de movimento resultou em colisão.

Duas abordagens de agente são implementadas e comparadas:

- **Agente Reflexo Simples** (`SimpleReflexAgent`): decide a ação usando somente a percepção do instante atual, sem manter qualquer histórico ou mapa do ambiente.
- **Agente Reflexo Baseado em Modelo** (`ModelBasedReflexAgent`): mantém um modelo interno do ambiente (posição estimada e o estado conhecido de cada célula já visitada ou detectada) e utiliza esse modelo para direcionar a exploração.

A comparação é conduzida de duas formas complementares: uma simulação interativa em terminal (`simulacao.py`), que exibe passo a passo o comportamento de um agente em um único ambiente, e um notebook de avaliação experimental (`avaliacao_agentes_aspirador.ipynb`), que executa os dois agentes em múltiplas configurações de mapa e consolida os resultados em tabelas e gráficos.

## 2. Métricas utilizadas

As métricas são calculadas pela função `run_simulation` (notebook de avaliação), a partir dos retornos de `VacuumEnvironment.step`. Cada quadrado sujo só pode gerar pontuação uma única vez, no momento em que é limpo.

- **M1 (quadrados limpos):** soma o total de quadrados efetivamente limpos pelo agente ao longo da execução. Mede diretamente o quanto da tarefa (limpar o ambiente) foi cumprido.
- **M2 (quadrados limpos menos movimentos):** calculada como `M1 - movimentos`, em que `movimentos` é o número de ações de deslocamento bem-sucedidas (`moved = True`). Penaliza deslocamento, favorecendo agentes que limpam o ambiente com menos passos de movimentação.

Além de M1 e M2, o notebook também registra, para cada execução:

- **passos:** número total de iterações do laço de simulação até o ambiente ficar limpo ou o limite `max_steps` ser atingido.
- **movimentos:** número de ações de movimento que resultaram em deslocamento efetivo (subconjunto de `passos`).
- **limpou_tudo:** booleano que indica se o agente conseguiu limpar toda a sujeira antes de atingir o limite de passos.
- **sujeira_inicial:** quantidade de células sujas na configuração de mapa sorteada, usada para derivar a sujeira restante (`sujeira_inicial - M1`).

## 3. Funções principais

### `agents.py`

- **`class VacuumEnvironment(rows, cols, dirt_cells, obstacle_cells, agent_pos)`**: representa o ambiente de grade. Mantém a matriz de estados (`EMPTY`, `DIRT`, `OBSTACLE`) e a posição do agente.
  - `percept()`: retorna a percepção local (`dirty`, `bump`) da posição atual.
  - `step(action)`: executa a ação (`Suck`, `Up`, `Down`, `Left`, `Right` ou `NoOp`), atualiza o estado do grid e retorna a tupla `(moved, cleaned)`.
  - `dirt_count()`: retorna a quantidade de células ainda sujas.
  - `is_clean()`: retorna `True` quando não resta nenhuma célula suja.
- **`class SimpleReflexAgent(seed=None)`**: implementa o agente reativo simples. O método `act(percept)` aplica três regras em ordem: aspirar se a célula estiver suja; sortear nova direção se a última tentativa de movimento colidiu; caso contrário, manter a direção atual.
- **`class ModelBasedReflexAgent(seed=None)`**: implementa o agente com modelo interno. `act(percept)` chama `_update_model(percept)`, que atualiza a posição estimada e o estado conhecido (`unknown`, `clean`, `dirty`, `obstacle`) de cada célula, e então decide a ação: aspira se a célula atual estiver suja, ou chama `_choose_direction()` para escolher a direção de menor prioridade (desconhecida > suja > limpa), excluindo direções que levam a obstáculos já conhecidos. Se todas as direções vizinhas forem obstáculos conhecidos, retorna `NoOp`.

### `simulacao.py`

- **`reachable_cells(rows, cols, obstacle_cells, start)`**: realiza uma busca em largura (BFS) a partir de `start`, respeitando os obstáculos, e retorna o conjunto de células alcançáveis.
- **`generate_configs(rows, cols, n_configs, dirt_ratio=0.3, obstacle_ratio=0.15, seed=0)`**: gera `n_configs` configurações iniciais aleatórias (posição do agente, obstáculos e sujeira). A sujeira é sorteada apenas entre as células alcançáveis a partir da posição inicial, garantindo que o ambiente gerado seja sempre limpável por completo.
- **`criar_ambiente(seed=None)`**: gera uma única configuração via `generate_configs` e instancia o `VacuumEnvironment` correspondente.
- **`renderizar(env, passo)`**: limpa o terminal e imprime a matriz do ambiente no passo atual, usando os símbolos `_` (limpo), `S` (sujeira), `O` (obstáculo) e `R` (agente), além da contagem de sujeira restante.
- **`simular(classe_agente, seed=None)`**: cria o ambiente e o agente, e executa o laço principal, renderizando o estado a cada passo (com pausa de `INTERVALO_MS`) até o ambiente ficar limpo ou `MAX_PASSOS` ser atingido.
- **`main()`**: interpreta o argumento de linha de comando (`"Agente Simples"` ou `"Agente com Modelo"`), valida a entrada e chama `simular` com a classe de agente correspondente e semente fixa (`seed=42`).

### `avaliacao_agentes_aspirador.ipynb`

- **`run_simulation(env, agent, max_steps=500)`**: executa o laço de simulação até o ambiente ficar limpo ou o limite de passos ser atingido, retornando um dicionário com `M1`, `M2`, `passos`, `movimentos` e `limpou_tudo`. Como a trajetória do agente não depende da métrica escolhida, M1 e M2 são calculadas em uma única execução.
- Reaproveita `reachable_cells` e uma cópia de `generate_configs` (com `dirt_ratio=0.4` como padrão local) para gerar as 10 configurações de mapa usadas no experimento, executar os dois agentes em cada uma e consolidar os resultados no DataFrame `df`.

## 4. Estrutura de diretórios

```
IC-Projeto1-feature-prototype/
├── .gitignore                          # arquivos/pastas ignorados pelo git (cache Python, .venv, build)
├── .python-version                     # versão do Python fixada para o projeto (3.12)
├── README.md                           # este documento
├── agents.py                           # VacuumEnvironment, SimpleReflexAgent e ModelBasedReflexAgent
├── avaliacao_agentes_aspirador.ipynb   # notebook com o experimento completo, tabelas e gráficos
├── pyproject.toml                      # metadados do projeto e dependências (uv)
├── simulacao.py                        # script de simulação interativa em terminal (entrada via uv run)
├── uv.lock                             # lockfile de dependências gerado pelo uv
└── src/
    └── trabalho_ic/
        └── __init__.py                 # pacote do projeto (função main() de exemplo, não usada por simulacao.py)
```

## 5. Análise dos gráficos e resultados

**Gráfico 1 — Taxa de limpeza total por agente**
- O Agente Reflexo com Modelo concluiu a limpeza completa em 80% das configurações de mapa testadas, enquanto o Agente Reflexo Simples não concluiu em nenhuma delas (0%), evidenciando que manter um modelo interno aumenta substancialmente a chance de atingir o objetivo dentro do limite de passos.
- O fato de o agente com modelo não atingir 100% mostra que sua exploração ainda depende de sorteio entre direções empatadas em prioridade (`_choose_direction`), de modo que, em configurações menos favoráveis, ele também pode não concluir a limpeza dentro de `MAX_STEPS`.

**Gráfico 2 — Passos e movimentos médios até a simulação parar, por agente**
- O Agente Reflexo Simples atinge, em média, um número de passos próximo do limite máximo (500), consistente com a taxa de conclusão nula do Gráfico 1: na maioria das execuções ele é interrompido pelo limite antes de terminar.
- A diferença entre passos e movimentos é maior para o agente simples: como cada ação `Suck` conta como passo mas não como movimento, e o número de quadrados aspirados é limitado pela sujeira inicial, boa parte dessa diferença corresponde a colisões (`bump`) contra obstáculos e limites do grid, indicando deslocamento pouco eficiente.

**Gráfico 3 — Sujeira deixada em cada configuração de mapa, por agente**
- Em todas as 10 configurações, o Agente Reflexo Simples deixou mais sujeira remanescente que o Agente Reflexo com Modelo, que terminou a maioria dos mapas sem nenhuma célula suja restante.
- A quantidade de sujeira deixada pelo agente simples varia bastante entre mapas (de poucas células até valores bem maiores em configurações específicas), o que é esperado de um agente sem memória, cujo desempenho depende fortemente do layout de obstáculos sorteado em cada configuração.

**Gráfico 4 — Média de desempenho (M1 e M2)**
- Na métrica M1, o Agente Reflexo com Modelo limpa, em média, mais quadrados que o Agente Reflexo Simples, resultado coerente com sua maior taxa de conclusão (Gráfico 1) e menor sujeira residual (Gráfico 3).
- Na métrica M2, ambos os agentes apresentam média negativa, pois o número de movimentos supera o de quadrados limpos em um grid deste tamanho; ainda assim, a penalidade do agente com modelo é bem menor, refletindo o menor número médio de movimentos observado no Gráfico 2.

**Gráfico 5 — M1 e M2 por configuração**
- A curva do Agente Reflexo com Modelo permanece acima da curva do Agente Reflexo Simples em praticamente todas as configurações, tanto em M1 quanto em M2, mostrando que sua vantagem não se restringe a mapas específicos, mas se mantém de forma consistente ao longo do experimento.
- A curva do Agente Reflexo Simples oscila com mais intensidade entre configurações (com quedas acentuadas em mapas específicos), refletindo a dependência de seu desempenho em relação ao layout de obstáculos de cada configuração, enquanto a curva do agente com modelo se mantém comparativamente estável e próxima do teto de M1.

## 6. Como executar o projeto

Execução do agente baseado em modelo:

```bash
uv run simulacao.py "Agente com Modelo"
```

Execução do agente reflexo simples:

```bash
uv run simulacao.py "Agente Simples"
```

Cada comando abre a simulação diretamente no terminal, renderizando a grade a cada passo até o ambiente ficar totalmente limpo ou o limite de 500 passos ser atingido.

## 7. Autores

- João Victor dos Santos Sales
- Guilherme Souto de Andrade
