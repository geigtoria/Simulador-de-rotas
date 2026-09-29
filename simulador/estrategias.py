from __future__ import annotations

import heapq
import itertools
import statistics
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .grade import Grade, Posicao


def distancia_manhattan(a: Posicao, b: Posicao) -> int:
    """Heurística admissível e consistente para grade 4-conectada com custo 1."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


@dataclass(frozen=True)
class PassoBusca:
    """Um passo da busca: o nó expandido e os nós que ele colocou na fronteira."""
    expandido: Posicao
    descobertos: tuple[Posicao, ...]


@dataclass
class ResultadoBusca:
    algoritmo: str
    caminho: list[Posicao]
    passos: list[PassoBusca]
    nos_explorados: int
    nos_gerados: int
    fronteira_maxima: int
    tempo_ms: float = 0.0
    versao_grade: int = -1

    @property
    def encontrou(self) -> bool:
        return bool(self.caminho)

    @property
    def custo(self) -> int | None:
        return len(self.caminho) - 1 if self.caminho else None


class EstrategiaBusca(ABC):
    nome: str = ""
    nome_curto: str = ""

    def __init__(self, repeticoes_tempo: int = 5) -> None:
        self.repeticoes_tempo = max(1, repeticoes_tempo)

    def buscar_caminho(self, grade: Grade) -> ResultadoBusca:
        duracoes = []
        resultado: ResultadoBusca | None = None
        for _ in range(self.repeticoes_tempo):
            t0 = time.perf_counter_ns()
            resultado = self._buscar(grade)
            duracoes.append(time.perf_counter_ns() - t0)
        assert resultado is not None
        resultado.tempo_ms = statistics.median(duracoes) / 1_000_000
        resultado.versao_grade = grade.versao
        return resultado

    @abstractmethod
    def _buscar(self, grade: Grade) -> ResultadoBusca: ...

    @staticmethod
    def _reconstruir_caminho(pais: dict[Posicao, Posicao | None],
                             alvo: Posicao) -> list[Posicao]:
        caminho: list[Posicao] = []
        atual: Posicao | None = alvo
        while atual is not None:
            caminho.append(atual)
            atual = pais[atual]
        caminho.reverse()
        return caminho


class BuscaGulosa(EstrategiaBusca):
    """Busca Gulosa: ordena a fronteira apenas por h(n)."""

    nome = "Busca Gulosa (Greedy Best-First)"
    nome_curto = "Gulosa"

    def _buscar(self, grade: Grade) -> ResultadoBusca:
        inicio, alvo = grade.inicio, grade.alvo
        desempate = itertools.count()
        fronteira = [(distancia_manhattan(inicio, alvo), next(desempate), inicio)]
        pais: dict[Posicao, Posicao | None] = {inicio: None}
        fechados: set[Posicao] = set()
        passos: list[PassoBusca] = []
        fronteira_maxima = 1

        while fronteira:
            fronteira_maxima = max(fronteira_maxima, len(pais) - len(fechados))
            _, _, atual = heapq.heappop(fronteira)
            fechados.add(atual)

            if atual == alvo:
                passos.append(PassoBusca(atual, ()))
                return ResultadoBusca(self.nome_curto, self._reconstruir_caminho(pais, alvo),
                                      passos, len(fechados), len(pais), fronteira_maxima)

            novos = []
            for vizinho in grade.vizinhos(atual):
                if vizinho not in pais:
                    pais[vizinho] = atual
                    heapq.heappush(fronteira, (distancia_manhattan(vizinho, alvo),
                                               next(desempate), vizinho))
                    novos.append(vizinho)
            passos.append(PassoBusca(atual, tuple(novos)))

        return ResultadoBusca(self.nome_curto, [], passos, len(fechados), len(pais),
                              fronteira_maxima)


class AEstrela(EstrategiaBusca):
    """A*: ordena a fronteira por f(n) = g(n) + h(n)."""

    nome = "A* (A-Star)"
    nome_curto = "A*"

    def _buscar(self, grade: Grade) -> ResultadoBusca:
        inicio, alvo = grade.inicio, grade.alvo
        desempate = itertools.count()
        h_inicio = distancia_manhattan(inicio, alvo)
        fronteira = [(h_inicio, h_inicio, next(desempate), inicio)]
        custo_g: dict[Posicao, int] = {inicio: 0}
        pais: dict[Posicao, Posicao | None] = {inicio: None}
        fechados: set[Posicao] = set()
        passos: list[PassoBusca] = []
        fronteira_maxima = 1

        while fronteira:
            fronteira_maxima = max(fronteira_maxima, len(custo_g) - len(fechados))
            _, _, _, atual = heapq.heappop(fronteira)
            if atual in fechados:
                continue  # entrada obsoleta
            fechados.add(atual)

            if atual == alvo:
                passos.append(PassoBusca(atual, ()))
                return ResultadoBusca(self.nome_curto, self._reconstruir_caminho(pais, alvo),
                                      passos, len(fechados), len(custo_g), fronteira_maxima)

            novos = []
            for vizinho in grade.vizinhos(atual):
                if vizinho in fechados:
                    continue
                g_tentativo = custo_g[atual] + 1
                if g_tentativo < custo_g.get(vizinho, float("inf")):
                    if vizinho not in custo_g:
                        novos.append(vizinho)
                    custo_g[vizinho] = g_tentativo
                    pais[vizinho] = atual
                    h = distancia_manhattan(vizinho, alvo)
                    heapq.heappush(fronteira, (g_tentativo + h, h, next(desempate), vizinho))
            passos.append(PassoBusca(atual, tuple(novos)))

        return ResultadoBusca(self.nome_curto, [], passos, len(fechados), len(custo_g),
                              fronteira_maxima)


ESTRATEGIAS: tuple[type[EstrategiaBusca], ...] = (BuscaGulosa, AEstrela)
