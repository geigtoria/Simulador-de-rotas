# Simulador de Rotas (Python)

Simulador interativo de planejamento de rota de um agente do ponto **A** ao ponto **B**,
comparando **Busca Gulosa (Greedy Best-First)** e **A\***. Port em Python/Tkinter do
projeto MazeSolverFX (Java/JavaFX), com as métricas comparativas que faltavam.

![Comparação no cenário "Armadilha do túnel"](documentacao/captura_de_tela.png)

## Como executar

Requer apenas Python 3.10+ com Tkinter (já incluso no instalador oficial do Windows e macOS).
No Ubuntu/Debian: `sudo apt install python3-tk`.

```bash
python principal.py                                  # grade 20x32
python principal.py --linhas 30 --colunas 45 --celula 20
python -m unittest -v                                # testes
```

## Como usar

- **Clique esquerdo e arraste**: desenha paredes (se começar sobre uma parede, apaga).
- **Botão direito e arraste**: apaga paredes.
- **Arraste A ou B** para mover o início ou o alvo.
- Escolha a estratégia e clique em **Executar**, ou use **Comparar as duas no mesmo mapa**
  para desenhar as duas rotas sobrepostas.
- **Cenários prontos**: *Armadilha do túnel* (a Gulosa explora menos nós, mas acha uma rota
  mais cara) e *Obstáculo em U* (mesmo custo, número de nós diferente).

## As estratégias

| | Busca Gulosa | A\* |
|---|---|---|
| Prioridade na fronteira | `h(n)` | `f(n) = g(n) + h(n)` |
| Heurística | Manhattan | Manhattan (admissível e consistente) |
| Rota ótima garantida? | Não | Sim |

Movimento em 4 direções com custo 1 por passo. No A\*, empates em `f` são resolvidos pelo menor `h`.

## Métricas

| Métrica | Significado |
|---|---|
| Convergência (ms) | Tempo da busca pura até chegar em B; mediana de 5 execuções, sem animação |
| Nós explorados | Nós retirados da fronteira e expandidos |
| Nós gerados | Nós que entraram na fronteira em algum momento |
| Fronteira máxima | Maior tamanho da lista aberta (indicador de memória) |
| Custo do caminho | Número de passos de A até B |
| Caminho ótimo? | Compara o custo da Gulosa com o do A\* no mesmo mapa |

## Estrutura

```
principal.py                # ponto de entrada (--linhas --colunas --celula)
simulador/grade.py          # modelo do ambiente: classe Grade (paredes, A, B)
simulador/estrategias.py    # padrão Strategy: BuscaGulosa e AEstrela + métricas
simulador/cenarios.py       # cenários de demonstração
simulador/interface.py      # interface Tkinter: classe AplicacaoSimulador
testes/teste_estrategias.py # testes (A* comparado com busca em largura etc.)
```

Nomes que ficaram em inglês por exigência do Python ou de convenção: `__init__.py`
(obrigatório para pastas de pacote), `README.md` (o GitHub só exibe este nome na página
do projeto), `.gitignore` (nome fixo do Git) e os métodos do Tkinter (`pack`, `bind`, `after`...).
