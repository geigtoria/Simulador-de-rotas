from __future__ import annotations

from .grade import Grade, Posicao


def armadilha_tunel(grade: Grade) -> None:
    """Túnel que "atrai" a Busca Gulosa."""
    linhas, colunas = grade.linhas, grade.colunas
    if linhas < 10 or colunas < 14:
        raise ValueError("Este cenário precisa de uma grade de pelo menos 10x14.")

    meio = linhas // 2
    tampa = colunas - 5
    canal = tampa - 1
    profundidade = max(2, min(6, linhas - meio - 3))

    paredes: set[Posicao] = set()
    for c in range(3, tampa + 1):
        paredes.add((meio - 1, c))
        paredes.add((meio + 1, c))
    paredes.add((meio, tampa))                       # fim do túnel
    paredes.discard((meio + 1, canal))               # abertura para o canal
    for l in range(meio + 1, meio + profundidade + 1):  # paredes laterais do canal
        paredes.add((l, canal - 1))
        paredes.add((l, tampa))

    grade.paredes = paredes
    grade.inicio = (meio, 1)
    grade.alvo = (meio, colunas - 2)
    grade.versao += 1


def obstaculo_em_u(grade: Grade) -> None:
    """Obstáculo côncavo (em U) aberto para o ponto de partida."""
    linhas, colunas = grade.linhas, grade.colunas
    if linhas < 8 or colunas < 10:
        raise ValueError("Este cenário precisa de uma grade de pelo menos 8x10.")

    meio = linhas // 2
    topo, base = meio - linhas // 3, meio + linhas // 3
    frente, fundo = colunas // 3, colunas * 2 // 3

    paredes: set[Posicao] = set()
    for l in range(topo, base + 1):
        paredes.add((l, fundo))
    for c in range(frente, fundo + 1):
        paredes.add((topo, c))
        paredes.add((base, c))

    grade.paredes = paredes
    grade.inicio = (meio, 1)
    grade.alvo = (meio, colunas - 2)
    grade.versao += 1


CENARIOS = {
    "Armadilha do túnel": armadilha_tunel,
    "Obstáculo em U": obstaculo_em_u,
}
