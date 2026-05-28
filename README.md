📦 Sistema de Controle de Estoque (Python + SQLite)

Este projeto é um sistema de controle de estoque desenvolvido em Python com banco de dados SQLite. Ele permite cadastrar produtos, registrar entradas e saídas, consultar o estoque em tempo real, gerar alertas de baixo estoque e visualizar relatórios gerenciais e histórico de movimentações.

🚀 Funcionalidades
📌 Cadastro de Produtos
Cadastro de novos itens no estoque
Validação de código com 3 dígitos
Registro de preço unitário e cálculo automático do valor total
Armazena categoria, unidade de medida e local de armazenamento
📥 Entrada de Produtos
Adiciona quantidade ao estoque existente
Atualiza automaticamente o valor total do produto
Registra movimentação no histórico
📤 Saída de Produtos
Remove quantidade do estoque
Impede saída maior que o estoque disponível
Registra tipo de saída:
venda
perda
transferência
Atualiza valor total automaticamente
📊 Consulta de Estoque
Exibe todos os produtos cadastrados
Mostra informações completas:
Código
Nome
Quantidade
Categoria
Armazenamento
Unidade de medida
Preço unitário e total
Estoque mínimo
⚠️ Alerta de Estoque
Identifica produtos abaixo do estoque mínimo
Exibe alerta automático para reposição
📈 Relatório Gerencial
Soma total do valor do estoque
Total de movimentações registradas
Cálculo de giro de estoque
Indicadores de desempenho do sistema
🕒 Histórico de Movimentações
Registro completo de todas as entradas e saídas
Exibe:
ID
Código do produto
Tipo de movimentação
Quantidade
Data
Observação
🗄️ Estrutura do Banco de Dados
Tabela: estoque
Campo	Tipo	Descrição
codigo	TEXT	Código do produto (PK)
nome_item	TEXT	Nome do produto
quantidade	REAL	Quantidade em estoque
categoria	TEXT	Categoria do produto
armazenar	TEXT	Local de armazenamento
unidade_medida	TEXT	Unidade (kg, un, L etc)
preco_unitario	REAL	Preço por unidade
preco_total	REAL	Valor total do estoque
estoque_minimo	REAL	Limite mínimo
Tabela: movimentacao
Campo	Tipo	Descrição
id	INTEGER	ID automático
codigo_produto	TEXT	Produto relacionado
tipo	TEXT	entrada / saída
quantidade	REAL	Quantidade movimentada
data	TEXT	Data e hora
observacao	TEXT	Detalhes da movimentação
🧠 Tecnologias Utilizadas
Python 3
SQLite3 (banco de dados local)
Biblioteca datetime
▶️ Como Executar o Projeto
Instale o Python 3

Salve o arquivo como:

estoque.py

Execute no terminal:

python estoque.py
📌 Menu do Sistema
1 - Cadastrar produto
2 - Adicionar produtos
3 - Retirar produtos
4 - Consultar em estoque
5 - Alerta de estoque
6 - Histórico de movimentação
7 - Relatório gerencial
0 - Sair
⚠️ Observações
O banco de dados estoque.db é criado automaticamente.
Todas as movimentações são registradas automaticamente.
O sistema funciona em modo terminal (CLI).
📊 Melhorias Futuras
Interface gráfica (Tkinter ou Web)
Login de usuários
Exportação de relatórios em PDF/Excel
Dashboard com gráficos
API para integração com sistemas externos
👨‍💻 Autor

Projeto desenvolvido para fins educacionais, com foco em lógica de programação, banco de dados e automação de processos.
