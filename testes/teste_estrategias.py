import random
import unittest
from collections import deque

from simulador.cenarios import armadilha_tunel, obstaculo_em_u
from simulador.estrategias import AEstrela, BuscaGulosa
from simulador.grade import Grade


def custo_por_largura(grade):
    """Custo mínimo por busca em largura."""
    distancia = {grade.inicio: 0}
    fila = deque([grade.inicio])
    while fila:
        atual = fila.popleft()
        if atual == grade.alvo:
            return distancia[atual]
        for vizinho in grade.vizinhos(atual):
            if vizinho not in distancia:
                distancia[vizinho] = distancia[atual] + 1
                fila.append(vizinho)
    return None


def caminho_valido(grade, caminho):
    if caminho[0] != grade.inicio or caminho[-1] != grade.alvo:
        return False
    for a, b in zip(caminho, caminho[1:]):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1 or b in grade.paredes:
            return False
    return True


class TestesEstrategias(unittest.TestCase):
    def setUp(self):
        self.a_estrela = AEstrela(repeticoes_tempo=1)
        self.gulosa = BuscaGulosa(repeticoes_tempo=1)

    def teste_a_estrela_eh_otimo_em_mapas_aleatorios(self):
        for semente in range(200):
            grade = Grade(15, 22)
            grade.paredes_aleatorias(0.3, random.Random(semente))
            resultado = self.a_estrela.buscar_caminho(grade)
            self.assertEqual(resultado.custo, custo_por_largura(grade), f"semente {semente}")
            self.assertTrue(caminho_valido(grade, resultado.caminho))

    def teste_gulosa_acha_caminho_valido_nunca_mais_barato_que_a_estrela(self):
        for semente in range(200):
            grade = Grade(15, 22)
            grade.paredes_aleatorias(0.3, random.Random(semente))
            gulosa = self.gulosa.buscar_caminho(grade)
            a_estrela = self.a_estrela.buscar_caminho(grade)
            self.assertTrue(gulosa.encontrou)
            self.assertTrue(caminho_valido(grade, gulosa.caminho))
            self.assertGreaterEqual(gulosa.custo, a_estrela.custo)

    def teste_sem_caminho(self):
        grade = Grade(8, 10)
        for linha in range(grade.linhas):
            grade.definir_parede((linha, 5), True)
        for estrategia in (self.a_estrela, self.gulosa):
            resultado = estrategia.buscar_caminho(grade)
            self.assertFalse(resultado.encontrou)
            self.assertIsNone(resultado.custo)

    def teste_custo_conta_passos_e_nao_nos(self):
        grade = Grade(8, 10)
        grade.inicio, grade.alvo = (0, 0), (0, 4)
        self.assertEqual(self.a_estrela.buscar_caminho(grade).custo, 4)

    def teste_armadilha_do_tunel_mostra_o_compromisso(self):
        grade = Grade(20, 32)
        armadilha_tunel(grade)
        gulosa = self.gulosa.buscar_caminho(grade)
        a_estrela = self.a_estrela.buscar_caminho(grade)
        self.assertGreater(gulosa.custo, a_estrela.custo)
        self.assertLess(gulosa.nos_explorados, a_estrela.nos_explorados)

    def teste_obstaculo_em_u_tem_mesmo_custo(self):
        grade = Grade(20, 32)
        obstaculo_em_u(grade)
        self.assertEqual(self.gulosa.buscar_caminho(grade).custo,
                         self.a_estrela.buscar_caminho(grade).custo)

    def teste_metricas_consistentes(self):
        grade = Grade(20, 32)
        grade.paredes_aleatorias(0.25, random.Random(7))
        for estrategia in (self.a_estrela, self.gulosa):
            resultado = estrategia.buscar_caminho(grade)
            self.assertEqual(resultado.nos_explorados, len(resultado.passos))
            self.assertEqual(resultado.nos_gerados,
                             1 + sum(len(p.descobertos) for p in resultado.passos))
            self.assertGreaterEqual(resultado.tempo_ms, 0)
            self.assertEqual(resultado.versao_grade, grade.versao)


if __name__ == "__main__":
    unittest.main()
