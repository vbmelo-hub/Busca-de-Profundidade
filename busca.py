# -*- coding: utf-8 -*-
"""
Algoritmos de busca: aleatória, DFS, BFS e A*.

Só a busca aleatória está implementada em busca(); DFS, BFS e A* ficam
como exercício, seguindo a mesma estrutura (um `while` que tira uma
célula da fronteira e expande os vizinhos dela). O que muda entre eles é
a estrutura de dados usada pra guardar a fronteira:

    aleatória -> lista comum + random.choice
    DFS       -> pilha (LIFO): tira sempre o último que entrou
    BFS       -> fila (FIFO): tira sempre o primeiro que entrou
    A*        -> fila de prioridade: tira sempre o "mais promissor"

busca() roda o algoritmo inteiro e devolve uma lista de estados (um
dicionário por passo), na ordem em que aconteceram.

Rode "python3 busca.py" pra ver a busca aleatória resolvendo um labirinto
de exemplo, passo a passo, no terminal.
"""

import random


def novo_estado():
    """Um retrato do algoritmo em um instante da busca: só dados, sem lógica."""
    return {
        "visitados": set(),   # células já expandidas ("fechadas")
        "fronteira": set(),   # células conhecidas mas ainda não expandidas ("abertas")
        "pai": {},             # pai[celula] = célula anterior no caminho até ela
        "atual": None,         # célula sendo expandida neste passo
        "passos": 0,           # quantos nós já foram expandidos até agora
        "encontrado": False,   # True quando o objetivo foi alcançado
        "falhou": False,       # True quando a fronteira esvaziou sem achar o objetivo
        "caminho": [],         # caminho início -> objetivo, preenchido quando encontrado=True
    }


def _copia_do_estado(estado):
    """Tira uma 'foto' do estado atual, pra guardar no histórico sem que
    mudanças futuras no `estado` original afetem essa foto já tirada."""
    return {
        "visitados": set(estado["visitados"]),
        "fronteira": set(estado["fronteira"]),
        "atual": estado["atual"],
        "passos": estado["passos"],
        "encontrado": estado["encontrado"],
        "falhou": estado["falhou"],
        "caminho": list(estado["caminho"]),
    }


def _reconstruir_caminho(pai, objetivo):
    """Segue os "pais" de trás pra frente, do objetivo até o início."""
    caminho = []
    celula = objetivo
    while celula is not None:
        caminho.append(celula)
        celula = pai.get(celula)
    caminho.reverse()
    return caminho


def _expandir(estado, celula, objetivo, vizinhos, fronteira):
    """Passo comum às buscas aleatória / DFS / BFS:

    1. marca `celula` como visitada;
    2. se `celula` for o objetivo, monta o caminho e termina;
    3. senão, manda os vizinhos ainda não conhecidos pra fronteira.

    (o bloco do A*, lá embaixo, não usa esta função porque também precisa
    comparar custos entre caminhos, então ele é um pouquinho diferente.)
    """
    estado["fronteira"].discard(celula)
    estado["visitados"].add(celula)
    estado["atual"] = celula
    estado["passos"] += 1

    if celula == objetivo:
        estado["encontrado"] = True
        estado["caminho"] = _reconstruir_caminho(estado["pai"], objetivo)
        return

    for viz in vizinhos(celula):
        if viz in estado["visitados"] or viz in estado["fronteira"]:
            continue
        estado["pai"][viz] = celula
        estado["fronteira"].add(viz)
        fronteira.append(viz)


def busca(inicio, objetivo, vizinhos):
    """Roda a busca em profundidade (DFS) e devolve o histórico: um estado
    (dicionário) por passo, na ordem em que aconteceram.

    A fronteira funciona como uma pilha (LIFO): a última célula adicionada
    é a primeira a ser expandida, aprofundando a busca em cada ramo.
    Os vizinhos são explorados na ordem inversa à fornecida por `vizinhos`.
    O pai só é definido ao visitar a célula, seguindo o ramo ativo da DFS.
    """
    estado = novo_estado()
    estado["fronteira"].add(inicio)
    estado["pai"][inicio] = None
    historico = []

    # BUSCA EM PROFUNDIDADE (DFS)
    # Cada entrada guarda a célula e o pai proposto pelo ramo atual.
    fronteira = [(inicio, None)]
    
    while fronteira:
        celula, pai = fronteira.pop()
        if celula in estado["visitados"]:
            continue

        estado["fronteira"].discard(celula)
        estado["visitados"].add(celula)
        estado["pai"][celula] = pai
        estado["atual"] = celula
        estado["passos"] += 1

        if celula == objetivo:
            estado["encontrado"] = True
            estado["caminho"] = _reconstruir_caminho(estado["pai"], objetivo)
        else:
            for viz in vizinhos(celula):
                if viz not in estado["visitados"]:
                    # Mesmo que já esteja na pilha, este ramo tem prioridade.
                    fronteira.append((viz, celula))
                    estado["fronteira"].add(viz)

        historico.append(_copia_do_estado(estado))
        if estado["encontrado"]:
            return historico

    estado["falhou"] = True
    historico.append(_copia_do_estado(estado))
    return historico


if __name__ == "__main__":
    # Demonstração em modo texto, sem pygame: mostra a busca aleatória
    # resolvendo um labirinto pequeno, passo a passo, no terminal.
    grade_exemplo = [
        "#########",
        "#S..#...#",
        "#.#.#.#.#",
        "#.#...#.#",
        "#.#####.#",
        "#.......#",
        "#.#####E#",
        "#########",
    ]

    paredes = set()
    inicio = objetivo = None
    for y, linha in enumerate(grade_exemplo):
        for x, c in enumerate(linha):
            if c == "#":
                paredes.add((x, y))
            elif c == "S":
                inicio = (x, y)
            elif c == "E":
                objetivo = (x, y)

    largura, altura = len(grade_exemplo[0]), len(grade_exemplo)

    def vizinhos_exemplo(celula):
        cx, cy = celula
        livres = []
        for nx, ny in ((cx, cy - 1), (cx, cy + 1), (cx - 1, cy), (cx + 1, cy)):
            if 0 <= nx < largura and 0 <= ny < altura and (nx, ny) not in paredes:
                livres.append((nx, ny))
        return livres

    print("Labirinto de exemplo (S=início, E=objetivo):")
    for linha in grade_exemplo:
        print(" ", linha)
    print()

    historico = busca(inicio, objetivo, vizinhos_exemplo)
    for estado in historico:
        print(f"passo {estado['passos']:2d}: atual={estado['atual']}  "
              f"fronteira={len(estado['fronteira']):2d}  visitados={len(estado['visitados']):2d}")

    print()
    estado_final = historico[-1]
    if estado_final["encontrado"]:
        print(f"Achou o objetivo em {estado_final['passos']} passos "
              f"(caminho com {len(estado_final['caminho'])} células).")
    else:
        print("Não achou o objetivo.")
