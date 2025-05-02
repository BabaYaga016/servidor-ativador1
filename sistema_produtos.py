import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import requests
import uuid
from datetime import datetime
from cryptography.fernet import Fernet
import os

ARQUIVO_CHAVE = "chave.key"
ARQUIVO_ATIVACAO = "data_ativacao.txt"
DIAS_VALIDOS = 31
URL_SERVIDOR = "http://SEU_IP:5000/verificar"  # <- coloque o IP ou domínio aqui

def gerar_chave():
    chave = Fernet.generate_key()
    with open(ARQUIVO_CHAVE, 'wb') as f:
        f.write(chave)

def carregar_chave():
    if not os.path.exists(ARQUIVO_CHAVE):
        gerar_chave()
    with open(ARQUIVO_CHAVE, 'rb') as f:
        return f.read()

def obter_mac_address():
    return "mac:" + hex(uuid.getnode())

def salvar_data_ativacao():
    chave = carregar_chave()
    f = Fernet(chave)
    data = datetime.now().strftime('%Y-%m-%d')
    criptografado = f.encrypt(data.encode())
    with open(ARQUIVO_ATIVACAO, 'wb') as f:
        f.write(criptografado)

def ler_data_ativacao():
    if not os.path.exists(ARQUIVO_ATIVACAO):
        return None
    chave = carregar_chave()
    f = Fernet(chave)
    with open(ARQUIVO_ATIVACAO, 'rb') as arq:
        try:
            data = f.decrypt(arq.read()).decode()
            return datetime.strptime(data, '%Y-%m-%d')
        except:
            return None

def sistema_esta_ativo():
    data = ler_data_ativacao()
    if not data:
        return False
    return (datetime.now() - data).days <= DIAS_VALIDOS

def tentar_ativar_online():
    mac = obter_mac_address()
    try:
        resposta = requests.post(URL_SERVIDOR, json={"mac": mac})
        if resposta.status_code == 200 and resposta.json().get("autorizado"):
            salvar_data_ativacao()
            return True
    except:
        pass
    return False

# ---------------- USO FINAL ------------------
if sistema_esta_ativo():
    print("✅ Sistema ativo")
else:
    print("❌ Sistema expirado ou não ativado")
    print("🔄 Tentando ativar online...")
    if tentar_ativar_online():
        print("✅ Sistema reativado com sucesso!")
    else:
        print("❌ Ativação negada. Contate o suporte.")

# Paleta de cores profissional
CORES = {
    "fundo": "#f8f9fa",
    "fundo_topo": "#343a40",
    "texto_topo": "#ffffff",
    "botao_primario": "#007bff",
    "botao_sucesso": "#28a745",
    "botao_perigo": "#dc3545",
    "botao_aviso": "#ffc107",
    "botao_info": "#17a2b8",
    "botao_texto": "#ffffff",
    "quadro": "#e9ecef",
    "texto": "#212529",
    "destaque": "#fd7e14",
    "borda": "#dee2e6"
}

class SistemaGestaoLoja:
    def __init__(self, root):
        self.root = root
        self.root.title("Tecno Store - Sistema de Gestão Comercial")
        self.root.geometry("1200x750")
        self.root.configure(bg=CORES["fundo"])
        self.root.minsize(1000, 650)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Inicializar banco de dados e interface
        self.criar_banco_dados()
        self.inicializar_interface()
    
    def criar_banco_dados(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        
        # Verificar se a tabela produtos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos'")
        if not cursor.fetchone():
            # Criar tabela produtos se não existir
            cursor.execute('''
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco_compra REAL NOT NULL CHECK(preco_compra > 0),
                preco_venda REAL NOT NULL CHECK(preco_venda > 0),
                quantidade INTEGER NOT NULL DEFAULT 0 CHECK(quantidade >= 0),
                categoria TEXT,
                fornecedor TEXT,
                data_cadastro TEXT NOT NULL,
                data_atualizacao TEXT
            )''')
        
        # Verificar se a tabela vendas existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vendas'")
        if not cursor.fetchone():
            # Criar tabela vendas se não existir
            cursor.execute('''
            CREATE TABLE vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                produto_codigo TEXT NOT NULL,
                produto_nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL CHECK(quantidade > 0),
                preco_unitario REAL NOT NULL CHECK(preco_unitario > 0),
                total REAL NOT NULL CHECK(total > 0),
                forma_pagamento TEXT NOT NULL,
                data_venda TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )''')
        
        # Verificar se a tabela clientes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
        if not cursor.fetchone():
            # Criar tabela clientes se não existir
            cursor.execute('''
            CREATE TABLE clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                data_cadastro TEXT NOT NULL
            )''')
        
        # Verificar se a tabela fornecedores existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fornecedores'")
        if not cursor.fetchone():
            # Criar tabela fornecedores se não existir
            cursor.execute('''
            CREATE TABLE fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                data_cadastro TEXT NOT NULL
            )''')
        
        conn.commit()
        conn.close()
    
    def inicializar_interface(self):
        """Configura os elementos principais da interface gráfica"""
        self.criar_barra_superior()
        self.criar_area_navegacao()
        self.criar_area_conteudo()
        self.exibir_dashboard()
    
    def criar_barra_superior(self):
        """Cria a barra superior com título e informações do sistema"""
        frame_topo = tk.Frame(
            self.root, 
            bg=CORES["fundo_topo"], 
            height=80,
            padx=20
        )
        frame_topo.pack(fill="x")
        
        lbl_titulo = tk.Label(
            frame_topo, 
            text="Tecno Store - Sistema de Gestão Comercial", 
            font=('Segoe UI', 18, 'bold'), 
            bg=CORES["fundo_topo"], 
            fg=CORES["texto_topo"]
        )
        lbl_titulo.pack(side="left", padx=10)
        
        frame_usuario = tk.Frame(frame_topo, bg=CORES["fundo_topo"])
        frame_usuario.pack(side="right", padx=10)
        
        lbl_usuario = tk.Label(
            frame_usuario, 
            text="Usuário: Admin", 
            font=('Segoe UI', 10), 
            bg=CORES["fundo_topo"], 
            fg=CORES["texto_topo"]
        )
        lbl_usuario.pack(side="left", padx=5)
        
        lbl_data = tk.Label(
            frame_usuario, 
            text=self.obter_data_atual(), 
            font=('Segoe UI', 10), 
            bg=CORES["fundo_topo"], 
            fg=CORES["texto_topo"]
        )
        lbl_data.pack(side="left", padx=5)
    
    def criar_area_navegacao(self):
        """Cria o painel de navegação lateral"""
        frame_principal = tk.Frame(self.root, bg=CORES["fundo"])
        frame_principal.pack(fill="both", expand=True)
        
        frame_nav = tk.Frame(
            frame_principal, 
            bg=CORES["fundo_topo"], 
            width=200,
            padx=10,
            pady=20
        )
        frame_nav.pack(side="left", fill="y")
        frame_nav.pack_propagate(False)
        
        botoes_nav = [
            ("Dashboard", self.exibir_dashboard),
            ("Produtos", self.abrir_modulo_produtos),
            ("Vendas", self.abrir_modulo_vendas),
            ("Clientes", self.abrir_modulo_clientes),
            ("Fornecedores", self.abrir_modulo_fornecedores),
            ("Estoque", self.abrir_modulo_estoque),
            ("Relatórios", self.abrir_modulo_relatorios),
            ("Configurações", self.abrir_modulo_configuracoes)
        ]
        
        for texto, comando in botoes_nav:
            btn = tk.Button(
                frame_nav, 
                text=f" {texto}", 
                command=comando,
                anchor="w",
                padx=10,
                bg=CORES["fundo_topo"],
                fg=CORES["texto_topo"],
                activebackground="#495057",
                activeforeground="#ffffff",
                font=('Segoe UI', 11),
                relief="flat",
                bd=0
            )
            btn.pack(fill="x", pady=2)
        
        btn_sair = tk.Button(
            frame_nav, 
            text=" Sair", 
            command=self.sair_sistema,
            anchor="w",
            padx=10,
            bg="#dc3545",
            fg=CORES["texto_topo"],
            activebackground="#c82333",
            activeforeground="#ffffff",
            font=('Segoe UI', 11),
            relief="flat",
            bd=0
        )
        btn_sair.pack(side="bottom", fill="x", pady=(10, 0))
    
    def criar_area_conteudo(self):
        """Cria a área de conteúdo principal"""
        # Encontra o frame principal (que contém a barra de navegação e conteúdo)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_children() and isinstance(widget.winfo_children()[0], tk.Frame):
                frame_principal = widget
                break
        else:
            frame_principal = tk.Frame(self.root, bg=CORES["fundo"])
            frame_principal.pack(fill="both", expand=True)
        
        self.frame_conteudo = tk.Frame(
            frame_principal, 
            bg=CORES["fundo"],
            padx=20,
            pady=20
        )
        self.frame_conteudo.pack(side="right", fill="both", expand=True)
    
    def limpar_conteudo(self):
        """Remove todos os widgets do frame de conteúdo"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()
    
    def exibir_dashboard(self):
        """Exibe o painel de controle inicial"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Dashboard", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Cards de métricas
        frame_metricas = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_metricas.pack(fill="x", pady=(0, 20))
        
        metricas = [
            ("Total de Produtos", self.contar_produtos(), CORES["botao_primario"]),
            ("Produtos em Estoque", self.contar_estoque(), CORES["botao_sucesso"]),
            ("Vendas Hoje", self.contar_vendas_hoje(), CORES["botao_perigo"]),
            ("Faturamento Mensal", f"R$ {self.calcular_faturamento_mensal():,.2f}", CORES["botao_aviso"]),
            ("Clientes Cadastrados", self.contar_clientes(), CORES["botao_info"])
        ]
        
        for i, (titulo, valor, cor) in enumerate(metricas):
            card = tk.Frame(
                frame_metricas, 
                bg=cor,
                bd=0,
                relief="groove",
                highlightbackground=CORES["borda"],
                highlightthickness=1
            )
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            
            # Conteúdo do card
            frame_card = tk.Frame(card, bg="white")
            frame_card.pack(padx=1, pady=1, fill="both", expand=True)
            
            tk.Label(
                frame_card, 
                text=titulo, 
                bg="white", 
                font=('Segoe UI', 9)
            ).pack(pady=(10, 5))
            
            tk.Label(
                frame_card, 
                text=valor, 
                bg="white", 
                font=('Segoe UI', 14, 'bold')
            ).pack(pady=(0, 10))
            
            frame_metricas.grid_columnconfigure(i, weight=1, uniform="metricas")
        
        # Gráficos e últimas vendas
        frame_graficos = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_graficos.pack(fill="both", expand=True)
        
        # Frame de gráficos (simulado)
        frame_grafico_principal = tk.Frame(
            frame_graficos, 
            bg="white",
            bd=1,
            relief="solid",
            highlightbackground=CORES["borda"]
        )
        frame_grafico_principal.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(
            frame_grafico_principal, 
            text="Desempenho de Vendas (Últimos 30 dias)", 
            bg="white", 
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=10)
        
        # Frame de últimas vendas
        frame_ultimas_vendas = tk.Frame(
            frame_graficos, 
            bg="white",
            width=300,
            bd=1,
            relief="solid",
            highlightbackground=CORES["borda"]
        )
        frame_ultimas_vendas.pack(side="right", fill="y")
        frame_ultimas_vendas.pack_propagate(False)
        
        tk.Label(
            frame_ultimas_vendas, 
            text="Últimas Vendas", 
            bg="white", 
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=10)
                  
    # Métodos auxiliares para o dashboard
    def obter_data_atual(self):
        """Retorna a data atual formatada"""
        return datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def contar_produtos(self):
        """Retorna o total de produtos cadastrados"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total = cursor.fetchone()[0]
        conn.close()
        return total
    
    def contar_estoque(self):
        """Retorna a soma total de itens em estoque"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantidade) FROM produtos")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total
    
    def contar_vendas_hoje(self):
        """Retorna o número de vendas realizadas hoje"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vendas WHERE date(data_venda) = date('now')")
        total = cursor.fetchone()[0]
        conn.close()
        return total
    
    def calcular_faturamento_mensal(self):
        """Calcula o faturamento total do mês atual"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM vendas WHERE strftime('%m', data_venda) = strftime('%m', 'now')")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total
    
    def contar_clientes(self):
        """Retorna o total de clientes cadastrados"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
        conn.close()
        return total
    
    # Métodos dos módulos do sistema
    def abrir_modulo_produtos(self):
        """Abre o módulo de gerenciamento de produtos"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Gerenciamento de Produtos", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Barra de ferramentas
        frame_ferramentas = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_ferramentas.pack(fill="x", pady=(0, 10))
        
        # Botões de ação
        btn_novo = tk.Button(
            frame_ferramentas, 
            text="Novo Produto", 
            command=self.cadastrar_produto,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_novo.pack(side="left", padx=5)
        
        btn_editar = tk.Button(
            frame_ferramentas, 
            text="Editar", 
            command=self.editar_produto,
            bg=CORES["botao_primario"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_editar.pack(side="left", padx=5)
        
        btn_excluir = tk.Button(
            frame_ferramentas, 
            text="Excluir", 
            command=self.excluir_produto,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_excluir.pack(side="left", padx=5)
        
        # Barra de pesquisa
        frame_pesquisa = tk.Frame(
            frame_ferramentas, 
            bg=CORES["fundo"]
        )
        frame_pesquisa.pack(side="right")
        
        self.var_pesquisa = tk.StringVar()
        entry_pesquisa = tk.Entry(
            frame_pesquisa, 
            textvariable=self.var_pesquisa,
            width=30,
            font=('Segoe UI', 10),
            relief="solid",
            bd=1
        )
        entry_pesquisa.pack(side="left", padx=5)
        
        btn_pesquisar = tk.Button(
            frame_pesquisa, 
            text="Pesquisar", 
            command=self.pesquisar_produtos,
            bg=CORES["botao_info"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_pesquisar.pack(side="left")
        
        # Tabela de produtos
        frame_tabela = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_tabela.pack(fill="both", expand=True)
        
        # Configurar Treeview
        colunas = (
            "ID", "Código", "Nome", "Preço Compra", 
            "Preço Venda", "Estoque", "Categoria", "Fornecedor"
        )
        
        self.tree_produtos = ttk.Treeview(
            frame_tabela, 
            columns=colunas, 
            show="headings",
            selectmode="browse"
        )
        
        # Configurar colunas
        larguras = [50, 80, 200, 90, 90, 70, 120, 120]
        for col, larg in zip(colunas, larguras):
            self.tree_produtos.heading(col, text=col)
            self.tree_produtos.column(col, width=larg, anchor="center")
        
        # Barra de rolagem
        scroll_y = ttk.Scrollbar(
            frame_tabela, 
            orient="vertical", 
            command=self.tree_produtos.yview
        )
        self.tree_produtos.configure(yscrollcommand=scroll_y.set)
        
        # Layout
        self.tree_produtos.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        # Carregar produtos
        self.carregar_produtos()
        
        # Configurar estilo
        self.style.configure("Treeview", font=('Segoe UI', 10))
        self.style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
    
    def carregar_produtos(self, filtro=None):
        """Carrega os produtos na tabela, opcionalmente com filtro"""
        # Limpar tabela
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        
        # Buscar produtos no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            if filtro and filtro.strip():
                query = '''
                    SELECT id, codigo, nome, preco_compra, preco_venda, 
                           quantidade, categoria, fornecedor 
                    FROM produtos 
                    WHERE nome LIKE ? OR codigo LIKE ? OR categoria LIKE ?
                    ORDER BY nome
                '''
                params = (f'%{filtro.strip()}%', f'%{filtro.strip()}%', f'%{filtro.strip()}%')
            else:
                query = '''
                    SELECT id, codigo, nome, preco_compra, preco_venda, 
                           quantidade, categoria, fornecedor 
                    FROM produtos 
                    ORDER BY nome
                '''
                params = ()
            
            cursor.execute(query, params)
            produtos = cursor.fetchall()
            
            # Adicionar produtos na tabela
            for produto in produtos:
                # Formatar preços
                produto = list(produto)
                produto[3] = f"R$ {produto[3]:.2f}".replace(".", ",")
                produto[4] = f"R$ {produto[4]:.2f}".replace(".", ",")
                self.tree_produtos.insert("", "end", values=produto)
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar os produtos:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def cadastrar_produto(self):
        """Abre o formulário para cadastrar um novo produto"""
        self.janela_produto = tk.Toplevel()
        self.janela_produto.title("Cadastrar Novo Produto")
        self.janela_produto.geometry("500x600")
        self.janela_produto.resizable(False, False)
        self.janela_produto.grab_set()
        
        # Variáveis do formulário
        self.var_codigo = tk.StringVar()
        self.var_nome = tk.StringVar()
        self.var_descricao = tk.StringVar()
        self.var_preco_compra = tk.StringVar()
        self.var_preco_venda = tk.StringVar()
        self.var_quantidade = tk.StringVar(value="0")
        self.var_categoria = tk.StringVar()
        self.var_fornecedor = tk.StringVar()
        
        # Frame principal
        frame_principal = tk.Frame(self.janela_produto, padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)
        
        # Título
        tk.Label(
            frame_principal, 
            text="Informações do Produto", 
            font=('Segoe UI', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Campos do formulário
        campos = [
            ("Código*", self.var_codigo, 1),
            ("Nome*", self.var_nome, 2),
            ("Descrição", self.var_descricao, 3),
            ("Preço de Compra*", self.var_preco_compra, 4),
            ("Preço de Venda*", self.var_preco_venda, 5),
            ("Quantidade*", self.var_quantidade, 6),
            ("Categoria", self.var_categoria, 7),
            ("Fornecedor", self.var_fornecedor, 8)
        ]
        
        for i, (label, var, row) in enumerate(campos):
            tk.Label(
                frame_principal, 
                text=label, 
                font=('Segoe UI', 10)
            ).grid(row=row, column=0, sticky="w", pady=(10, 0))
            
            if label == "Descrição":
                entry = tk.Text(
                    frame_principal, 
                    width=40, 
                    height=4,
                    font=('Segoe UI', 10),
                    wrap="word"
                )
                entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
                self.entry_descricao = entry
            else:
                entry = tk.Entry(
                    frame_principal, 
                    textvariable=var,
                    width=40,
                    font=('Segoe UI', 10)
                )
                entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
        
        # Configurar grid
        for i in range(9):
            frame_principal.grid_rowconfigure(i, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(1, weight=3)
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.grid(row=9, column=0, columnspan=2, pady=20)
        
        btn_salvar = tk.Button(
            frame_botoes, 
            text="Salvar", 
            command=self.salvar_produto,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10, 'bold'),
            width=15
        )
        btn_salvar.pack(side="left", padx=10)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_produto.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=15
        )
        btn_cancelar.pack(side="right", padx=10)
    
    def salvar_produto(self):
        """Valida e salva o novo produto no banco de dados"""
        # Validação dos campos obrigatórios
        campos_obrigatorios = {
            "Código": self.var_codigo.get(),
            "Nome": self.var_nome.get(),
            "Preço de Compra": self.var_preco_compra.get(),
            "Preço de Venda": self.var_preco_venda.get(),
            "Quantidade": self.var_quantidade.get()
        }
        
        for campo, valor in campos_obrigatorios.items():
            if not valor.strip():
                messagebox.showerror(
                    "Erro de Validação", 
                    f"O campo {campo} é obrigatório!"
                )
                return
        
        # Validação dos valores numéricos
        try:
            preco_compra = float(self.var_preco_compra.get().replace(",", "."))
            preco_venda = float(self.var_preco_venda.get().replace(",", "."))
            quantidade = int(self.var_quantidade.get())
            
            if preco_compra <= 0 or preco_venda <= 0:
                raise ValueError("Preços devem ser maiores que zero")
            
            if quantidade < 0:
                raise ValueError("Quantidade não pode ser negativa")
                
            if preco_venda < preco_compra:
                if not messagebox.askyesno(
                    "Aviso", 
                    "Preço de venda é menor que o preço de compra! Deseja continuar mesmo assim?"
                ):
                    return
                    
        except ValueError as e:
            messagebox.showerror(
                "Erro de Validação", 
                f"Valor inválido: {str(e)}"
            )
            return
        
        # Obter descrição do Text widget
        descricao = self.entry_descricao.get("1.0", "end-1c")
        
        # Obter data atual
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Inserir no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO produtos (
                    codigo, nome, descricao, preco_compra, preco_venda, 
                    quantidade, categoria, fornecedor, data_cadastro
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.var_codigo.get().strip(),
                self.var_nome.get().strip(),
                descricao.strip(),
                preco_compra,
                preco_venda,
                quantidade,
                self.var_categoria.get().strip(),
                self.var_fornecedor.get().strip(),
                data_atual
            ))
            
            conn.commit()
            messagebox.showinfo(
                "Sucesso", 
                "Produto cadastrado com sucesso!"
            )
            self.janela_produto.destroy()
            self.carregar_produtos()  # Atualizar a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro", 
                "Já existe um produto com este código!"
            )
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível salvar o produto:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def editar_produto(self):
        """Abre o formulário para editar um produto existente"""
        # Verificar seleção
        selecao = self.tree_produtos.selection()
        if not selecao:
            messagebox.showwarning(
                "Aviso", 
                "Selecione um produto para editar!"
            )
            return
        
        # Obter ID do produto selecionado
        item = self.tree_produtos.item(selecao)
        produto_id = item['values'][0]
        
        # Buscar produto no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
            produto = cursor.fetchone()
            
            if not produto:
                messagebox.showerror(
                    "Erro", 
                    "Produto não encontrado no banco de dados!"
                )
                return
            
            # Criar janela de edição
            self.janela_edicao = tk.Toplevel()
            self.janela_edicao.title(f"Editar Produto - ID: {produto_id}")
            self.janela_edicao.geometry("500x600")
            self.janela_edicao.resizable(False, False)
            self.janela_edicao.grab_set()
            
            # Variáveis do formulário
            self.var_editar_id = produto[0]
            self.var_editar_codigo = tk.StringVar(value=produto[1])
            self.var_editar_nome = tk.StringVar(value=produto[2])
            self.var_editar_descricao = produto[3] if produto[3] else ""
            self.var_editar_preco_compra = tk.StringVar(value=f"{produto[4]:.2f}")
            self.var_editar_preco_venda = tk.StringVar(value=f"{produto[5]:.2f}")
            self.var_editar_quantidade = tk.StringVar(value=str(produto[6]))
            self.var_editar_categoria = tk.StringVar(value=produto[7] if produto[7] else "")
            self.var_editar_fornecedor = tk.StringVar(value=produto[8] if produto[8] else "")
            
            # Frame principal
            frame_principal = tk.Frame(self.janela_edicao, padx=20, pady=20)
            frame_principal.pack(fill="both", expand=True)
            
            # Título
            tk.Label(
                frame_principal, 
                text="Editar Produto", 
                font=('Segoe UI', 14, 'bold')
            ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
            
            # Campos do formulário
            campos = [
                ("Código*", self.var_editar_codigo, 1),
                ("Nome*", self.var_editar_nome, 2),
                ("Descrição", None, 3),
                ("Preço de Compra*", self.var_editar_preco_compra, 4),
                ("Preço de Venda*", self.var_editar_preco_venda, 5),
                ("Quantidade*", self.var_editar_quantidade, 6),
                ("Categoria", self.var_editar_categoria, 7),
                ("Fornecedor", self.var_editar_fornecedor, 8)
            ]
            
            for i, (label, var, row) in enumerate(campos):
                tk.Label(
                    frame_principal, 
                    text=label, 
                    font=('Segoe UI', 10)
                ).grid(row=row, column=0, sticky="w", pady=(10, 0))
                
                if label == "Descrição":
                    entry = tk.Text(
                        frame_principal, 
                        width=40, 
                        height=4,
                        font=('Segoe UI', 10),
                        wrap="word"
                    )
                    entry.insert("1.0", self.var_editar_descricao)
                    entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
                    self.entry_editar_descricao = entry
                else:
                    entry = tk.Entry(
                        frame_principal, 
                        textvariable=var,
                        width=40,
                        font=('Segoe UI', 10)
                    )
                    entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
            
            # Configurar grid
            for i in range(9):
                frame_principal.grid_rowconfigure(i, weight=1)
            frame_principal.grid_columnconfigure(0, weight=1)
            frame_principal.grid_columnconfigure(1, weight=3)
            
            # Frame de botões
            frame_botoes = tk.Frame(frame_principal)
            frame_botoes.grid(row=9, column=0, columnspan=2, pady=20)
            
            btn_salvar = tk.Button(
                frame_botoes, 
                text="Salvar Alterações", 
                command=self.salvar_edicao_produto,
                bg=CORES["botao_sucesso"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10, 'bold'),
                width=20
            )
            btn_salvar.pack(side="left", padx=10)
            
            btn_cancelar = tk.Button(
                frame_botoes, 
                text="Cancelar", 
                command=self.janela_edicao.destroy,
                bg=CORES["botao_perigo"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10),
                width=20
            )
            btn_cancelar.pack(side="right", padx=10)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar o produto:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def salvar_edicao_produto(self):
        """Salva as alterações do produto no banco de dados"""
        # Validação dos campos obrigatórios
        campos_obrigatorios = {
            "Código": self.var_editar_codigo.get(),
            "Nome": self.var_editar_nome.get(),
            "Preço de Compra": self.var_editar_preco_compra.get(),
            "Preço de Venda": self.var_editar_preco_venda.get(),
            "Quantidade": self.var_editar_quantidade.get()
        }
        
        for campo, valor in campos_obrigatorios.items():
            if not valor.strip():
                messagebox.showerror(
                    "Erro de Validação", 
                    f"O campo {campo} é obrigatório!"
                )
                return
        
        # Validação dos valores numéricos
        try:
            preco_compra = float(self.var_editar_preco_compra.get().replace(",", "."))
            preco_venda = float(self.var_editar_preco_venda.get().replace(",", "."))
            quantidade = int(self.var_editar_quantidade.get())
            
            if preco_compra <= 0 or preco_venda <= 0:
                raise ValueError("Preços devem ser maiores que zero")
            
            if quantidade < 0:
                raise ValueError("Quantidade não pode ser negativa")
                
            if preco_venda < preco_compra:
                if not messagebox.askyesno(
                    "Aviso", 
                    "Preço de venda é menor que o preço de compra! Deseja continuar mesmo assim?"
                ):
                    return
                    
        except ValueError as e:
            messagebox.showerror(
                "Erro de Validação", 
                f"Valor inválido: {str(e)}"
            )
            return
        
        # Obter descrição do Text widget
        descricao = self.entry_editar_descricao.get("1.0", "end-1c")
        
        # Obter data atual para atualização
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Atualizar no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE produtos SET
                    codigo = ?,
                    nome = ?,
                    descricao = ?,
                    preco_compra = ?,
                    preco_venda = ?,
                    quantidade = ?,
                    categoria = ?,
                    fornecedor = ?,
                    data_atualizacao = ?
                WHERE id = ?
            ''', (
                self.var_editar_codigo.get().strip(),
                self.var_editar_nome.get().strip(),
                descricao.strip(),
                preco_compra,
                preco_venda,
                quantidade,
                self.var_editar_categoria.get().strip(),
                self.var_editar_fornecedor.get().strip(),
                data_atual,
                self.var_editar_id
            ))
            
            conn.commit()
            messagebox.showinfo(
                "Sucesso", 
                "Produto atualizado com sucesso!"
            )
            self.janela_edicao.destroy()
            self.carregar_produtos()  # Atualizar a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erro", 
                "Já existe um produto com este código!"
            )
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível atualizar o produto:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def excluir_produto(self):
        """Exclui o produto selecionado após confirmação"""
        selecao = self.tree_produtos.selection()
        if not selecao:
            messagebox.showwarning(
                "Aviso", 
                "Selecione um produto para excluir!"
            )
            return
        
        # Obter ID do produto selecionado
        item = self.tree_produtos.item(selecao)
        produto_id = item['values'][0]
        produto_nome = item['values'][2]
        
        # Confirmar exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o produto:\n\n{produto_nome}?"
        ):
            return
        
        # Excluir do banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo(
                    "Sucesso", 
                    "Produto excluído com sucesso!"
                )
                self.carregar_produtos()
            else:
                messagebox.showerror(
                    "Erro", 
                    "Produto não encontrado!"
                )
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro", 
                f"Não foi possível excluir o produto:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def pesquisar_produtos(self):
        """Filtra os produtos com base no termo de pesquisa"""
        termo = self.var_pesquisa.get().strip()
        self.carregar_produtos(termo if termo else None)
    
    def abrir_modulo_vendas(self):
        """Abre o módulo de vendas"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Módulo de Vendas", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Frame principal
        frame_principal = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_principal.pack(fill="both", expand=True)
        
        # Frame de seleção de produtos
        frame_produtos = tk.Frame(
            frame_principal, 
            bg=CORES["fundo"],
            padx=10,
            pady=10
        )
        frame_produtos.pack(fill="x")
        
        tk.Label(
            frame_produtos, 
            text="Selecione o Produto:", 
            font=('Segoe UI', 10),
            bg=CORES["fundo"]
        ).pack(side="left", padx=5)
        
        self.var_produto_venda = tk.StringVar()
        self.combo_produtos = ttk.Combobox(
            frame_produtos,
            textvariable=self.var_produto_venda,
            font=('Segoe UI', 10),
            width=40,
            state="readonly"
        )
        self.combo_produtos.pack(side="left", padx=5)
        
        # Carregar produtos no combobox
        self.carregar_produtos_combobox()
        
        btn_adicionar = tk.Button(
            frame_produtos, 
            text="Adicionar", 
            command=self.adicionar_produto_venda,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_adicionar.pack(side="left", padx=5)
        
        # Frame de itens da venda
        frame_itens = tk.Frame(
            frame_principal, 
            bg=CORES["fundo"],
            padx=10,
            pady=10
        )
        frame_itens.pack(fill="both", expand=True)
        
        # Tabela de itens da venda
        colunas = ("Produto", "Quantidade", "Preço Unitário", "Subtotal")
        self.tree_itens = ttk.Treeview(
            frame_itens, 
            columns=colunas, 
            show="headings",
            selectmode="browse"
        )
        
        for col in colunas:
            self.tree_itens.heading(col, text=col)
            self.tree_itens.column(col, width=120, anchor="center")
        
        scroll_y = ttk.Scrollbar(
            frame_itens, 
            orient="vertical", 
            command=self.tree_itens.yview
        )
        self.tree_itens.configure(yscrollcommand=scroll_y.set)
        
        self.tree_itens.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        # Frame de total e pagamento
        frame_total = tk.Frame(
            frame_principal, 
            bg=CORES["fundo"],
            padx=10,
            pady=10
        )
        frame_total.pack(fill="x")
        
        tk.Label(
            frame_total, 
            text="Total da Venda:", 
            font=('Segoe UI', 12),
            bg=CORES["fundo"]
        ).pack(side="left", padx=5)
        
        self.var_total_venda = tk.StringVar(value="R$ 0,00")
        lbl_total = tk.Label(
            frame_total, 
            textvariable=self.var_total_venda, 
            font=('Segoe UI', 12, 'bold'),
            bg=CORES["fundo"]
        )
        lbl_total.pack(side="left", padx=5)
        
        tk.Label(
            frame_total, 
            text="Forma de Pagamento:", 
            font=('Segoe UI', 10),
            bg=CORES["fundo"]
        ).pack(side="left", padx=(20, 5))
        
        self.var_forma_pagamento = tk.StringVar(value="Dinheiro")
        opcoes_pagamento = ["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Transferência"]
        combo_pagamento = ttk.Combobox(
            frame_total,
            textvariable=self.var_forma_pagamento,
            values=opcoes_pagamento,
            font=('Segoe UI', 10),
            width=20,
            state="readonly"
        )
        combo_pagamento.pack(side="left", padx=5)
        
        btn_finalizar = tk.Button(
            frame_total, 
            text="Finalizar Venda", 
            command=self.finalizar_venda,
            bg=CORES["botao_primario"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 12, 'bold'),
            relief="flat",
            padx=20
        )
        btn_finalizar.pack(side="right", padx=10)
    
    def carregar_produtos_combobox(self):
        """Carrega os produtos disponíveis no combobox de vendas"""
        conn = sqlite3.connect('loja.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo, nome, preco_venda, quantidade FROM produtos WHERE quantidade > 0 ORDER BY nome")
        produtos = cursor.fetchall()
        conn.close()
        
        # Formatar para exibição no combobox
        opcoes = [f"{p[1]} - {p[2]} (R$ {p[3]:.2f} | Estoque: {p[4]})" for p in produtos]
        self.combo_produtos['values'] = opcoes
        self.produtos_disponiveis = produtos  # Guardar os dados completos para referência
        
        if opcoes:
            self.combo_produtos.current(0)
    
    def adicionar_produto_venda(self):
        """Adiciona um produto à lista de itens da venda"""
        selecao = self.combo_produtos.current()
        if selecao == -1:
            messagebox.showwarning("Aviso", "Selecione um produto para adicionar!")
            return
        
        produto = self.produtos_disponiveis[selecao]
        
        # Janela para quantidade
        self.janela_quantidade = tk.Toplevel()
        self.janela_quantidade.title("Quantidade")
        self.janela_quantidade.geometry("300x150")
        self.janela_quantidade.resizable(False, False)
        self.janela_quantidade.grab_set()
        
        tk.Label(
            self.janela_quantidade, 
            text=f"Quantidade para {produto[2]}", 
            font=('Segoe UI', 10)
        ).pack(pady=10)
        
        self.var_quantidade_venda = tk.StringVar(value="1")
        spin_quantidade = tk.Spinbox(
            self.janela_quantidade,
            from_=1,
            to=produto[4],  # Quantidade em estoque
            textvariable=self.var_quantidade_venda,
            font=('Segoe UI', 12),
            width=5
        )
        spin_quantidade.pack(pady=5)
        
        frame_botoes = tk.Frame(self.janela_quantidade)
        frame_botoes.pack(pady=10)
        
        btn_confirmar = tk.Button(
            frame_botoes, 
            text="Confirmar", 
            command=lambda: self.confirmar_quantidade(produto),
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=10
        )
        btn_confirmar.pack(side="left", padx=5)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_quantidade.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=10
        )
        btn_cancelar.pack(side="right", padx=5)
    
    def confirmar_quantidade(self, produto):
        """Confirma a quantidade do produto a ser vendido"""
        try:
            quantidade = int(self.var_quantidade_venda.get())
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva")
            if quantidade > produto[4]:  # Quantidade em estoque
                raise ValueError("Quantidade indisponível em estoque")
                
            # Adicionar à lista de itens
            subtotal = produto[3] * quantidade
            self.tree_itens.insert("", "end", values=(
                produto[2],  # Nome
                quantidade,
                f"R$ {produto[3]:.2f}",
                f"R$ {subtotal:.2f}"
            ))
            
            # Atualizar total
            self.atualizar_total_venda()
            
            self.janela_quantidade.destroy()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Quantidade inválida: {str(e)}")
    
    def atualizar_total_venda(self):
        """Calcula e atualiza o total da venda"""
        total = 0.0
        for item in self.tree_itens.get_children():
            valores = self.tree_itens.item(item, 'values')
            subtotal = float(valores[3].replace("R$ ", "").replace(",", "."))
            total += subtotal
        
        self.var_total_venda.set(f"R$ {total:.2f}".replace(".", ","))
    
    def finalizar_venda(self):
        """Finaliza a venda e registra no banco de dados"""
        if not self.tree_itens.get_children():
            messagebox.showwarning("Aviso", "Adicione pelo menos um item à venda!")
            return
        
        # Confirmar venda
        if not messagebox.askyesno("Confirmar", "Deseja finalizar esta venda?"):
            return
        
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            data_venda = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Registrar cada item da venda
            for item in self.tree_itens.get_children():
                valores = self.tree_itens.item(item, 'values')
                produto_nome = valores[0]
                quantidade = int(valores[1])
                preco_unitario = float(valores[2].replace("R$ ", "").replace(",", "."))
                total = float(valores[3].replace("R$ ", "").replace(",", "."))
                
                # Obter ID do produto
                cursor.execute("SELECT id, codigo FROM produtos WHERE nome = ?", (produto_nome,))
                produto = cursor.fetchone()
                
                if produto:
                    # Registrar venda
                    cursor.execute('''
                        INSERT INTO vendas (
                            produto_id, produto_codigo, produto_nome, quantidade, 
                            preco_unitario, total, forma_pagamento, data_venda
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        produto[0], produto[1], produto_nome, quantidade,
                        preco_unitario, total, self.var_forma_pagamento.get(), data_venda
                    ))
                    
                    # Atualizar estoque
                    cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", 
                                 (quantidade, produto[0]))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            
            # Limpar venda atual
            for item in self.tree_itens.get_children():
                self.tree_itens.delete(item)
            self.var_total_venda.set("R$ 0,00")
            self.carregar_produtos_combobox()  # Atualizar estoque
            
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Falha ao registrar venda:\n{str(e)}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    def abrir_modulo_clientes(self):
        """Abre o módulo de gerenciamento de clientes"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Gerenciamento de Clientes", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Barra de ferramentas
        frame_ferramentas = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_ferramentas.pack(fill="x", pady=(0, 10))
        
        # Botões de ação
        btn_novo = tk.Button(
            frame_ferramentas, 
            text="Novo Cliente", 
            command=self.cadastrar_cliente,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_novo.pack(side="left", padx=5)
        
        btn_editar = tk.Button(
            frame_ferramentas, 
            text="Editar", 
            command=self.editar_cliente,
            bg=CORES["botao_primario"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_editar.pack(side="left", padx=5)
        
        btn_excluir = tk.Button(
            frame_ferramentas, 
            text="Excluir", 
            command=self.excluir_cliente,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_excluir.pack(side="left", padx=5)
        
        # Barra de pesquisa
        frame_pesquisa = tk.Frame(
            frame_ferramentas, 
            bg=CORES["fundo"]
        )
        frame_pesquisa.pack(side="right")
        
        self.var_pesquisa_cliente = tk.StringVar()
        entry_pesquisa = tk.Entry(
            frame_pesquisa, 
            textvariable=self.var_pesquisa_cliente,
            width=30,
            font=('Segoe UI', 10),
            relief="solid",
            bd=1
        )
        entry_pesquisa.pack(side="left", padx=5)
        
        btn_pesquisar = tk.Button(
            frame_pesquisa, 
            text="Pesquisar", 
            command=self.pesquisar_clientes,
            bg=CORES["botao_info"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_pesquisar.pack(side="left")
        
        # Tabela de clientes
        frame_tabela = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_tabela.pack(fill="both", expand=True)
        
        # Configurar Treeview
        colunas = ("ID", "Nome", "CPF", "Telefone", "Email", "Data Cadastro")
        
        self.tree_clientes = ttk.Treeview(
            frame_tabela, 
            columns=colunas, 
            show="headings",
            selectmode="browse"
        )
        
        # Configurar colunas
        larguras = [50, 200, 120, 120, 200, 120]
        for col, larg in zip(colunas, larguras):
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=larg, anchor="center")
        
        # Barra de rolagem
        scroll_y = ttk.Scrollbar(
            frame_tabela, 
            orient="vertical", 
            command=self.tree_clientes.yview
        )
        self.tree_clientes.configure(yscrollcommand=scroll_y.set)
        
        # Layout
        self.tree_clientes.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        # Carregar clientes
        self.carregar_clientes()
    
    def carregar_clientes(self, filtro=None):
        """Carrega os clientes na tabela, opcionalmente com filtro"""
        # Limpar tabela
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        # Buscar clientes no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            if filtro and filtro.strip():
                query = '''
                    SELECT id, nome, cpf, telefone, email, data_cadastro 
                    FROM clientes 
                    WHERE nome LIKE ? OR cpf LIKE ? OR email LIKE ?
                    ORDER BY nome
                '''
                params = (f'%{filtro.strip()}%', f'%{filtro.strip()}%', f'%{filtro.strip()}%')
            else:
                query = '''
                    SELECT id, nome, cpf, telefone, email, data_cadastro 
                    FROM clientes 
                    ORDER BY nome
                '''
                params = ()
            
            cursor.execute(query, params)
            clientes = cursor.fetchall()
            
            # Adicionar clientes na tabela
            for cliente in clientes:
                self.tree_clientes.insert("", "end", values=cliente)
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar os clientes:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def cadastrar_cliente(self):
        """Abre o formulário para cadastrar um novo cliente"""
        self.janela_cliente = tk.Toplevel()
        self.janela_cliente.title("Cadastrar Novo Cliente")
        self.janela_cliente.geometry("500x450")
        self.janela_cliente.resizable(False, False)
        self.janela_cliente.grab_set()
        
        # Variáveis do formulário
        self.var_cliente_nome = tk.StringVar()
        self.var_cliente_cpf = tk.StringVar()
        self.var_cliente_telefone = tk.StringVar()
        self.var_cliente_email = tk.StringVar()
        self.var_cliente_endereco = tk.StringVar()
        
        # Frame principal
        frame_principal = tk.Frame(self.janela_cliente, padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)
        
        # Título
        tk.Label(
            frame_principal, 
            text="Informações do Cliente", 
            font=('Segoe UI', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Campos do formulário
        campos = [
            ("Nome*", self.var_cliente_nome, 1),
            ("CPF", self.var_cliente_cpf, 2),
            ("Telefone", self.var_cliente_telefone, 3),
            ("Email", self.var_cliente_email, 4),
            ("Endereço", self.var_cliente_endereco, 5)
        ]
        
        for i, (label, var, row) in enumerate(campos):
            tk.Label(
                frame_principal, 
                text=label, 
                font=('Segoe UI', 10)
            ).grid(row=row, column=0, sticky="w", pady=(10, 0))
            
            entry = tk.Entry(
                frame_principal, 
                textvariable=var,
                width=40,
                font=('Segoe UI', 10)
            )
            entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
        
        # Configurar grid
        for i in range(6):
            frame_principal.grid_rowconfigure(i, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(1, weight=3)
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=20)
        
        btn_salvar = tk.Button(
            frame_botoes, 
            text="Salvar", 
            command=self.salvar_cliente,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10, 'bold'),
            width=15
        )
        btn_salvar.pack(side="left", padx=10)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_cliente.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=15
        )
        btn_cancelar.pack(side="right", padx=10)
    
    def salvar_cliente(self):
        """Valida e salva o novo cliente no banco de dados"""
        # Validação dos campos obrigatórios
        if not self.var_cliente_nome.get().strip():
            messagebox.showerror("Erro", "O campo Nome é obrigatório!")
            return
        
        # Obter data atual
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Inserir no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO clientes (
                    nome, cpf, telefone, email, endereco, data_cadastro
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.var_cliente_nome.get().strip(),
                self.var_cliente_cpf.get().strip(),
                self.var_cliente_telefone.get().strip(),
                self.var_cliente_email.get().strip(),
                self.var_cliente_endereco.get().strip(),
                data_atual
            ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.janela_cliente.destroy()
            self.carregar_clientes()  # Atualizar a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um cliente com este CPF!")
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível salvar o cliente:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def editar_cliente(self):
        """Abre o formulário para editar um cliente existente"""
        selecao = self.tree_clientes.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um cliente para editar!")
            return
        
        # Obter ID do cliente selecionado
        item = self.tree_clientes.item(selecao)
        cliente_id = item['values'][0]
        
        # Buscar cliente no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
            cliente = cursor.fetchone()
            
            if not cliente:
                messagebox.showerror("Erro", "Cliente não encontrado!")
                return
            
            # Criar janela de edição
            self.janela_editar_cliente = tk.Toplevel()
            self.janela_editar_cliente.title(f"Editar Cliente - ID: {cliente_id}")
            self.janela_editar_cliente.geometry("500x450")
            self.janela_editar_cliente.resizable(False, False)
            self.janela_editar_cliente.grab_set()
            
            # Variáveis do formulário
            self.var_editar_cliente_id = cliente[0]
            self.var_editar_cliente_nome = tk.StringVar(value=cliente[1])
            self.var_editar_cliente_cpf = tk.StringVar(value=cliente[2] if cliente[2] else "")
            self.var_editar_cliente_telefone = tk.StringVar(value=cliente[3] if cliente[3] else "")
            self.var_editar_cliente_email = tk.StringVar(value=cliente[4] if cliente[4] else "")
            self.var_editar_cliente_endereco = tk.StringVar(value=cliente[5] if cliente[5] else "")
            
            # Frame principal
            frame_principal = tk.Frame(self.janela_editar_cliente, padx=20, pady=20)
            frame_principal.pack(fill="both", expand=True)
            
            # Título
            tk.Label(
                frame_principal, 
                text="Editar Cliente", 
                font=('Segoe UI', 14, 'bold')
            ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
            
            # Campos do formulário
            campos = [
                ("Nome*", self.var_editar_cliente_nome, 1),
                ("CPF", self.var_editar_cliente_cpf, 2),
                ("Telefone", self.var_editar_cliente_telefone, 3),
                ("Email", self.var_editar_cliente_email, 4),
                ("Endereço", self.var_editar_cliente_endereco, 5)
            ]
            
            for i, (label, var, row) in enumerate(campos):
                tk.Label(
                    frame_principal, 
                    text=label, 
                    font=('Segoe UI', 10)
                ).grid(row=row, column=0, sticky="w", pady=(10, 0))
                
                entry = tk.Entry(
                    frame_principal, 
                    textvariable=var,
                    width=40,
                    font=('Segoe UI', 10)
                )
                entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
            
            # Configurar grid
            for i in range(6):
                frame_principal.grid_rowconfigure(i, weight=1)
            frame_principal.grid_columnconfigure(0, weight=1)
            frame_principal.grid_columnconfigure(1, weight=3)
            
            # Frame de botões
            frame_botoes = tk.Frame(frame_principal)
            frame_botoes.grid(row=6, column=0, columnspan=2, pady=20)
            
            btn_salvar = tk.Button(
                frame_botoes, 
                text="Salvar Alterações", 
                command=self.salvar_edicao_cliente,
                bg=CORES["botao_sucesso"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10, 'bold'),
                width=20
            )
            btn_salvar.pack(side="left", padx=10)
            
            btn_cancelar = tk.Button(
                frame_botoes, 
                text="Cancelar", 
                command=self.janela_editar_cliente.destroy,
                bg=CORES["botao_perigo"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10),
                width=20
            )
            btn_cancelar.pack(side="right", padx=10)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar o cliente:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def salvar_edicao_cliente(self):
        """Salva as alterações do cliente no banco de dados"""
        # Validação dos campos obrigatórios
        if not self.var_editar_cliente_nome.get().strip():
            messagebox.showerror("Erro", "O campo Nome é obrigatório!")
            return
        
        # Atualizar no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE clientes SET
                    nome = ?,
                    cpf = ?,
                    telefone = ?,
                    email = ?,
                    endereco = ?
                WHERE id = ?
            ''', (
                self.var_editar_cliente_nome.get().strip(),
                self.var_editar_cliente_cpf.get().strip(),
                self.var_editar_cliente_telefone.get().strip(),
                self.var_editar_cliente_email.get().strip(),
                self.var_editar_cliente_endereco.get().strip(),
                self.var_editar_cliente_id
            ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")
            self.janela_editar_cliente.destroy()
            self.carregar_clientes()  # Atualizar a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um cliente com este CPF!")
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível atualizar o cliente:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def excluir_cliente(self):
        """Exclui o cliente selecionado após confirmação"""
        selecao = self.tree_clientes.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um cliente para excluir!")
            return
        
        # Obter ID do cliente selecionado
        item = self.tree_clientes.item(selecao)
        cliente_id = item['values'][0]
        cliente_nome = item['values'][1]
        
        # Confirmar exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o cliente:\n\n{cliente_nome}?"
        ):
            return
        
        # Excluir do banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")
                self.carregar_clientes()
            else:
                messagebox.showerror("Erro", "Cliente não encontrado!")
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro", 
                f"Não foi possível excluir o cliente:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def pesquisar_clientes(self):
        """Filtra os clientes com base no termo de pesquisa"""
        termo = self.var_pesquisa_cliente.get().strip()
        self.carregar_clientes(termo if termo else None)
    
    def abrir_modulo_fornecedores(self):
        """Abre o módulo de gerenciamento de fornecedores"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Gerenciamento de Fornecedores", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Barra de ferramentas
        frame_ferramentas = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_ferramentas.pack(fill="x", pady=(0, 10))
        
        # Botões de ação
        btn_novo = tk.Button(
            frame_ferramentas, 
            text="Novo Fornecedor", 
            command=self.cadastrar_fornecedor,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_novo.pack(side="left", padx=5)
        
        btn_editar = tk.Button(
            frame_ferramentas, 
            text="Editar", 
            command=self.editar_fornecedor,
            bg=CORES["botao_primario"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_editar.pack(side="left", padx=5)
        
        btn_excluir = tk.Button(
            frame_ferramentas, 
            text="Excluir", 
            command=self.excluir_fornecedor,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_excluir.pack(side="left", padx=5)
        
        # Barra de pesquisa
        frame_pesquisa = tk.Frame(
            frame_ferramentas, 
            bg=CORES["fundo"]
        )
        frame_pesquisa.pack(side="right")
        
        self.var_pesquisa_fornecedor = tk.StringVar()
        entry_pesquisa = tk.Entry(
            frame_pesquisa, 
            textvariable=self.var_pesquisa_fornecedor,
            width=30,
            font=('Segoe UI', 10),
            relief="solid",
            bd=1
        )
        entry_pesquisa.pack(side="left", padx=5)
        
        btn_pesquisar = tk.Button(
            frame_pesquisa, 
            text="Pesquisar", 
            command=self.pesquisar_fornecedores,
            bg=CORES["botao_info"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_pesquisar.pack(side="left")
        
        # Tabela de fornecedores
        frame_tabela = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_tabela.pack(fill="both", expand=True)
        
        # Configurar Treeview
        colunas = ("ID", "Nome", "CNPJ", "Telefone", "Email", "Data Cadastro")
        
        self.tree_fornecedores = ttk.Treeview(
            frame_tabela, 
            columns=colunas, 
            show="headings",
            selectmode="browse"
        )
        
        # Configurar colunas
        larguras = [50, 200, 150, 120, 200, 120]
        for col, larg in zip(colunas, larguras):
            self.tree_fornecedores.heading(col, text=col)
            self.tree_fornecedores.column(col, width=larg, anchor="center")
        
        # Barra de rolagem
        scroll_y = ttk.Scrollbar(
            frame_tabela, 
            orient="vertical", 
            command=self.tree_fornecedores.yview
        )
        self.tree_fornecedores.configure(yscrollcommand=scroll_y.set)
        
        # Layout
        self.tree_fornecedores.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        # Carregar fornecedores
        self.carregar_fornecedores()
    
    def carregar_fornecedores(self, filtro=None):
        """Carrega os fornecedores na tabela, opcionalmente com filtro"""
        # Limpar tabela
        for item in self.tree_fornecedores.get_children():
            self.tree_fornecedores.delete(item)
        
        # Buscar fornecedores no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            if filtro and filtro.strip():
                query = '''
                    SELECT id, nome, cnpj, telefone, email, data_cadastro 
                    FROM fornecedores 
                    WHERE nome LIKE ? OR cnpj LIKE ? OR email LIKE ?
                    ORDER BY nome
                '''
                params = (f'%{filtro.strip()}%', f'%{filtro.strip()}%', f'%{filtro.strip()}%')
            else:
                query = '''
                    SELECT id, nome, cnpj, telefone, email, data_cadastro 
                    FROM fornecedores 
                    ORDER BY nome
                '''
                params = ()
            
            cursor.execute(query, params)
            fornecedores = cursor.fetchall()
            
            # Adicionar fornecedores na tabela
            for fornecedor in fornecedores:
                self.tree_fornecedores.insert("", "end", values=fornecedor)
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar os fornecedores:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def cadastrar_fornecedor(self):
        """Abre o formulário para cadastrar um novo fornecedor"""
        self.janela_fornecedor = tk.Toplevel()
        self.janela_fornecedor.title("Cadastrar Novo Fornecedor")
        self.janela_fornecedor.geometry("500x450")
        self.janela_fornecedor.resizable(False, False)
        self.janela_fornecedor.grab_set()
        
        # Variáveis do formulário
        self.var_fornecedor_nome = tk.StringVar()
        self.var_fornecedor_cnpj = tk.StringVar()
        self.var_fornecedor_telefone = tk.StringVar()
        self.var_fornecedor_email = tk.StringVar()
        self.var_fornecedor_endereco = tk.StringVar()
        
        # Frame principal
        frame_principal = tk.Frame(self.janela_fornecedor, padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)
        
        # Título
        tk.Label(
            frame_principal, 
            text="Informações do Fornecedor", 
            font=('Segoe UI', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Campos do formulário
        campos = [
            ("Nome*", self.var_fornecedor_nome, 1),
            ("CNPJ", self.var_fornecedor_cnpj, 2),
            ("Telefone", self.var_fornecedor_telefone, 3),
            ("Email", self.var_fornecedor_email, 4),
            ("Endereço", self.var_fornecedor_endereco, 5)
        ]
        
        for i, (label, var, row) in enumerate(campos):
            tk.Label(
                frame_principal, 
                text=label, 
                font=('Segoe UI', 10)
            ).grid(row=row, column=0, sticky="w", pady=(10, 0))
            
            entry = tk.Entry(
                frame_principal, 
                textvariable=var,
                width=40,
                font=('Segoe UI', 10)
            )
            entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
        
        # Configurar grid
        for i in range(6):
            frame_principal.grid_rowconfigure(i, weight=1)
        frame_principal.grid_columnconfigure(0, weight=1)
        frame_principal.grid_columnconfigure(1, weight=3)
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=20)
        
        btn_salvar = tk.Button(
            frame_botoes, 
            text="Salvar", 
            command=self.salvar_fornecedor,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10, 'bold'),
            width=15
        )
        btn_salvar.pack(side="left", padx=10)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_fornecedor.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=15
        )
        btn_cancelar.pack(side="right", padx=10)
    
    def salvar_fornecedor(self):
        """Valida e salva o novo fornecedor no banco de dados"""
        # Validação dos campos obrigatórios
        if not self.var_fornecedor_nome.get().strip():
            messagebox.showerror("Erro", "O campo Nome é obrigatório!")
            return
        
        # Obter data atual
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Inserir no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO fornecedores (
                    nome, cnpj, telefone, email, endereco, data_cadastro
                )
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.var_fornecedor_nome.get().strip(),
                self.var_fornecedor_cnpj.get().strip(),
                self.var_fornecedor_telefone.get().strip(),
                self.var_fornecedor_email.get().strip(),
                self.var_fornecedor_endereco.get().strip(),
                data_atual
            ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Fornecedor cadastrado com sucesso!")
            self.janela_fornecedor.destroy()
            self.carregar_fornecedores()  # Atualizar a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um fornecedor com este CNPJ!")
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível salvar o fornecedor:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def editar_fornecedor(self):
        """Abre o formulário para editar um fornecedor existente"""
        selecao = self.tree_fornecedores.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para editar!")
            return
        
        # Obter ID do fornecedor selecionado
        item = self.tree_fornecedores.item(selecao)
        fornecedor_id = item['values'][0]
        
        # Buscar fornecedor no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM fornecedores WHERE id = ?", (fornecedor_id,))
            fornecedor = cursor.fetchone()
            
            if not fornecedor:
                messagebox.showerror("Erro", "Fornecedor não encontrado!")
                return
            
            # Criar janela de edição
            self.janela_editar_fornecedor = tk.Toplevel()
            self.janela_editar_fornecedor.title(f"Editar Fornecedor - ID: {fornecedor_id}")
            self.janela_editar_fornecedor.geometry("500x450")
            self.janela_editar_fornecedor.resizable(False, False)
            self.janela_editar_fornecedor.grab_set()
            
            # Variáveis do formulário
            self.var_editar_fornecedor_id = fornecedor[0]
            self.var_editar_fornecedor_nome = tk.StringVar(value=fornecedor[1])
            self.var_editar_fornecedor_cnpj = tk.StringVar(value=fornecedor[2] if fornecedor[2] else "")
            self.var_editar_fornecedor_telefone = tk.StringVar(value=fornecedor[3] if fornecedor[3] else "")
            self.var_editar_fornecedor_email = tk.StringVar(value=fornecedor[4] if fornecedor[4] else "")
            self.var_editar_fornecedor_endereco = tk.StringVar(value=fornecedor[5] if fornecedor[5] else "")
            
            # Frame principal
            frame_principal = tk.Frame(self.janela_editar_fornecedor, padx=20, pady=20)
            frame_principal.pack(fill="both", expand=True)
            
            # Título
            tk.Label(
                frame_principal, 
                text="Editar Fornecedor", 
                font=('Segoe UI', 14, 'bold')
            ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
            
            # Campos do formulário
            campos = [
                ("Nome*", self.var_editar_fornecedor_nome, 1),
                ("CNPJ", self.var_editar_fornecedor_cnpj, 2),
                ("Telefone", self.var_editar_fornecedor_telefone, 3),
                ("Email", self.var_editar_fornecedor_email, 4),
                ("Endereço", self.var_editar_fornecedor_endereco, 5)
            ]
            
            for i, (label, var, row) in enumerate(campos):
                tk.Label(
                    frame_principal, 
                    text=label, 
                    font=('Segoe UI', 10)
                ).grid(row=row, column=0, sticky="w", pady=(10, 0))
                
                entry = tk.Entry(
                    frame_principal, 
                    textvariable=var,
                    width=40,
                    font=('Segoe UI', 10)
                )
                entry.grid(row=row, column=1, sticky="w", pady=(10, 0))
            
            # Configurar grid
            for i in range(6):
                frame_principal.grid_rowconfigure(i, weight=1)
            frame_principal.grid_columnconfigure(0, weight=1)
            frame_principal.grid_columnconfigure(1, weight=3)
            
            # Frame de botões
            frame_botoes = tk.Frame(frame_principal)
            frame_botoes.grid(row=6, column=0, columnspan=2, pady=20)
            
            btn_salvar = tk.Button(
                frame_botoes, 
                text="Salvar Alterações", 
                command=self.salvar_edicao_fornecedor,
                bg=CORES["botao_sucesso"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10, 'bold'),
                width=20
            )
            btn_salvar.pack(side="left", padx=10)
            
            btn_cancelar = tk.Button(
                frame_botoes, 
                text="Cancelar", 
                command=self.janela_editar_fornecedor.destroy,
                bg=CORES["botao_perigo"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10),
                width=20
            )
            btn_cancelar.pack(side="right", padx=10)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar o fornecedor:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def salvar_edicao_fornecedor(self):
        """Salva as alterações do fornecedor no banco de dados"""
        # Validação dos campos obrigatórios
        if not self.var_editar_fornecedor_nome.get().strip():
            messagebox.showerror("Erro", "O campo Nome é obrigatório!")
            return
        
        # Atualizar no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE fornecedores SET
                    nome = ?,
                    cnpj = ?,
                    telefone = ?,
                    email = ?,
                    endereco = ?
                WHERE id = ?
            ''', (
                self.var_editar_fornecedor_nome.get().strip(),
                self.var_editar_fornecedor_cnpj.get().strip(),
                self.var_editar_fornecedor_telefone.get().strip(),
                self.var_editar_fornecedor_email.get().strip(),
                self.var_editar_fornecedor_endereco.get().strip(),
                self.var_editar_fornecedor_id
            ))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Fornecedor atualizado com sucesso!")
            self.janela_editar_fornecedor.destroy()
            self.carregar_fornecedores()  # Atualizar a lista
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Já existe um fornecedor com este CNPJ!")
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível atualizar o fornecedor:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def excluir_fornecedor(self):
        """Exclui o fornecedor selecionado após confirmação"""
        selecao = self.tree_fornecedores.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um fornecedor para excluir!")
            return
        
        # Obter ID do fornecedor selecionado
        item = self.tree_fornecedores.item(selecao)
        fornecedor_id = item['values'][0]
        fornecedor_nome = item['values'][1]
        
        # Confirmar exclusão
        if not messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o fornecedor:\n\n{fornecedor_nome}?"
        ):
            return
        
        # Excluir do banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM fornecedores WHERE id = ?", (fornecedor_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                messagebox.showinfo("Sucesso", "Fornecedor excluído com sucesso!")
                self.carregar_fornecedores()
            else:
                messagebox.showerror("Erro", "Fornecedor não encontrado!")
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro", 
                f"Não foi possível excluir o fornecedor:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def pesquisar_fornecedores(self):
        """Filtra os fornecedores com base no termo de pesquisa"""
        termo = self.var_pesquisa_fornecedor.get().strip()
        self.carregar_fornecedores(termo if termo else None)
    
    def abrir_modulo_estoque(self):
        """Abre o módulo de gerenciamento de estoque"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Gerenciamento de Estoque", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Barra de ferramentas
        frame_ferramentas = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_ferramentas.pack(fill="x", pady=(0, 10))
        
        # Botões de ação
        btn_entrada = tk.Button(
            frame_ferramentas, 
            text="Entrada de Estoque", 
            command=self.registrar_entrada_estoque,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_entrada.pack(side="left", padx=5)
        
        btn_ajuste = tk.Button(
            frame_ferramentas, 
            text="Ajuste de Estoque", 
            command=self.registrar_ajuste_estoque,
            bg=CORES["botao_aviso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_ajuste.pack(side="left", padx=5)
        
        # Barra de pesquisa
        frame_pesquisa = tk.Frame(
            frame_ferramentas, 
            bg=CORES["fundo"]
        )
        frame_pesquisa.pack(side="right")
        
        self.var_pesquisa_estoque = tk.StringVar()
        entry_pesquisa = tk.Entry(
            frame_pesquisa, 
            textvariable=self.var_pesquisa_estoque,
            width=30,
            font=('Segoe UI', 10),
            relief="solid",
            bd=1
        )
        entry_pesquisa.pack(side="left", padx=5)
        
        btn_pesquisar = tk.Button(
            frame_pesquisa, 
            text="Pesquisar", 
            command=self.pesquisar_estoque,
            bg=CORES["botao_info"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15
        )
        btn_pesquisar.pack(side="left")
        
        # Tabela de estoque
        frame_tabela = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_tabela.pack(fill="both", expand=True)
        
        # Configurar Treeview
        colunas = ("ID", "Código", "Nome", "Quantidade", "Preço Compra", "Preço Venda", "Categoria")
        
        self.tree_estoque = ttk.Treeview(
            frame_tabela, 
            columns=colunas, 
            show="headings",
            selectmode="browse"
        )
        
        # Configurar colunas
        larguras = [50, 80, 200, 80, 100, 100, 120]
        for col, larg in zip(colunas, larguras):
            self.tree_estoque.heading(col, text=col)
            self.tree_estoque.column(col, width=larg, anchor="center")
        
        # Barra de rolagem
        scroll_y = ttk.Scrollbar(
            frame_tabela, 
            orient="vertical", 
            command=self.tree_estoque.yview
        )
        self.tree_estoque.configure(yscrollcommand=scroll_y.set)
        
        # Layout
        self.tree_estoque.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        
        # Carregar estoque
        self.carregar_estoque()
    
    def carregar_estoque(self, filtro=None):
        """Carrega os produtos em estoque na tabela, opcionalmente com filtro"""
        # Limpar tabela
        for item in self.tree_estoque.get_children():
            self.tree_estoque.delete(item)
        
        # Buscar produtos no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            if filtro and filtro.strip():
                query = '''
                    SELECT id, codigo, nome, quantidade, preco_compra, preco_venda, categoria 
                    FROM produtos 
                    WHERE nome LIKE ? OR codigo LIKE ? OR categoria LIKE ?
                    ORDER BY nome
                '''
                params = (f'%{filtro.strip()}%', f'%{filtro.strip()}%', f'%{filtro.strip()}%')
            else:
                query = '''
                    SELECT id, codigo, nome, quantidade, preco_compra, preco_venda, categoria 
                    FROM produtos 
                    ORDER BY nome
                '''
                params = ()
            
            cursor.execute(query, params)
            produtos = cursor.fetchall()
            
            # Adicionar produtos na tabela
            for produto in produtos:
                # Formatar preços
                produto = list(produto)
                produto[4] = f"R$ {produto[4]:.2f}".replace(".", ",")
                produto[5] = f"R$ {produto[5]:.2f}".replace(".", ",")
                self.tree_estoque.insert("", "end", values=produto)
                
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível carregar o estoque:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def registrar_entrada_estoque(self):
        """Registra uma entrada de estoque para o produto selecionado"""
        selecao = self.tree_estoque.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um produto para registrar entrada!")
            return
        
        # Obter ID do produto selecionado
        item = self.tree_estoque.item(selecao)
        produto_id = item['values'][0]
        produto_nome = item['values'][2]
        
        # Janela para entrada de estoque
        self.janela_entrada = tk.Toplevel()
        self.janela_entrada.title(f"Entrada de Estoque - {produto_nome}")
        self.janela_entrada.geometry("400x250")
        self.janela_entrada.resizable(False, False)
        self.janela_entrada.grab_set()
        
        # Variáveis
        self.var_entrada_produto_id = produto_id
        self.var_entrada_quantidade = tk.StringVar(value="1")
        self.var_entrada_preco_compra = tk.StringVar()
        
        # Frame principal
        frame_principal = tk.Frame(self.janela_entrada, padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)
        
        # Informações do produto
        tk.Label(
            frame_principal, 
            text=f"Produto: {produto_nome}", 
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            frame_principal, 
            text="Quantidade de Entrada:", 
            font=('Segoe UI', 10)
        ).pack(anchor="w", pady=(5, 0))
        
        spin_quantidade = tk.Spinbox(
            frame_principal,
            from_=1,
            to=1000,
            textvariable=self.var_entrada_quantidade,
            font=('Segoe UI', 10),
            width=10
        )
        spin_quantidade.pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            frame_principal, 
            text="Novo Preço de Compra (opcional):", 
            font=('Segoe UI', 10)
        ).pack(anchor="w", pady=(5, 0))
        
        entry_preco = tk.Entry(
            frame_principal,
            textvariable=self.var_entrada_preco_compra,
            font=('Segoe UI', 10),
            width=15
        )
        entry_preco.pack(anchor="w", pady=(0, 20))
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(fill="x", pady=(10, 0))
        
        btn_confirmar = tk.Button(
            frame_botoes, 
            text="Confirmar Entrada", 
            command=self.salvar_entrada_estoque,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10, 'bold'),
            width=20
        )
        btn_confirmar.pack(side="left", padx=5)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_entrada.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=20
        )
        btn_cancelar.pack(side="right", padx=5)
    
    def salvar_entrada_estoque(self):
        """Salva a entrada de estoque no banco de dados"""
        try:
            quantidade = int(self.var_entrada_quantidade.get())
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva")
                
            preco_compra = None
            if self.var_entrada_preco_compra.get().strip():
                preco_compra = float(self.var_entrada_preco_compra.get().replace(",", "."))
                if preco_compra <= 0:
                    raise ValueError("Preço deve ser positivo")
            
            # Atualizar no banco de dados
            conn = None
            try:
                conn = sqlite3.connect('loja.db')
                cursor = conn.cursor()
                
                if preco_compra:
                    cursor.execute('''
                        UPDATE produtos SET
                            quantidade = quantidade + ?,
                            preco_compra = ?,
                            data_atualizacao = ?
                        WHERE id = ?
                    ''', (
                        quantidade,
                        preco_compra,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        self.var_entrada_produto_id
                    ))
                else:
                    cursor.execute('''
                        UPDATE produtos SET
                            quantidade = quantidade + ?,
                            data_atualizacao = ?
                        WHERE id = ?
                    ''', (
                        quantidade,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        self.var_entrada_produto_id
                    ))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "Entrada de estoque registrada com sucesso!")
                self.janela_entrada.destroy()
                self.carregar_estoque()  # Atualizar a lista
                
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Erro no Banco de Dados", 
                    f"Não foi possível registrar a entrada:\n{str(e)}"
                )
            finally:
                if conn:
                    conn.close()
                    
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
    
    def registrar_ajuste_estoque(self):
        """Registra um ajuste de estoque para o produto selecionado"""
        selecao = self.tree_estoque.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um produto para ajustar estoque!")
            return
        
        # Obter ID do produto selecionado
        item = self.tree_estoque.item(selecao)
        produto_id = item['values'][0]
        produto_nome = item['values'][2]
        quantidade_atual = int(item['values'][3])
        
        # Janela para ajuste de estoque
        self.janela_ajuste = tk.Toplevel()
        self.janela_ajuste.title(f"Ajuste de Estoque - {produto_nome}")
        self.janela_ajuste.geometry("400x250")
        self.janela_ajuste.resizable(False, False)
        self.janela_ajuste.grab_set()
        
        # Variáveis
        self.var_ajuste_produto_id = produto_id
        self.var_ajuste_quantidade = tk.StringVar(value=str(quantidade_atual))
        
        # Frame principal
        frame_principal = tk.Frame(self.janela_ajuste, padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)
        
        # Informações do produto
        tk.Label(
            frame_principal, 
            text=f"Produto: {produto_nome}", 
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            frame_principal, 
            text="Quantidade Atual:", 
            font=('Segoe UI', 10)
        ).pack(anchor="w", pady=(5, 0))
        
        tk.Label(
            frame_principal, 
            text=str(quantidade_atual), 
            font=('Segoe UI', 10)
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            frame_principal, 
            text="Nova Quantidade:", 
            font=('Segoe UI', 10)
        ).pack(anchor="w", pady=(5, 0))
        
        spin_quantidade = tk.Spinbox(
            frame_principal,
            from_=0,
            to=10000,
            textvariable=self.var_ajuste_quantidade,
            font=('Segoe UI', 10),
            width=10
        )
        spin_quantidade.pack(anchor="w", pady=(0, 20))
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.pack(fill="x", pady=(10, 0))
        
        btn_confirmar = tk.Button(
            frame_botoes, 
            text="Confirmar Ajuste", 
            command=self.salvar_ajuste_estoque,
            bg=CORES["botao_aviso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10, 'bold'),
            width=20
        )
        btn_confirmar.pack(side="left", padx=5)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_ajuste.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=20
        )
        btn_cancelar.pack(side="right", padx=5)
    
    def salvar_ajuste_estoque(self):
        """Salva o ajuste de estoque no banco de dados"""
        try:
            nova_quantidade = int(self.var_ajuste_quantidade.get())
            if nova_quantidade < 0:
                raise ValueError("Quantidade não pode ser negativa")
                
            # Atualizar no banco de dados
            conn = None
            try:
                conn = sqlite3.connect('loja.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE produtos SET
                        quantidade = ?,
                        data_atualizacao = ?
                    WHERE id = ?
                ''', (
                    nova_quantidade,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    self.var_ajuste_produto_id
                ))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "Ajuste de estoque registrado com sucesso!")
                self.janela_ajuste.destroy()
                self.carregar_estoque()  # Atualizar a lista
                
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Erro no Banco de Dados", 
                    f"Não foi possível registrar o ajuste:\n{str(e)}"
                )
            finally:
                if conn:
                    conn.close()
                    
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
    
    def pesquisar_estoque(self):
        """Filtra os produtos em estoque com base no termo de pesquisa"""
        termo = self.var_pesquisa_estoque.get().strip()
        self.carregar_estoque(termo if termo else None)
    
    def abrir_modulo_relatorios(self):
        """Abre o módulo de relatórios"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Relatórios", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Frame de opções
        frame_opcoes = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_opcoes.pack(fill="x", pady=20)
        
        # Botões de relatórios
        relatorios = [
            ("Vendas por Período", self.gerar_relatorio_vendas_periodo),
            ("Produtos Mais Vendidos", self.gerar_relatorio_produtos_mais_vendidos),
            ("Faturamento Mensal", self.gerar_relatorio_faturamento_mensal),
            ("Estoque Crítico", self.gerar_relatorio_estoque_critico)
        ]
        
        for i, (texto, comando) in enumerate(relatorios):
            btn = tk.Button(
                frame_opcoes, 
                text=texto, 
                command=comando,
                bg=CORES["botao_primario"],
                fg=CORES["botao_texto"],
                font=('Segoe UI', 10),
                relief="flat",
                padx=15,
                pady=10,
                width=25
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=5)
        
        # Frame de resultados
        frame_resultados = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_resultados.pack(fill="both", expand=True)
        
        # Área de texto para relatórios
        self.texto_relatorio = tk.Text(
            frame_resultados, 
            wrap="word", 
            font=('Segoe UI', 10),
            padx=10,
            pady=10
        )
        scroll_y = ttk.Scrollbar(
            frame_resultados, 
            orient="vertical", 
            command=self.texto_relatorio.yview
        )
        self.texto_relatorio.configure(yscrollcommand=scroll_y.set)
        
        self.texto_relatorio.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
    
    def gerar_relatorio_vendas_periodo(self):
        """Gera relatório de vendas por período"""
        # Janela para seleção de período
        self.janela_periodo = tk.Toplevel()
        self.janela_periodo.title("Selecionar Período")
        self.janela_periodo.geometry("400x200")
        self.janela_periodo.resizable(False, False)
        self.janela_periodo.grab_set()
        
        # Variáveis
        self.var_data_inicio = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.var_data_fim = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        
        # Frame principal
        frame_principal = tk.Frame(self.janela_periodo, padx=20, pady=20)
        frame_principal.pack(fill="both", expand=True)
        
        # Data de início
        tk.Label(
            frame_principal, 
            text="Data Início:", 
            font=('Segoe UI', 10)
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        entry_inicio = tk.Entry(
            frame_principal,
            textvariable=self.var_data_inicio,
            font=('Segoe UI', 10),
            width=15
        )
        entry_inicio.grid(row=0, column=1, sticky="w", pady=5)
        
        # Data de fim
        tk.Label(
            frame_principal, 
            text="Data Fim:", 
            font=('Segoe UI', 10)
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        entry_fim = tk.Entry(
            frame_principal,
            textvariable=self.var_data_fim,
            font=('Segoe UI', 10),
            width=15
        )
        entry_fim.grid(row=1, column=1, sticky="w", pady=5)
        
        # Frame de botões
        frame_botoes = tk.Frame(frame_principal)
        frame_botoes.grid(row=2, column=0, columnspan=2, pady=20)
        
        btn_gerar = tk.Button(
            frame_botoes, 
            text="Gerar Relatório", 
            command=self.processar_relatorio_vendas_periodo,
            bg=CORES["botao_sucesso"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10, 'bold'),
            width=20
        )
        btn_gerar.pack(side="left", padx=5)
        
        btn_cancelar = tk.Button(
            frame_botoes, 
            text="Cancelar", 
            command=self.janela_periodo.destroy,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            width=20
        )
        btn_cancelar.pack(side="right", padx=5)
    
    def processar_relatorio_vendas_periodo(self):
        """Processa o relatório de vendas por período"""
        try:
            data_inicio = datetime.strptime(self.var_data_inicio.get(), "%d/%m/%Y")
            data_fim = datetime.strptime(self.var_data_fim.get(), "%d/%m/%Y")
            
            if data_fim < data_inicio:
                messagebox.showerror("Erro", "Data final não pode ser anterior à data inicial!")
                return
            
            # Formatar datas para o SQL
            data_inicio_sql = data_inicio.strftime("%Y-%m-%d")
            data_fim_sql = data_fim.strftime("%Y-%m-%d")
            
            # Buscar dados no banco de dados
            conn = None
            try:
                conn = sqlite3.connect('loja.db')
                cursor = conn.cursor()
                
                # Total de vendas no período
                cursor.execute('''
                    SELECT COUNT(*), SUM(total) 
                    FROM vendas 
                    WHERE date(data_venda) BETWEEN ? AND ?
                ''', (data_inicio_sql, data_fim_sql))
                total_vendas, faturamento = cursor.fetchone()
                faturamento = faturamento or 0
                
                # Vendas por dia
                cursor.execute('''
                    SELECT date(data_venda), COUNT(*), SUM(total) 
                    FROM vendas 
                    WHERE date(data_venda) BETWEEN ? AND ?
                    GROUP BY date(data_venda)
                    ORDER BY date(data_venda)
                ''', (data_inicio_sql, data_fim_sql))
                vendas_por_dia = cursor.fetchall()
                
                # Produtos mais vendidos
                cursor.execute('''
                    SELECT produto_nome, SUM(quantidade), SUM(total) 
                    FROM vendas 
                    WHERE date(data_venda) BETWEEN ? AND ?
                    GROUP BY produto_nome
                    ORDER BY SUM(quantidade) DESC
                    LIMIT 10
                ''', (data_inicio_sql, data_fim_sql))
                produtos_mais_vendidos = cursor.fetchall()
                
                # Formatar relatório
                relatorio = f"RELATÓRIO DE VENDAS - {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n"
                relatorio += "="*60 + "\n\n"
                relatorio += f"Total de Vendas: {total_vendas}\n"
                relatorio += f"Faturamento Total: R$ {faturamento:.2f}\n\n"
                
                relatorio += "Vendas por Dia:\n"
                relatorio += "-"*40 + "\n"
                for data, qtd, total in vendas_por_dia:
                    data_formatada = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                    relatorio += f"{data_formatada}: {qtd} vendas (R$ {total:.2f})\n"
                
                relatorio += "\nProdutos Mais Vendidos:\n"
                relatorio += "-"*40 + "\n"
                for produto, qtd, total in produtos_mais_vendidos:
                    relatorio += f"{produto}: {qtd} unidades (R$ {total:.2f})\n"
                
                # Exibir relatório
                self.texto_relatorio.delete("1.0", "end")
                self.texto_relatorio.insert("1.0", relatorio)
                self.janela_periodo.destroy()
                
            except sqlite3.Error as e:
                messagebox.showerror(
                    "Erro no Banco de Dados", 
                    f"Não foi possível gerar o relatório:\n{str(e)}"
                )
            finally:
                if conn:
                    conn.close()
                    
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido! Use DD/MM/AAAA")
    
    def gerar_relatorio_produtos_mais_vendidos(self):
        """Gera relatório dos produtos mais vendidos"""
        # Buscar dados no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            # Produtos mais vendidos (últimos 30 dias)
            cursor.execute('''
                SELECT produto_nome, SUM(quantidade), SUM(total) 
                FROM vendas 
                WHERE date(data_venda) >= date('now', '-30 days')
                GROUP BY produto_nome
                ORDER BY SUM(quantidade) DESC
                LIMIT 10
            ''')
            produtos_mais_vendidos = cursor.fetchall()
            
            # Formatar relatório
            relatorio = "RELATÓRIO DE PRODUTOS MAIS VENDIDOS (ÚLTIMOS 30 DIAS)\n"
            relatorio += "="*60 + "\n\n"
            
            if not produtos_mais_vendidos:
                relatorio += "Nenhuma venda registrada no período.\n"
            else:
                for i, (produto, qtd, total) in enumerate(produtos_mais_vendidos, 1):
                    relatorio += f"{i}. {produto}: {qtd} unidades (R$ {total:.2f})\n"
            
            # Exibir relatório
            self.texto_relatorio.delete("1.0", "end")
            self.texto_relatorio.insert("1.0", relatorio)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível gerar o relatório:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def gerar_relatorio_faturamento_mensal(self):
        """Gera relatório de faturamento mensal"""
        # Buscar dados no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            # Faturamento por mês
            cursor.execute('''
                SELECT strftime('%m/%Y', data_venda) as mes, 
                       COUNT(*), 
                       SUM(total) 
                FROM vendas 
                GROUP BY strftime('%m/%Y', data_venda)
                ORDER BY strftime('%Y-%m', data_venda) DESC
                LIMIT 12
            ''')
            faturamento_mensal = cursor.fetchall()
            
            # Formatar relatório
            relatorio = "RELATÓRIO DE FATURAMENTO MENSAL\n"
            relatorio += "="*60 + "\n\n"
            
            if not faturamento_mensal:
                relatorio += "Nenhuma venda registrada.\n"
            else:
                for mes, qtd, total in faturamento_mensal:
                    relatorio += f"{mes}: {qtd} vendas (R$ {total:.2f})\n"
            
            # Exibir relatório
            self.texto_relatorio.delete("1.0", "end")
            self.texto_relatorio.insert("1.0", relatorio)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível gerar o relatório:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def gerar_relatorio_estoque_critico(self):
        """Gera relatório de estoque crítico (produtos com baixo estoque)"""
        # Buscar dados no banco de dados
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            # Produtos com estoque abaixo de 5 unidades
            cursor.execute('''
                SELECT codigo, nome, quantidade, preco_venda 
                FROM produtos 
                WHERE quantidade <= 5
                ORDER BY quantidade
            ''')
            estoque_critico = cursor.fetchall()
            
            # Formatar relatório
            relatorio = "RELATÓRIO DE ESTOQUE CRÍTICO (5 OU MENOS UNIDADES)\n"
            relatorio += "="*60 + "\n\n"
            
            if not estoque_critico:
                relatorio += "Nenhum produto com estoque crítico.\n"
            else:
                for codigo, nome, qtd, preco in estoque_critico:
                    relatorio += f"{codigo} - {nome}: {qtd} unidades (R$ {preco:.2f})\n"
            
            # Exibir relatório
            self.texto_relatorio.delete("1.0", "end")
            self.texto_relatorio.insert("1.0", relatorio)
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro no Banco de Dados", 
                f"Não foi possível gerar o relatório:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def abrir_modulo_configuracoes(self):
        """Abre o módulo de configurações do sistema"""
        self.limpar_conteudo()
        
        # Cabeçalho
        frame_cabecalho = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"]
        )
        frame_cabecalho.pack(fill="x", pady=(0, 20))
        
        lbl_titulo = tk.Label(
            frame_cabecalho, 
            text="Configurações do Sistema", 
            font=('Segoe UI', 16, 'bold'), 
            bg=CORES["fundo"], 
            fg=CORES["texto"]
        )
        lbl_titulo.pack(side="left")
        
        # Frame de configurações
        frame_config = tk.Frame(
            self.frame_conteudo, 
            bg=CORES["fundo"],
            padx=20,
            pady=20
        )
        frame_config.pack(fill="both", expand=True)
        
        # Configurações de tema
        frame_tema = tk.LabelFrame(
            frame_config, 
            text="Tema da Interface", 
            bg=CORES["fundo"],
            fg=CORES["texto"],
            font=('Segoe UI', 10, 'bold'),
            padx=10,
            pady=10
        )
        frame_tema.pack(fill="x", pady=10)
        
        self.var_tema = tk.StringVar(value="Claro")
        temas = ["Claro", "Escuro",]
        
        for tema in temas:
            rb = tk.Radiobutton(
                frame_tema, 
                text=tema, 
                variable=self.var_tema,
                value=tema,
                bg=CORES["fundo"],
                fg=CORES["texto"],
                font=('Segoe UI', 10),
                command=self.alterar_tema
            )
            rb.pack(anchor="w", padx=10, pady=5)
        
        # Configurações de backup
        frame_backup = tk.LabelFrame(
            frame_config, 
            text="Backup do Sistema", 
            bg=CORES["fundo"],
            fg=CORES["texto"],
            font=('Segoe UI', 10, 'bold'),
            padx=10,
            pady=10
        )
        frame_backup.pack(fill="x", pady=10)
        
        btn_backup = tk.Button(
            frame_backup, 
            text="Criar Backup Agora", 
            command=self.criar_backup,
            bg=CORES["botao_info"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15,
            pady=5
        )
        btn_backup.pack(anchor="w", padx=10, pady=5)
        
        # Configurações avançadas
        frame_avancado = tk.LabelFrame(
            frame_config, 
            text="Configurações Avançadas", 
            bg=CORES["fundo"],
            fg=CORES["texto"],
            font=('Segoe UI', 10, 'bold'),
            padx=10,
            pady=10
        )
        frame_avancado.pack(fill="x", pady=10)
        
        btn_limpar = tk.Button(
            frame_avancado, 
            text="Limpar Banco de Dados", 
            command=self.limpar_banco_dados,
            bg=CORES["botao_perigo"],
            fg=CORES["botao_texto"],
            font=('Segoe UI', 10),
            relief="flat",
            padx=15,
            pady=5
        )
        btn_limpar.pack(anchor="w", padx=10, pady=5)
    
    def alterar_tema(self):
        """Altera o tema da interface"""
        tema = self.var_tema.get()
        if tema == "Claro":
            CORES["fundo"] = "#f8f9fa"
            CORES["texto"] = "#212529"
        elif tema == "Escuro":
            CORES["fundo"] = "#343a40"
            CORES["texto"] = "#f8f9fa"
        elif tema == "Azul":
            CORES["fundo"] = "#e7f5ff"
            CORES["texto"] = "#1864ab"
        elif tema == "Verde":
            CORES["fundo"] = "#ebfbee"
            CORES["texto"] = "#2b8a3e"
        
        # Atualizar cores da interface
        self.root.configure(bg=CORES["fundo"])
        self.frame_conteudo.configure(bg=CORES["fundo"])
        
        # Atualizar todos os widgets
        for widget in self.frame_conteudo.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=CORES["fundo"])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=CORES["fundo"], fg=CORES["texto"])
    
    def criar_backup(self):
        """Cria um backup do banco de dados"""
        try:
            import shutil
            import os
            from datetime import datetime
            
            # Criar pasta de backups se não existir
            if not os.path.exists("backups"):
                os.makedirs("backups")
            
            # Nome do arquivo de backup
            data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_backup = f"backups/loja_backup_{data_atual}.db"
            
            # Copiar arquivo do banco de dados
            shutil.copy2('loja.db', nome_backup)
            
            messagebox.showinfo(
                "Backup Criado", 
                f"Backup criado com sucesso:\n{nome_backup}"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao Criar Backup", 
                f"Não foi possível criar o backup:\n{str(e)}"
            )
    
    def limpar_banco_dados(self):
        """Limpa todos os dados do banco de dados (apenas para desenvolvimento)"""
        if not messagebox.askyesno(
            "Confirmar", 
            "ATENÇÃO: Isso apagará TODOS os dados do sistema. Continuar?"
        ):
            return
        
        conn = None
        try:
            conn = sqlite3.connect('loja.db')
            cursor = conn.cursor()
            
            # Apagar todas as tabelas
            cursor.execute("DROP TABLE IF EXISTS produtos")
            cursor.execute("DROP TABLE IF EXISTS vendas")
            cursor.execute("DROP TABLE IF EXISTS clientes")
            cursor.execute("DROP TABLE IF EXISTS fornecedores")
            
            # Recriar tabelas vazias
            self.criar_banco_dados()
            
            conn.commit()
            messagebox.showinfo(
                "Sucesso", 
                "Banco de dados limpo com sucesso!"
            )
            
            # Atualizar interfaces
            if hasattr(self, 'tree_produtos'):
                self.carregar_produtos()
            if hasattr(self, 'tree_clientes'):
                self.carregar_clientes()
            if hasattr(self, 'tree_fornecedores'):
                self.carregar_fornecedores()
            if hasattr(self, 'tree_estoque'):
                self.carregar_estoque()
            
        except sqlite3.Error as e:
            messagebox.showerror(
                "Erro", 
                f"Não foi possível limpar o banco de dados:\n{str(e)}"
            )
        finally:
            if conn:
                conn.close()
    
    def sair_sistema(self):
        """Encerra o sistema após confirmação"""
        if messagebox.askyesno(
            "Sair", 
            "Tem certeza que deseja sair do sistema?"
        ):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaGestaoLoja(root)
    root.mainloop()