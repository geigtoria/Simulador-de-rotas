from __future__ import annotations

import random
from collections import deque
from typing import Iterator

Posicao = tuple[int, int]

DIRECOES: tuple[Posicao, ...] = ((-1, 0), (0, 1), (1, 0), (0, -1))


class Grade:
    def __init__(self, linhas: int, colunas: int) -> None:
        if linhas < 2 or colunas < 2:
            raise ValueError("A grade precisa ter pelo menos 2x2 células.")
        self.linhas = linhas
        self.colunas = colunas
        self.paredes: set[Posicao] = set()
        self.inicio: Posicao = (linhas // 2, 1)
        self.alvo: Posicao = (linhas // 2, colunas - 2)
        self.versao = 0

    # ------------------------------------------------------------ consultas
    def dentro_limites(self, posicao: Posicao) -> bool:
        linha, coluna = posicao
        return 0 <= linha < self.linhas and 0 <= coluna < self.colunas

    def eh_parede(self, posicao: Posicao) -> bool:
        return posicao in self.paredes

    def eh_especial(self, posicao: Posicao) -> bool:
        return posicao == self.inicio or posicao == self.alvo

    def vizinhos(self, posicao: Posicao) -> Iterator[Posicao]:
        """Vizinhos transitáveis (4-conectividade, custo 1 por passo)."""
        linha, coluna = posicao
        for d_linha, d_coluna in DIRECOES:
            proxima = (linha + d_linha, coluna + d_coluna)
            if self.dentro_limites(proxima) and proxima not in self.paredes:
                yield proxima

    def existe_caminho(self) -> bool:
        """Busca em largura para verificar se existe caminho de A até B."""
        visitados = {self.inicio}
        fila = deque([self.inicio])
        while fila:
            atual = fila.popleft()
            if atual == self.alvo:
                return True
            for proxima in self.vizinhos(atual):
                if proxima not in visitados:
                    visitados.add(proxima)
                    fila.append(proxima)
        return False

    # ------------------------------------------------------------ edição
    def _marcar_alteracao(self) -> None:
        self.versao += 1

    def definir_parede(self, posicao: Posicao, parede: bool) -> bool:
        """Cria/remove parede. Retorna True se algo mudou."""
        if not self.dentro_limites(posicao) or self.eh_especial(posicao):
            return False
        if parede and posicao not in self.paredes:
            self.paredes.add(posicao)
        elif not parede and posicao in self.paredes:
            self.paredes.discard(posicao)
        else:
            return False
        self._marcar_alteracao()
        return True

    def mover_inicio(self, posicao: Posicao) -> bool:
        if self._pode_posicionar(posicao):
            self.inicio = posicao
            self._marcar_alteracao()
            return True
        return False

    def mover_alvo(self, posicao: Posicao) -> bool:
        if self._pode_posicionar(posicao):
            self.alvo = posicao
            self._marcar_alteracao()
            return True
        return False

    def _pode_posicionar(self, posicao: Posicao) -> bool:
        return (self.dentro_limites(posicao) and posicao not in self.paredes
                and not self.eh_especial(posicao))

    def limpar_paredes(self) -> None:
        self.paredes.clear()
        self._marcar_alteracao()

    def paredes_aleatorias(self, densidade: float = 0.3,
                           gerador: random.Random | None = None,
                           max_tentativas: int = 200) -> None:
        """Preenche a grade com paredes aleatórias garantindo que exista caminho."""
        gerador = gerador or random.Random()
        celulas = [(l, c) for l in range(self.linhas) for c in range(self.colunas)
                   if (l, c) not in (self.inicio, self.alvo)]
        for _ in range(max_tentativas):
            self.paredes = {p for p in celulas if gerador.random() < densidade}
            if self.existe_caminho():
                break
        else:
            self.paredes = set()
        self._marcar_alteracao()
