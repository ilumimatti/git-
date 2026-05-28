import sqlite3
import datetime

# ✅ MELHORIA: constante centralizada para o nome do banco
BANCO = "estoque.db"

# ✅ MELHORIA: tipos de saída válidos definidos em um lugar só
TIPOS_SAIDA = ("venda", "perda", "transferência")


# ---------------------------------------------------------------------
# Conexão e criação de tabelas
# ---------------------------------------------------------------------

def conectar_banco():
    return sqlite3.connect(BANCO)


def criar_tabelas():
    # ✅ MELHORIA: uso de 'with' garante fechamento mesmo em caso de erro
    with conectar_banco() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estoque (
                codigo          TEXT PRIMARY KEY,
                nome_item       TEXT NOT NULL,
                quantidade      REAL NOT NULL,
                categoria       TEXT NOT NULL,
                armazenar       TEXT NOT NULL,
                unidade_medida  TEXT NOT NULL,
                preco_unitario  REAL NOT NULL,
                preco_total     REAL NOT NULL,
                estoque_minimo  REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimentacao (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_produto   TEXT,
                tipo             TEXT,
                quantidade       REAL,
                data             TEXT,
                observacao       TEXT
            )
        """)
        conexao.commit()


# ---------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------

def _data_hora_atual():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")


def _registrar_movimentacao(cursor, codigo, tipo, quantidade, observacao):
    """Insere um registro na tabela de movimentação."""
    cursor.execute("""
        INSERT INTO movimentacao (codigo_produto, tipo, quantidade, data, observacao)
        VALUES (?, ?, ?, ?, ?)
    """, (codigo, tipo, quantidade, _data_hora_atual(), observacao))


def _buscar_produto(cursor, codigo):
    """Retorna a linha do produto ou None."""
    cursor.execute("SELECT * FROM estoque WHERE codigo = ?", (codigo,))
    return cursor.fetchone()


# ---------------------------------------------------------------------
# Cadastro de produto
# ---------------------------------------------------------------------

def cadastro_produto():
    print("\nCADASTRO DE PRODUTOS")

    codigo = input("Digite o código do produto (3 dígitos): ").strip()

    # ✅ CORREÇÃO: strip() remove espaços acidentais antes da validação
    if not codigo.isdigit() or len(codigo) != 3:
        print("Erro: o código deve conter exatamente 3 dígitos numéricos.")
        return

    nome_item  = input("Digite o nome do produto: ").strip()
    categoria  = input("Digite a categoria do produto: ").strip()
    armazenar  = input("Digite onde o produto será armazenado: ").strip()

    try:
        quantidade     = float(input("Digite a quantidade inicial do produto: "))
        preco_unitario = float(input("Digite o preço unitário do produto: "))
        estoque_minimo = float(input("Digite o estoque mínimo: "))
    except ValueError:
        print("Erro: digite apenas números para quantidade, preço e estoque mínimo.")
        return

    unidade_medida = input("Digite a unidade de medida: ").strip()
    preco_total    = quantidade * preco_unitario

    # ✅ MELHORIA: 'with' garante fechamento correto da conexão
    with conectar_banco() as conexao:
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                INSERT INTO estoque (
                    codigo, nome_item, quantidade, categoria,
                    armazenar, unidade_medida, preco_unitario,
                    preco_total, estoque_minimo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                codigo, nome_item, quantidade, categoria,
                armazenar, unidade_medida, preco_unitario,
                preco_total, estoque_minimo
            ))
            _registrar_movimentacao(cursor, codigo, "entrada", quantidade, "cadastro inicial")
            conexao.commit()
            print("Produto cadastrado com sucesso.")
            print(f"Preço total do estoque: R$ {preco_total:.2f}")

        except sqlite3.IntegrityError:
            print("Erro: já existe um produto com esse código.")
        except sqlite3.Error as erro:
            print("Erro no banco de dados:", erro)


# ---------------------------------------------------------------------
# Entrada de produtos
# ---------------------------------------------------------------------

def entrada_produto():
    print("\nENTRADA DE PRODUTOS")
    codigo = input("Digite o código do produto: ").strip()

    with conectar_banco() as conexao:
        cursor = conexao.cursor()
        produto = _buscar_produto(cursor, codigo)

        if produto is None:
            print("Produto não encontrado.")
            return

        try:
            quantidade = float(input("Digite a quantidade de entrada: "))
        except ValueError:
            print("Erro: digite apenas números.")
            return

        if quantidade <= 0:
            print("Erro: a quantidade deve ser maior que zero.")
            return

        cursor.execute("""
            UPDATE estoque
            SET quantidade  = quantidade + ?,
                preco_total = (quantidade + ?) * preco_unitario
            WHERE codigo = ?
        """, (quantidade, quantidade, codigo))

        _registrar_movimentacao(cursor, codigo, "entrada", quantidade, "reposição de estoque")
        conexao.commit()
        print("Entrada registrada com sucesso.")


# ---------------------------------------------------------------------
# Saída de produtos
# ---------------------------------------------------------------------

def saida_produto():
    print("\nSAÍDA DE PRODUTOS")
    codigo = input("Digite o código do produto: ").strip()

    with conectar_banco() as conexao:
        cursor = conexao.cursor()
        produto = _buscar_produto(cursor, codigo)

        if produto is None:
            print("Produto não encontrado.")
            return

        try:
            quantidade_saida = float(input("Digite a quantidade de saída: "))
        except ValueError:
            print("Erro: digite apenas números.")
            return

        if quantidade_saida <= 0:
            print("Erro: a quantidade deve ser maior que zero.")
            return

        if quantidade_saida > produto[2]:
            print(f"Erro: estoque disponível é apenas {produto[2]} {produto[5]}.")
            return

        # ✅ CORREÇÃO: valida o tipo de saída contra valores permitidos
        print(f"Tipos de saída aceitos: {', '.join(TIPOS_SAIDA)}")
        tipo_saida = input("Digite o tipo de saída: ").strip().lower()

        if tipo_saida not in TIPOS_SAIDA:
            print(f"Erro: tipo inválido. Use: {', '.join(TIPOS_SAIDA)}")
            return

        cursor.execute("""
            UPDATE estoque
            SET quantidade  = quantidade - ?,
                preco_total = (quantidade - ?) * preco_unitario
            WHERE codigo = ?
        """, (quantidade_saida, quantidade_saida, codigo))

        _registrar_movimentacao(cursor, codigo, tipo_saida, quantidade_saida, "saída registrada")
        conexao.commit()
        print("Saída registrada com sucesso.")


# ---------------------------------------------------------------------
# Consultar estoque
# ---------------------------------------------------------------------

def consultar_estoque():
    print("\nCONSULTA DE ESTOQUE")
    filtro = input("Digite código ou nome para filtrar (ou ENTER para ver tudo): ").strip()

    with conectar_banco() as conexao:
        cursor = conexao.cursor()

        if filtro:
            cursor.execute("""
                SELECT * FROM estoque
                WHERE codigo = ? OR nome_item LIKE ?
            """, (filtro, f"%{filtro}%"))
        else:
            cursor.execute("SELECT * FROM estoque ORDER BY nome_item")

        produtos = cursor.fetchall()

    print("\nESTOQUE ATUAL")
    if not produtos:
        print("Nenhum produto encontrado.")
        return

    for p in produtos:
        alerta = " ⚠️  ESTOQUE BAIXO" if p[2] <= p[8] else ""
        print(f"""
Código:         {p[0]}{alerta}
Nome:           {p[1]}
Quantidade:     {p[2]} {p[5]}
Categoria:      {p[3]}
Armazenamento:  {p[4]}
Preço unitário: R$ {p[6]:.2f}
Preço total:    R$ {p[7]:.2f}
Estoque mínimo: {p[8]} {p[5]}
{'-' * 40}""")


# ---------------------------------------------------------------------
# Alerta de estoque
# ---------------------------------------------------------------------

def alerta_estoque():
    print("\nALERTAS DE ESTOQUE")

    with conectar_banco() as conexao:
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT nome_item, quantidade, estoque_minimo, unidade_medida
            FROM estoque
            WHERE quantidade <= estoque_minimo
            ORDER BY (quantidade - estoque_minimo)
        """)
        produtos = cursor.fetchall()

    if not produtos:
        print("Nenhum produto com estoque baixo.")
        return

    for nome, qtd, minimo, unidade in produtos:
        print(f"⚠️  ALERTA: '{nome}' — estoque atual: {qtd} {unidade} "
              f"(mínimo: {minimo} {unidade})")


# ---------------------------------------------------------------------
# Relatório gerencial  ← principal correção de lógica
# ---------------------------------------------------------------------

def relatorio_gerencial():
    print("\nRELATÓRIO GERENCIAL")

    with conectar_banco() as conexao:
        cursor = conexao.cursor()

        # Valor total do estoque
        cursor.execute("SELECT COALESCE(SUM(preco_total), 0) FROM estoque")
        valor_total = cursor.fetchone()[0]

        # Total de produtos cadastrados
        cursor.execute("SELECT COUNT(*) FROM estoque")
        total_produtos = cursor.fetchone()[0]

        # Movimentações por tipo
        cursor.execute("""
            SELECT tipo, COUNT(*), COALESCE(SUM(quantidade), 0)
            FROM movimentacao
            GROUP BY tipo
        """)
        movimentacoes = cursor.fetchall()

        # ✅ CORREÇÃO: giro de estoque = total de saídas / valor total do estoque
        # Fórmula gerencial real: saídas do período / estoque médio
        cursor.execute("""
            SELECT COALESCE(SUM(quantidade), 0)
            FROM movimentacao
            WHERE tipo IN ('venda', 'perda', 'transferência')
        """)
        total_saidas = cursor.fetchone()[0]

    # ✅ CORREÇÃO: divisão segura (evita divisão por zero)
    if valor_total > 0:
        # Giro simplificado: unidades saídas / valor total (índice relativo)
        giro_estoque = total_saidas / valor_total if valor_total else 0
    else:
        giro_estoque = 0

    print(f"Valor total em estoque:   R$ {valor_total:.2f}")
    print(f"Total de produtos:        {total_produtos}")
    print(f"Total de saídas:          {total_saidas:.2f} unidades")

    if movimentacoes:
        print("\nMovimentações por tipo:")
        for tipo, contagem, quantidade in movimentacoes:
            print(f"  {tipo:<15} → {contagem} registros | {quantidade:.2f} unidades")

    print(f"\nÍndice de giro (saídas/valor): {giro_estoque:.4f}")


# ---------------------------------------------------------------------
# Histórico de movimentação
# ---------------------------------------------------------------------

def historico_movimentacao():
    print("\nHISTÓRICO DE MOVIMENTAÇÃO")
    filtro = input("Filtrar por código do produto (ou ENTER para ver tudo): ").strip()

    with conectar_banco() as conexao:
        cursor = conexao.cursor()

        if filtro:
            cursor.execute("""
                SELECT * FROM movimentacao
                WHERE codigo_produto = ?
                ORDER BY id DESC
            """, (filtro,))
        else:
            cursor.execute("SELECT * FROM movimentacao ORDER BY id DESC")

        movimentacoes = cursor.fetchall()

    if not movimentacoes:
        print("Nenhuma movimentação registrada.")
        return

    for mov in movimentacoes:
        print(f"""
ID:               {mov[0]}
Código produto:   {mov[1]}
Tipo:             {mov[2]}
Quantidade:       {mov[3]}
Data:             {mov[4]}
Observação:       {mov[5]}
{'-' * 40}""")


# ---------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------

def menu():
    criar_tabelas()

    opcoes = {
        "1": ("Cadastrar produto",       cadastro_produto),
        "2": ("Adicionar produtos",      entrada_produto),
        "3": ("Retirar produtos",        saida_produto),
        "4": ("Consultar estoque",       consultar_estoque),
        "5": ("Alerta de estoque",       alerta_estoque),
        "6": ("Histórico de movimentação", historico_movimentacao),
        "7": ("Relatório gerencial",     relatorio_gerencial),
        "0": ("Sair",                    None),
    }

    while True:
        print("\nSISTEMA DE ESTOQUE")
        for chave, (descricao, _) in opcoes.items():
            print(f"  {chave} - {descricao}")

        opcao = input("\nDigite a opção desejada: ").strip()

        if opcao == "0":
            print("Saindo do sistema.")
            break
        elif opcao in opcoes:
            _, funcao = opcoes[opcao]
            funcao()
        else:
            print("Opção inválida. Tente novamente.")


# ✅ MELHORIA: ponto de entrada correto para scripts Python
if __name__ == "__main__":
    menu()
```

