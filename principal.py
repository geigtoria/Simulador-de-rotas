import argparse
import tkinter as tk

from simulador.interface import AplicacaoSimulador


def principal() -> None:
    analisador = argparse.ArgumentParser(description="Simulador de rotas: Busca Gulosa × A*")
    analisador.add_argument("--linhas", type=int, default=20,
                            help="linhas da grade (padrão 20)")
    analisador.add_argument("--colunas", type=int, default=32,
                            help="colunas da grade (padrão 32)")
    analisador.add_argument("--celula", type=int, default=26,
                            help="tamanho da célula em pixels (padrão 26)")
    argumentos = analisador.parse_args()

    if not (8 <= argumentos.linhas <= 80 and 10 <= argumentos.colunas <= 120
            and 10 <= argumentos.celula <= 60):
        analisador.error("use 8-80 linhas, 10-120 colunas e células de 10-60 px")

    janela = tk.Tk()
    AplicacaoSimulador(janela, linhas=argumentos.linhas, colunas=argumentos.colunas,
                       tamanho_celula=argumentos.celula)
    janela.mainloop()


if __name__ == "__main__":
    principal()
