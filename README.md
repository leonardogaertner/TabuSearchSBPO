# TabuSearchSBPO

Este repositório contém a implementação completa de uma abordagem baseada na **metaheurística Busca Tabu** para resolver o problema de **seleção ótima de pedidos e corredores** em ambientes logísticos com restrições de capacidade e suprimento.

## 📌 Objetivo

Maximizar a razão entre a quantidade total de unidades processadas e o número de corredores utilizados, respeitando limites inferiores e superiores de capacidade e a disponibilidade de itens em estoque.

## 🧠 Algoritmo

A solução implementa a metaheurística **Tabu Search**, com os seguintes recursos:

- Lista tabu com `tenure` ajustável
- Oscilação estratégica (expansão e contração)
- Geração de vizinhança com operadores de adição, remoção e troca
- Critério de aspiração
- Controle de estagnação por tempo e iteração
- Pós-processamento para refinar soluções com alta demanda
- Ajuste automático de parâmetros (`ajuste_parametros.py`)

## 📂 Estrutura do Repositório

```
├── main.py                   # Executa a Busca Tabu com parâmetros fixos
├── ajuste_parametros.py     # Busca os melhores parâmetros (tenure, iterações, vizinhança)
├── teste-resultados.py      # Testa o desempenho com os parâmetros otimizados
├── instances/               # Instâncias de entrada do problema
├── results/                 # Arquivos de saída gerados
├── ajuste_parametros_resultado.xlsx  # Resultados paramétricos
├── artigo/                  # Artigo científico em LaTeX (formato SBPO)
└── README.md
```

## ▶️ Como Executar

### Requisitos:
- Python 3.7+
- Bibliotecas: `numpy`, `pandas` (para análise), `openpyxl` (para planilhas)

Instale com:

```bash
pip install -r requirements.txt
```

### Executar a busca principal:

```bash
python main.py instance_0001.txt output_0001.txt
```

### Ajustar parâmetros:

```bash
python ajuste_parametros.py
```

### Testar instâncias com parâmetros definidos:

```bash
python teste-resultados.py
```

## 📈 Resultados

Os testes foram realizados em diversas instâncias com diferentes configurações. Os dados experimentais podem ser consultados em:

- `ajuste_parametros_resultado.xlsx`
- Gráficos e tabelas no artigo disponível em `/artigo`

## 📄 Artigo

Este repositório acompanha o artigo submetido ao **Simpósio Brasileiro de Pesquisa Operacional (SBPO)**. O texto completo está disponível no diretório `/artigo`.

## 🧑‍💻 Autor

- Leonardo Gaertner — [@leonardogaertner](https://github.com/leonardogaertner)

## 📜 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
