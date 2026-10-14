import random
import time
import tkinter as tk
from tkinter import messagebox


class SudokuGenerator:

  @staticmethod
  def gerar_sudoku(nivel):
    remocoes = {
        "Fácil": 30,
        "Média": 38,
        "Difícil": 46,
        "Especialista": 52,
        "Mestra": 56,
        "Extrema": 60,
    }
    remover = remocoes.get(nivel, 40)

    board = [[0 for _ in range(9)] for _ in range(9)]
    SudokuGenerator._resolver(board)
    solucao = [row[:] for row in board]

    digitos = list(range(1, 10))
    random.shuffle(digitos)
    mapa = {i + 1: digitos[i] for i in range(9)}

    for r in range(9):
      for c in range(9):
        solucao[r][c] = mapa[solucao[r][c]]

    board = [row[:] for row in solucao]

    removidas = 0
    celulas = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(celulas)

    for r, c in celulas:
      if removidas >= remover:
        break
      temp = board[r][c]
      board[r][c] = 0

      copia_board = [row[:] for row in board]
      if not SudokuGenerator._tem_solucao_unica(copia_board):
        board[r][c] = temp
      else:
        removidas += 1

    return board, solucao

  @staticmethod
  def _resolver(board):
    vazia = SudokuGenerator._encontrar_vazia(board)
    if not vazia:
      return True
    r, c = vazia
    nums = list(range(1, 10))
    random.shuffle(nums)
    for num in nums:
      if SudokuGenerator._valido(board, num, (r, c)):
        board[r][c] = num
        if SudokuGenerator._resolver(board):
          return True
        board[r][c] = 0
    return False

  @staticmethod
  def _tem_solucao_unica(board):
    contador = 0

    def contar_solucoes(b):
      nonlocal contador
      vazia = SudokuGenerator._encontrar_vazia(b)
      if not vazia:
        contador += 1
        return
      r, c = vazia
      for num in range(1, 10):
        if SudokuGenerator._valido(b, num, (r, c)):
          b[r][c] = num
          contar_solucoes(b)
          b[r][c] = 0
          if contador > 1:
            return

    contar_solucoes(board)
    return contador == 1

  @staticmethod
  def _encontrar_vazia(board):
    for r in range(9):
      for c in range(9):
        if board[r][c] == 0:
          return (r, c)
    return None

  @staticmethod
  def _valido(board, num, pos):
    r, c = pos
    if num in board[r]:
      return False
    if num in [board[i][c] for i in range(9)]:
      return False
    br, bc = r // 3, c // 3
    for i in range(br * 3, br * 3 + 3):
      for j in range(bc * 3, bc * 3 + 3):
        if board[i][j] == num:
          return False
    return True


class SudokuApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Sudoku Python - Estilo Moderno")
    self.root.geometry("950x750")
    self.root.configure(bg="#f4f4f6")
    self.root.resizable(False, False)

    self.nivel_atual = "Fácil"
    self.erros = 0
    self.tempo_segundos = 0
    self.pausado = False
    self.anotacao_modo = False
    self.historico = []

    self.grid_valores = [[0 for _ in range(9)] for _ in range(9)]
    self.grid_notas = [[set() for _ in range(9)] for _ in range(9)]
    self.celula_selecionada = None

    self.criar_menu_superior()
    self.criar_interface_principal()
    self.iniciar_novo_jogo()
    self.atualizar_tempo()

  def criar_menu_superior(self):
    frame_topo = tk.Frame(self.root, bg="#f4f4f6")
    frame_topo.pack(fill=tk.X, padx=20, pady=12)

    lbl_titulo = tk.Label(
        frame_topo,
        text="Sudoku",
        font=("Segoe UI", 20, "bold"),
        bg="#f4f4f6",
        fg="#2c3e50",
    )
    lbl_titulo.pack(side=tk.LEFT)

    self.frame_dif = tk.Frame(frame_topo, bg="#f4f4f6")
    self.frame_dif.pack(side=tk.LEFT, padx=15)

    self.botoes_dif = {}
    for nivel in [
        "Fácil",
        "Média",
        "Difícil",
        "Especialista",
        "Mestra",
        "Extrema",
    ]:
      btn = tk.Button(
          self.frame_dif,
          text=nivel,
          font=("Segoe UI", 9, "bold"),
          bg="#e4e4e7",
          fg="#333",
          bd=0,
          padx=6,
          pady=4,
          command=lambda n=nivel: self.mudar_dificuldade(n),
      )
      btn.pack(side=tk.LEFT, padx=2)
      self.botoes_dif[nivel] = btn

    frame_status_dir = tk.Frame(frame_topo, bg="#f4f4f6")
    frame_status_dir.pack(side=tk.RIGHT)

    self.btn_pausa = tk.Button(
        frame_status_dir,
        text="⏸️ Pausar",
        font=("Segoe UI", 9, "bold"),
        bg="#e4e4e7",
        bd=0,
        padx=8,
        pady=4,
        command=self.alternar_pausa,
    )
    self.btn_pausa.pack(side=tk.LEFT, padx=10)

    self.lbl_status = tk.Label(
        frame_status_dir,
        text="Erros: 0/3   |   Tempo: 00:00",
        font=("Segoe UI", 11, "bold"),
        bg="#f4f4f6",
        fg="#e74c3c",
    )
    self.lbl_status.pack(side=tk.LEFT)

  def criar_interface_principal(self):
    frame_principal = tk.Frame(self.root, bg="#f4f4f6")
    frame_principal.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    self.frame_tabuleiro = tk.Frame(frame_principal, bg="#2c3e50", bd=3)
    self.frame_tabuleiro.pack(side=tk.LEFT, padx=10)

    self.celulas = [[None for _ in range(9)] for _ in range(9)]
    for r in range(9):
      for c in range(9):
        pt_r = 4 if r % 3 == 0 and r != 0 else 1
        pl_c = 4 if c % 3 == 0 and c != 0 else 1

        lbl = tk.Label(
            self.frame_tabuleiro,
            text="",
            font=("Segoe UI", 15, "bold"),
            width=4,
            height=2,
            bg="#ffffff",
            fg="#2c3e50",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        lbl.grid(row=r, column=c, padx=(pl_c, 1), pady=(pt_r, 1))
        lbl.bind(
            "<Button-1>", lambda event, row=r, col=c: self.selecionar_celula(row, col)
        )
        self.celulas[r][c] = lbl

    frame_lateral = tk.Frame(frame_principal, bg="#f4f4f6", width=280)
    frame_lateral.pack(side=tk.RIGHT, expand=True, fill=tk.Y, padx=10)
    frame_lateral.pack_propagate(False)

    frame_tools = tk.Frame(frame_lateral, bg="#f4f4f6")
    frame_tools.pack(fill=tk.X, pady=5)

    self.btn_anotacao = tk.Button(
        frame_tools,
        text="✏️ Notas",
        font=("Segoe UI", 8, "bold"),
        bg="#e4e4e7",
        bd=0,
        padx=6,
        pady=8,
        command=self.alternar_anotacao,
    )
    self.btn_anotacao.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    tk.Button(
        frame_tools,
        text="↩️ Desfazer",
        font=("Segoe UI", 8, "bold"),
        bg="#e4e4e7",
        bd=0,
        padx=6,
        pady=8,
        command=self.desfazer_jogada,
    ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    tk.Button(
        frame_tools,
        text="🧹 Apagar",
        font=("Segoe UI", 8, "bold"),
        bg="#e4e4e7",
        bd=0,
        padx=6,
        pady=8,
        command=self.apagar_celula,
    ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

    frame_teclado_container = tk.Frame(
        frame_lateral, bg="#ffffff", bd=1, relief=tk.SOLID
    )
    frame_teclado_container.pack(pady=15, padx=5, fill=tk.X)

    frame_teclado = tk.Frame(frame_teclado_container, bg="#ffffff")
    frame_teclado.pack(padx=10, pady=10)

    for i in range(1, 10):
      row_idx = (i - 1) // 3
      col_idx = (i - 1) % 3
      btn_num = tk.Button(
          frame_teclado,
          text=str(i),
          font=("Segoe UI", 15, "bold"),
          width=4,
          height=2,
          bg="#f8f9fa",
          fg="#3498db",
          bd=1,
          relief=tk.SOLID,
          command=lambda n=i: self.inserir_numero(n),
      )
      btn_num.grid(row=row_idx, column=col_idx, padx=4, pady=4)

    tk.Button(
        frame_lateral,
        text="Novo Jogo",
        font=("Segoe UI", 11, "bold"),
        bg="#3498db",
        fg="white",
        bd=0,
        pady=10,
        command=self.iniciar_novo_jogo,
    ).pack(fill=tk.X, pady=10, padx=5)

  def mudar_dificuldade(self, nivel):
    self.nivel_atual = nivel
    self.iniciar_novo_jogo()

  def iniciar_novo_jogo(self):
    for n, btn in self.botoes_dif.items():
      if n == self.nivel_atual:
        btn.config(bg="#3498db", fg="white")
      else:
        btn.config(bg="#e4e4e7", fg="#333")

    self.tabuleiro, self.solucao = SudokuGenerator.gerar_sudoku(
        self.nivel_atual
    )
    self.estado_inicial = [row[:] for row in self.tabuleiro]
    self.grid_valores = [row[:] for row in self.tabuleiro]
    self.grid_notas = [[set() for _ in range(9)] for _ in range(9)]
    self.erros = 0
    self.tempo_segundos = 0
    self.pausado = False
    self.btn_pausa.config(text="⏸️ Pausar", bg="#e4e4e7")
    self.historico.clear()
    self.celula_selecionada = None
    self.atualizar_interface()

  def atualizar_interface(self):
    sel_r, sel_c = (
        self.celula_selecionada if self.celula_selecionada else (-1, -1)
    )
    val_selecionado = (
        self.grid_valores[sel_r][sel_c]
        if self.celula_selecionada
        and self.grid_valores[sel_r][sel_c] != 0
        else None
    )

    for r in range(9):
      for c in range(9):
        val = self.grid_valores[r][c]
        lbl = self.celulas[r][c]

        if self.pausado:
          lbl.config(
              text="***", fg="#bdc3c7", bg="#ecf0f1", font=("Segoe UI", 14)
          )
          continue

        bg_color = "#ffffff"
        mesmo_bloco = (
            sel_r != -1
            and (r // 3 == sel_r // 3)
            and (c // 3 == sel_c // 3)
        )
        if sel_r != -1 and (r == sel_r or c == sel_c or mesmo_bloco):
          bg_color = "#e8f8f5"

        if self.celula_selecionada == (r, c):
          bg_color = "#d5f5e3"
        elif val_selecionado is not None and val == val_selecionado:
          bg_color = "#d4efdf"

        fg_color = "#2c3e50"
        font_style = ("Segoe UI", 15, "bold")
        text_val = ""

        if self.estado_inicial[r][c] != 0:
          fg_color = "#2c3e50"
          font_style = ("Segoe UI", 15, "bold")
          text_val = str(val)
        elif val != 0:
          fg_color = "#2980b9"
          font_style = ("Segoe UI", 15, "bold")
          text_val = str(val)
        else:
          if self.grid_notas[r][c]:
            notas_lista = sorted(list(self.grid_notas[r][c]))
            text_val = " ".join([str(n) for n in notas_lista])
            fg_color = "#c0392b"
            font_style = ("Segoe UI", 9, "bold")
          else:
            text_val = ""
            font_style = ("Segoe UI", 15, "bold")

        lbl.config(
            text=text_val, fg=fg_color, bg=bg_color, font=font_style
        )

    minutos = self.tempo_segundos // 60
    segundos = self.tempo_segundos % 60
    self.lbl_status.config(
        text=f"Erros: {self.erros}/3   |   Tempo: {minutos:02d}:{segundos:02d}"
    )

  def selecionar_celula(self, r, c):
    if self.pausado:
      return
    self.celula_selecionada = (r, c)
    self.atualizar_interface()

  def inserir_numero(self, num):
    if self.pausado or not self.celula_selecionada:
      return
    r, c = self.celula_selecionada

    if self.estado_inicial[r][c] != 0:
      return

    if self.anotacao_modo:
      valor_antigo = self.grid_valores[r][c]
      notas_antigas = self.grid_notas[r][c].copy()
      self.historico.append((r, c, valor_antigo, notas_antigas, self.erros))

      if num in self.grid_notas[r][c]:
        self.grid_notas[r][c].remove(num)
      else:
        self.grid_notas[r][c].add(num)
      self.atualizar_interface()
      return

    valor_antigo = self.grid_valores[r][c]
    notas_antigas = self.grid_notas[r][c].copy()

    if self.solucao[r][c] == num:
      self.grid_valores[r][c] = num
      self.grid_notas[r][c].clear()
      self.historico.append((r, c, valor_antigo, notas_antigas, self.erros))
      self.verificar_vitoria()
    else:
      self.erros += 1
      self.grid_valores[r][c] = num
      self.historico.append((r, c, valor_antigo, notas_antigas, self.erros))
      if self.erros >= 3:
        messagebox.showerror(
            "Fim de Jogo", "Você cometeu 3 erros e perdeu este jogo!"
        )
        self.iniciar_novo_jogo()
        return

    self.atualizar_interface()

  def apagar_celula(self):
    if self.pausado or not self.celula_selecionada:
      return
    r, c = self.celula_selecionada
    if self.estado_inicial[r][c] != 0:
      return

    valor_antigo = self.grid_valores[r][c]
    notas_antigas = self.grid_notas[r][c].copy()
    self.historico.append((r, c, valor_antigo, notas_antigas, self.erros))

    self.grid_valores[r][c] = 0
    self.grid_notas[r][c].clear()
    self.atualizar_interface()

  def desfazer_jogada(self):
    if self.pausado or not self.historico:
      return
    r, c, val_antigo, notas_antigas, erro_antigo = self.historico.pop()
    self.grid_valores[r][c] = val_antigo
    self.grid_notas[r][c] = notas_antigas
    self.erros = max(self.erros, erro_antigo)
    self.atualizar_interface()

  def alternar_anotacao(self):
    if self.pausado:
      return
    self.anotacao_modo = not self.anotacao_modo
    estado = "ON" if self.anotacao_modo else "OFF"
    self.btn_anotacao.config(
        text=f"✏️ Notas: {estado}", bg="#d5f5e3" if self.anotacao_modo else "#e4e4e7"
    )

  def alternar_pausa(self):
    self.pausado = not self.pausado
    if self.pausado:
      self.btn_pausa.config(text="▶️ Continuar", bg="#f1c40f")
    else:
      self.btn_pausa.config(text="⏸️ Pausar", bg="#e4e4e7")
    self.atualizar_interface()

  def atualizar_tempo(self):
    if not self.pausado:
      self.tempo_segundos += 1
      minutos = self.tempo_segundos // 60
      segundos = self.tempo_segundos % 60
      current_text = self.lbl_status.cget("text").split("|")[0].strip()
      self.lbl_status.config(
          text=f"{current_text}   |   Tempo: {minutos:02d}:{segundos:02d}"
      )
    self.root.after(1000, self.atualizar_tempo)

  def verificar_vitoria(self):
    if self.grid_valores == self.solucao:
      messagebox.showinfo(
          "Parabéns!",
          f"Você solucionou o Sudoku com sucesso no nível"
          f" {self.nivel_atual}!",
      )
      self.iniciar_novo_jogo()


if __name__ == "__main__":
  root = tk.Tk()
  app = SudokuApp(root)
  root.mainloop()