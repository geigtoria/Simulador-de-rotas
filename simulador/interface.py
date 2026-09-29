from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .cenarios import CENARIOS
from .estrategias import ESTRATEGIAS, EstrategiaBusca, ResultadoBusca
from .grade import Grade, Posicao

# Paleta de cores (Nord)
FUNDO = "#2E3440"
PAINEL = "#3B4252"
PAINEL_ALT = "#434C5E"
TEXTO = "#ECEFF4"
TEXTO_APAGADO = "#A0A8B8"
VAZIO = "#4C566A"
PAREDE = "#D08770"
EXPLORADO = "#5E81AC"
FRONTEIRA = "#8FBCBB"
INICIO = "#A3BE8C"
ALVO = "#B48EAD"
COR_ALGORITMO = {"Gulosa": "#BF616A", "A*": "#EBCB8B"}

# velocidade -> (atraso em ms, passos por quadro)
VELOCIDADES = {1: (120, 1), 2: (70, 1), 3: (40, 1), 4: (25, 1), 5: (15, 1),
               6: (10, 2), 7: (8, 4), 8: (5, 8), 9: (3, 16), 10: (1, 40)}


class AplicacaoSimulador:
    def __init__(self, janela: tk.Tk, linhas: int = 20, colunas: int = 32,
                 tamanho_celula: int = 26) -> None:
        self.janela = janela
        self.grade = Grade(linhas, colunas)
        self.tamanho_celula = tamanho_celula
        self.estrategias: dict[str, EstrategiaBusca] = {
            e.nome_curto: e() for e in ESTRATEGIAS}
        self.resultados: dict[str, ResultadoBusca] = {}

        self._tarefa_animacao: str | None = None
        self._arraste: str | None = None
        self._pintadas: set[Posicao] = set()
        self._retangulos: dict[Posicao, int] = {}

        self._configurar_estilo()
        self._montar_layout()
        self._desenhar_grade()
        self._atualizar_tabela()

    # ================================================================ layout
    def _configurar_estilo(self) -> None:
        self.janela.configure(bg=FUNDO)
        self.janela.title("Simulador de Rotas · Busca Gulosa × A*")
        estilo = ttk.Style(self.janela)
        estilo.theme_use("clam")
        estilo.configure(".", background=PAINEL, foreground=TEXTO, fieldbackground=PAINEL_ALT)
        estilo.configure("TFrame", background=PAINEL)
        estilo.configure("Fundo.TFrame", background=FUNDO)
        estilo.configure("TLabel", background=PAINEL, foreground=TEXTO)
        estilo.configure("Fundo.TLabel", background=FUNDO, foreground=TEXTO_APAGADO)
        estilo.configure("Apagado.TLabel", background=PAINEL, foreground=TEXTO_APAGADO)
        estilo.configure("Titulo.TLabel", background=PAINEL, foreground=TEXTO,
                         font=("TkDefaultFont", 11, "bold"))
        estilo.configure("Valor.TLabel", background=PAINEL, foreground=TEXTO,
                         font=("TkDefaultFont", 10, "bold"))
        estilo.configure("TButton", background=PAINEL_ALT, foreground=TEXTO,
                         borderwidth=0, padding=(10, 6))
        estilo.map("TButton", background=[("active", VAZIO), ("disabled", PAINEL)],
                   foreground=[("disabled", TEXTO_APAGADO)])
        estilo.configure("Destaque.TButton", background="#88C0D0", foreground=FUNDO,
                         font=("TkDefaultFont", 10, "bold"))
        estilo.map("Destaque.TButton", background=[("active", "#8FBCBB")])
        estilo.configure("TRadiobutton", background=PAINEL, foreground=TEXTO)
        estilo.map("TRadiobutton", background=[("active", PAINEL)])
        estilo.configure("TCheckbutton", background=PAINEL, foreground=TEXTO)
        estilo.map("TCheckbutton", background=[("active", PAINEL)])
        estilo.configure("Horizontal.TScale", background=PAINEL, troughcolor=PAINEL_ALT)
        estilo.configure("TCombobox", fieldbackground=PAINEL_ALT, background=PAINEL_ALT,
                         foreground=TEXTO, arrowcolor=TEXTO)
        estilo.map("TCombobox", fieldbackground=[("readonly", PAINEL_ALT)],
                   foreground=[("readonly", TEXTO)], selectbackground=[("readonly", PAINEL_ALT)],
                   selectforeground=[("readonly", TEXTO)])
        self.janela.option_add("*TCombobox*Listbox.background", PAINEL_ALT)
        self.janela.option_add("*TCombobox*Listbox.foreground", TEXTO)
        estilo.configure("Treeview", background=PAINEL_ALT, fieldbackground=PAINEL_ALT,
                         foreground=TEXTO, rowheight=24, borderwidth=0)
        estilo.configure("Treeview.Heading", background=FUNDO, foreground=TEXTO,
                         font=("TkDefaultFont", 10, "bold"), relief="flat")
        estilo.map("Treeview.Heading", background=[("active", FUNDO)])
        estilo.map("Treeview", background=[("selected", PAINEL_ALT)],
                   foreground=[("selected", TEXTO)])

    def _montar_layout(self) -> None:
        externo = ttk.Frame(self.janela, style="Fundo.TFrame", padding=12)
        externo.pack(fill="both", expand=True)

        esquerda = ttk.Frame(externo, style="Fundo.TFrame")
        esquerda.pack(side="left", fill="both", expand=True)
        direita = ttk.Frame(externo, padding=12)
        direita.pack(side="right", fill="y", padx=(12, 0))

        self._montar_barra_ferramentas(esquerda)
        largura = self.grade.colunas * self.tamanho_celula
        altura = self.grade.linhas * self.tamanho_celula
        self.tela = tk.Canvas(esquerda, width=largura, height=altura, bg=FUNDO,
                              highlightthickness=0)
        self.tela.pack(pady=(8, 8))
        self._ligar_eventos_mouse()
        self._montar_legenda(esquerda)

        self._montar_painel_estrategia(direita)
        self._montar_painel_ao_vivo(direita)
        self._montar_painel_comparativo(direita)

        self.barra_status = ttk.Label(esquerda, style="Fundo.TLabel", text=(
            "Clique esquerdo: desenhar paredes · Botão direito: apagar · "
            "Arraste A (início) e B (alvo) para mover"))
        self.barra_status.pack(anchor="w")

    def _montar_barra_ferramentas(self, pai: ttk.Frame) -> None:
        barra = ttk.Frame(pai, padding=8)
        barra.pack(fill="x")
        ttk.Button(barra, text="Paredes aleatórias",
                   command=self._gerar_paredes_aleatorias).pack(side="left")
        ttk.Button(barra, text="Limpar paredes",
                   command=self._limpar_paredes).pack(side="left", padx=6)
        ttk.Label(barra, text="Cenário:", style="Apagado.TLabel").pack(side="left", padx=(12, 4))
        self.var_cenario = tk.StringVar(value=next(iter(CENARIOS)))
        ttk.Combobox(barra, textvariable=self.var_cenario, values=list(CENARIOS),
                     state="readonly", width=20).pack(side="left")
        ttk.Button(barra, text="Carregar",
                   command=self._carregar_cenario).pack(side="left", padx=6)

    def _montar_legenda(self, pai: ttk.Frame) -> None:
        legenda = ttk.Frame(pai, style="Fundo.TFrame")
        legenda.pack(anchor="w", pady=(0, 6))
        itens = [(INICIO, "Início (A)"), (ALVO, "Alvo (B)"), (PAREDE, "Parede"),
                 (EXPLORADO, "Explorado"), (FRONTEIRA, "Fronteira"),
                 (COR_ALGORITMO["Gulosa"], "Rota Gulosa"), (COR_ALGORITMO["A*"], "Rota A*")]
        for cor, rotulo in itens:
            amostra = tk.Canvas(legenda, width=14, height=14, bg=FUNDO, highlightthickness=0)
            amostra.create_rectangle(1, 1, 13, 13, fill=cor, outline="")
            amostra.pack(side="left")
            ttk.Label(legenda, text=rotulo, style="Fundo.TLabel").pack(side="left", padx=(4, 12))

    def _montar_painel_estrategia(self, pai: ttk.Frame) -> None:
        ttk.Label(pai, text="Estratégia do agente", style="Titulo.TLabel").pack(anchor="w")
        self.var_algoritmo = tk.StringVar(value="A*")
        for nome_curto, estrategia in self.estrategias.items():
            ttk.Radiobutton(pai, text=estrategia.nome, value=nome_curto,
                            variable=self.var_algoritmo,
                            command=self._ao_trocar_algoritmo).pack(anchor="w", pady=1)

        self.botao_executar = ttk.Button(pai, style="Destaque.TButton",
                                         command=self._executar_selecionada)
        self.botao_executar.pack(fill="x", pady=(8, 4))
        ttk.Button(pai, text="Comparar as duas no mesmo mapa",
                   command=self._comparar_ambas).pack(fill="x", pady=2)
        ttk.Button(pai, text="Limpar busca", command=self._limpar_busca).pack(fill="x", pady=2)
        self._ao_trocar_algoritmo()

        linha_velocidade = ttk.Frame(pai)
        linha_velocidade.pack(fill="x", pady=(10, 0))
        self.var_animar = tk.BooleanVar(value=True)
        ttk.Checkbutton(linha_velocidade, text="Animar",
                        variable=self.var_animar).pack(side="left")
        ttk.Label(linha_velocidade, text="Velocidade",
                  style="Apagado.TLabel").pack(side="left", padx=(10, 4))
        self.var_velocidade = tk.IntVar(value=6)
        ttk.Scale(linha_velocidade, from_=1, to=10, variable=self.var_velocidade,
                  orient="horizontal",
                  command=lambda v: self.var_velocidade.set(round(float(v)))).pack(
            side="left", fill="x", expand=True)

    def _montar_painel_ao_vivo(self, pai: ttk.Frame) -> None:
        ttk.Separator(pai).pack(fill="x", pady=12)
        ttk.Label(pai, text="Execução atual (tempo real)", style="Titulo.TLabel").pack(anchor="w")
        caixa = ttk.Frame(pai)
        caixa.pack(fill="x", pady=(4, 0))
        self.ao_vivo: dict[str, tk.StringVar] = {}
        campos = [("algoritmo", "Algoritmo"), ("status", "Status"),
                  ("explorados", "Nós explorados"), ("fronteira", "Fronteira atual"),
                  ("custo", "Custo do caminho"), ("tempo", "Tempo de convergência")]
        for i, (chave, rotulo) in enumerate(campos):
            ttk.Label(caixa, text=rotulo, style="Apagado.TLabel").grid(
                row=i, column=0, sticky="w", pady=1)
            variavel = tk.StringVar(value="—")
            ttk.Label(caixa, textvariable=variavel, style="Valor.TLabel").grid(
                row=i, column=1, sticky="e", padx=(16, 0))
            self.ao_vivo[chave] = variavel
        caixa.columnconfigure(1, weight=1)

    def _montar_painel_comparativo(self, pai: ttk.Frame) -> None:
        ttk.Separator(pai).pack(fill="x", pady=12)
        ttk.Label(pai, text="Comparativo", style="Titulo.TLabel").pack(anchor="w")
        self.tabela = ttk.Treeview(pai, columns=("metrica", "Gulosa", "A*"),
                                   show="headings", height=6, selectmode="none")
        self.tabela.column("metrica", width=205, anchor="w")
        self.tabela.column("Gulosa", width=85, anchor="e")
        self.tabela.column("A*", width=100, anchor="e")
        self.tabela.heading("metrica", text="Métrica", anchor="w")
        self.tabela.pack(fill="x", pady=(4, 4))
        self.nota_tabela = ttk.Label(pai, style="Apagado.TLabel", wraplength=370,
                                     justify="left")
        self.nota_tabela.pack(anchor="w")

    # ================================================================ desenho
    def _desenhar_grade(self) -> None:
        tam, espaco = self.tamanho_celula, 1
        for l in range(self.grade.linhas):
            for c in range(self.grade.colunas):
                x0, y0 = c * tam + espaco, l * tam + espaco
                self._retangulos[(l, c)] = self.tela.create_rectangle(
                    x0, y0, x0 + tam - 2 * espaco, y0 + tam - 2 * espaco,
                    fill=VAZIO, outline="")
        margem = max(2, tam // 8)
        self._marcadores = {}
        for chave, cor, letra in (("inicio", INICIO, "A"), ("alvo", ALVO, "B")):
            circulo = self.tela.create_oval(0, 0, 1, 1, fill=cor, outline=FUNDO, width=2,
                                            tags=("marcador",))
            texto = self.tela.create_text(0, 0, text=letra, fill=FUNDO,
                                          font=("TkDefaultFont", max(8, tam // 2 - 2), "bold"),
                                          tags=("marcador",))
            self._marcadores[chave] = (circulo, texto, margem)
        self._redesenhar_tudo()

    def _redesenhar_tudo(self) -> None:
        for posicao, retangulo in self._retangulos.items():
            cor = PAREDE if posicao in self.grade.paredes else VAZIO
            self.tela.itemconfigure(retangulo, fill=cor)
        self._pintadas.clear()
        self._posicionar_marcadores()

    def _posicionar_marcadores(self) -> None:
        tam = self.tamanho_celula
        for chave, posicao in (("inicio", self.grade.inicio), ("alvo", self.grade.alvo)):
            circulo, texto, margem = self._marcadores[chave]
            l, c = posicao
            x0, y0 = c * tam, l * tam
            self.tela.coords(circulo, x0 + margem, y0 + margem,
                             x0 + tam - margem, y0 + tam - margem)
            self.tela.coords(texto, x0 + tam / 2, y0 + tam / 2)
        self.tela.tag_raise("marcador")

    def _pintar(self, posicao: Posicao, cor: str) -> None:
        self.tela.itemconfigure(self._retangulos[posicao], fill=cor)
        self._pintadas.add(posicao)

    def _centro(self, posicao: Posicao, deslocamento: float = 0.0) -> tuple[float, float]:
        l, c = posicao
        tam = self.tamanho_celula
        return c * tam + tam / 2 + deslocamento, l * tam + tam / 2 + deslocamento

    def _nova_linha_rota(self, algoritmo: str) -> int:
        return self.tela.create_line(0, 0, 0, 0, fill=COR_ALGORITMO[algoritmo],
                                     width=max(3, self.tamanho_celula // 5),
                                     capstyle="round", joinstyle="round", tags=("rota",))

    def _posicao_do_evento(self, evento: tk.Event) -> Posicao | None:
        posicao = (int(evento.y // self.tamanho_celula), int(evento.x // self.tamanho_celula))
        return posicao if self.grade.dentro_limites(posicao) else None

    # ============================================================== interação
    def _ligar_eventos_mouse(self) -> None:
        self.tela.bind("<ButtonPress-1>", self._ao_pressionar_esquerdo)
        self.tela.bind("<B1-Motion>", self._ao_arrastar_esquerdo)
        self.tela.bind("<ButtonRelease-1>", lambda e: setattr(self, "_arraste", None))
        for botao in ("2", "3"):  # botão direito
            self.tela.bind(f"<ButtonPress-{botao}>", self._ao_usar_direito)
            self.tela.bind(f"<B{botao}-Motion>", self._ao_usar_direito)

    def _ao_pressionar_esquerdo(self, evento: tk.Event) -> None:
        posicao = self._posicao_do_evento(evento)
        if posicao is None:
            return
        if posicao == self.grade.inicio:
            self._arraste = "inicio"
        elif posicao == self.grade.alvo:
            self._arraste = "alvo"
        else:
            # começou sobre parede: apaga; senão: desenha
            self._arraste = "apagar" if self.grade.eh_parede(posicao) else "parede"
            self._aplicar_parede(posicao, self._arraste == "parede")

    def _ao_arrastar_esquerdo(self, evento: tk.Event) -> None:
        posicao = self._posicao_do_evento(evento)
        if posicao is None or self._arraste is None:
            return
        if self._arraste == "inicio" and self.grade.mover_inicio(posicao):
            self._ao_alterar_grade()
        elif self._arraste == "alvo" and self.grade.mover_alvo(posicao):
            self._ao_alterar_grade()
        elif self._arraste in ("parede", "apagar"):
            self._aplicar_parede(posicao, self._arraste == "parede")

    def _ao_usar_direito(self, evento: tk.Event) -> None:
        posicao = self._posicao_do_evento(evento)
        if posicao is not None:
            self._aplicar_parede(posicao, False)

    def _aplicar_parede(self, posicao: Posicao, parede: bool) -> None:
        if self.grade.definir_parede(posicao, parede):
            self._ao_alterar_grade()

    def _ao_alterar_grade(self) -> None:
        """Qualquer edição cancela a animação e invalida a busca exibida."""
        self._parar_animacao()
        self._redesenhar_tudo()
        self.tela.delete("rota")
        self._atualizar_tabela()

    def _gerar_paredes_aleatorias(self) -> None:
        self.grade.paredes_aleatorias(0.3)
        self._ao_alterar_grade()
        self._definir_status("Mapa aleatório gerado (sempre com pelo menos um caminho).")

    def _limpar_paredes(self) -> None:
        self.grade.limpar_paredes()
        self._ao_alterar_grade()

    def _carregar_cenario(self) -> None:
        nome = self.var_cenario.get()
        try:
            CENARIOS[nome](self.grade)
        except ValueError as erro:
            self._definir_status(str(erro))
            return
        self._ao_alterar_grade()
        self._definir_status(f"Cenário carregado: {nome}. Rode as duas estratégias para comparar.")

    def _ao_trocar_algoritmo(self) -> None:
        self.botao_executar.configure(text=f"▶  Executar {self.var_algoritmo.get()}")

    def _definir_status(self, texto: str) -> None:
        self.barra_status.configure(text=texto)

    # ================================================================ busca
    def _limpar_busca(self) -> None:
        self._parar_animacao()
        for posicao in self._pintadas:
            self.tela.itemconfigure(self._retangulos[posicao], fill=VAZIO)
        self._pintadas.clear()
        self.tela.delete("rota")
        for variavel in self.ao_vivo.values():
            variavel.set("—")

    def _parar_animacao(self) -> None:
        if self._tarefa_animacao is not None:
            self.janela.after_cancel(self._tarefa_animacao)
            self._tarefa_animacao = None

    def _executar_selecionada(self) -> None:
        self._limpar_busca()
        estrategia = self.estrategias[self.var_algoritmo.get()]
        resultado = estrategia.buscar_caminho(self.grade)
        self.resultados[resultado.algoritmo] = resultado

        self.ao_vivo["algoritmo"].set(estrategia.nome.split(" (")[0])
        self.ao_vivo["status"].set("explorando…")
        self.ao_vivo["tempo"].set(f"{resultado.tempo_ms:.3f} ms")

        if self.var_animar.get():
            self._animar(resultado)
        else:
            self._mostrar_exploracao(resultado)
            self._desenhar_rota(resultado)
            self._finalizar(resultado)

    def _mostrar_exploracao(self, resultado: ResultadoBusca) -> None:
        for passo in resultado.passos:
            if not self.grade.eh_especial(passo.expandido):
                self._pintar(passo.expandido, EXPLORADO)
            for vizinho in passo.descobertos:
                if not self.grade.eh_especial(vizinho):
                    self._pintar(vizinho, FRONTEIRA)
        self.ao_vivo["explorados"].set(str(resultado.nos_explorados))
        self.ao_vivo["fronteira"].set(str(resultado.nos_gerados - resultado.nos_explorados))

    def _desenhar_rota(self, resultado: ResultadoBusca, deslocamento: float = 0.0) -> None:
        if len(resultado.caminho) < 2:
            return
        linha = self._nova_linha_rota(resultado.algoritmo)
        coordenadas = [v for p in resultado.caminho for v in self._centro(p, deslocamento)]
        self.tela.coords(linha, *coordenadas)
        self.tela.tag_raise("marcador")

    def _animar(self, resultado: ResultadoBusca) -> None:
        estado = {"passo": 0, "gerados": 1, "indice_rota": 1, "linha": None}

        def quadro_exploracao() -> None:
            atraso, por_quadro = VELOCIDADES[self.var_velocidade.get()]
            for _ in range(por_quadro):
                if estado["passo"] >= len(resultado.passos):
                    self.ao_vivo["status"].set(
                        "traçando rota…" if resultado.encontrou else "sem caminho")
                    self._tarefa_animacao = self.janela.after(atraso, quadro_rota)
                    return
                passo = resultado.passos[estado["passo"]]
                if not self.grade.eh_especial(passo.expandido):
                    self._pintar(passo.expandido, EXPLORADO)
                for vizinho in passo.descobertos:
                    if not self.grade.eh_especial(vizinho):
                        self._pintar(vizinho, FRONTEIRA)
                estado["passo"] += 1
                estado["gerados"] += len(passo.descobertos)
            self.ao_vivo["explorados"].set(str(estado["passo"]))
            self.ao_vivo["fronteira"].set(str(estado["gerados"] - estado["passo"]))
            self._tarefa_animacao = self.janela.after(atraso, quadro_exploracao)

        def quadro_rota() -> None:
            self.ao_vivo["explorados"].set(str(resultado.nos_explorados))
            self.ao_vivo["fronteira"].set(str(resultado.nos_gerados - resultado.nos_explorados))
            if not resultado.encontrou:
                self._finalizar(resultado)
                return
            if estado["linha"] is None:
                estado["linha"] = self._nova_linha_rota(resultado.algoritmo)
            atraso, por_quadro = VELOCIDADES[self.var_velocidade.get()]
            estado["indice_rota"] = min(len(resultado.caminho),
                                        estado["indice_rota"] + max(1, por_quadro // 4))
            trecho = resultado.caminho[: estado["indice_rota"]]
            coordenadas = [v for p in trecho for v in self._centro(p)]
            if len(coordenadas) >= 4:
                self.tela.coords(estado["linha"], *coordenadas)
                self.tela.tag_raise("marcador")
            self.ao_vivo["custo"].set(str(len(trecho) - 1))
            if estado["indice_rota"] >= len(resultado.caminho):
                self._finalizar(resultado)
            else:
                self._tarefa_animacao = self.janela.after(max(atraso, 15), quadro_rota)

        quadro_exploracao()

    def _finalizar(self, resultado: ResultadoBusca) -> None:
        self._tarefa_animacao = None
        self.ao_vivo["explorados"].set(str(resultado.nos_explorados))
        self.ao_vivo["fronteira"].set(str(resultado.nos_gerados - resultado.nos_explorados))
        if resultado.encontrou:
            self.ao_vivo["status"].set("alvo alcançado")
            self.ao_vivo["custo"].set(str(resultado.custo))
            self._definir_status(
                f"{resultado.algoritmo}: custo {resultado.custo} explorando "
                f"{resultado.nos_explorados} nós em {resultado.tempo_ms:.3f} ms.")
        else:
            self.ao_vivo["status"].set("sem caminho")
            self.ao_vivo["custo"].set("—")
            self._definir_status("Não existe caminho de A até B neste mapa.")
        self._atualizar_tabela()

    def _comparar_ambas(self) -> None:
        self._limpar_busca()
        for estrategia in self.estrategias.values():
            resultado = estrategia.buscar_caminho(self.grade)
            self.resultados[resultado.algoritmo] = resultado

        gulosa, a_estrela = self.resultados["Gulosa"], self.resultados["A*"]
        deslocamento = self.tamanho_celula / 6
        self._desenhar_rota(gulosa, -deslocamento)
        self._desenhar_rota(a_estrela, deslocamento)

        self.ao_vivo["algoritmo"].set("Gulosa × A*")
        self.ao_vivo["status"].set("comparação")
        for chave in ("explorados", "fronteira", "custo", "tempo"):
            self.ao_vivo[chave].set("ver tabela")
        self._atualizar_tabela()

        if not a_estrela.encontrou:
            self._definir_status("Não existe caminho de A até B neste mapa.")
            return
        diferenca = gulosa.custo - a_estrela.custo
        proporcao = 100 * gulosa.nos_explorados / a_estrela.nos_explorados
        conclusao = ("a Gulosa também achou a rota ótima" if diferenca == 0
                     else f"a rota da Gulosa ficou {diferenca} passo(s) mais cara")
        self._definir_status(f"A Gulosa explorou {proporcao:.0f}% dos nós do A*, e {conclusao}.")

    # ================================================================ tabela
    def _atualizar_tabela(self) -> None:
        linhas_tabela = [
            ("Convergência (ms)", lambda r: f"{r.tempo_ms:.3f}"),
            ("Nós explorados", lambda r: str(r.nos_explorados)),
            ("Nós gerados", lambda r: str(r.nos_gerados)),
            ("Fronteira máxima", lambda r: str(r.fronteira_maxima)),
            ("Custo do caminho", lambda r: str(r.custo) if r.encontrou else "sem caminho"),
            ("Caminho ótimo?", self._otimalidade),
        ]
        self.tabela.delete(*self.tabela.get_children())
        desatualizados = []
        for algoritmo in ("Gulosa", "A*"):
            resultado = self.resultados.get(algoritmo)
            antigo = resultado is not None and resultado.versao_grade != self.grade.versao
            if antigo:
                desatualizados.append(algoritmo)
            self.tabela.heading(algoritmo, text=f"{algoritmo}{' *' if antigo else ''}", anchor="e")
        for rotulo, formatar in linhas_tabela:
            valores = [rotulo]
            for algoritmo in ("Gulosa", "A*"):
                resultado = self.resultados.get(algoritmo)
                valores.append(formatar(resultado) if resultado else "—")
            self.tabela.insert("", "end", values=valores)

        if desatualizados:
            self.nota_tabela.configure(text="* resultado de uma versão anterior do mapa; "
                                            "execute novamente para comparar.")
        else:
            self.nota_tabela.configure(text="Convergência = mediana de 5 execuções da busca, "
                                            "sem a animação. O A* é ótimo por garantia "
                                            "(heurística admissível).")

    def _otimalidade(self, resultado: ResultadoBusca) -> str:
        if not resultado.encontrou:
            return "—"
        if resultado.algoritmo == "A*":
            return "sim"
        a_estrela = self.resultados.get("A*")
        if (a_estrela is None or not a_estrela.encontrou
                or a_estrela.versao_grade != resultado.versao_grade):
            return "rode o A*"
        diferenca = resultado.custo - a_estrela.custo
        return "sim" if diferenca == 0 else f"não (+{diferenca})"
