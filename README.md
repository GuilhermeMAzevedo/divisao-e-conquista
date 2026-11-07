# Divisão e Conquista

Trabalho prático de Projeto e Análise de Algoritmos. Implementamos algoritmos baseados na técnica de divisão e conquista, comparamos cada um com uma solução de força bruta e verificamos experimentalmente se o tempo de execução segue a complexidade prevista pela recorrência.

**Dupla:** Francisco Magno e Guilherme Moreira
**Linguagem:** Python 3.8 ou superior
**Entrega:** 06/11/2026

## Problemas

| Etapa | Problema | Força bruta | Divisão e conquista |
|---|---|---|---|
| 1 | Subarray de soma máxima | O(n²) | O(n log n), com o melhor subarray que cruza o meio calculado em O(n) |
| 2 | Par de pontos mais próximos | O(n²) | O(n log n), com faixa de largura 2δ e no máximo 7 vizinhos por ponto |
| 3 | Análise experimental | Medição de tempos, tabela, gráfico e CSV | |

### Etapa 1: Subarray de Soma Máxima

Dada a variação diária do preço de uma ação (valores positivos e negativos), encontrar o intervalo contínuo de dias com o maior ganho acumulado.

- **Entrada:** um inteiro `n` seguido de `n` inteiros.
- **Saída:** a soma máxima e os índices de início e fim do intervalo.

A divisão e conquista divide o vetor ao meio e resolve cada metade recursivamente. A resposta é a maior de três soluções: o melhor subarray inteiro na metade esquerda, o melhor inteiro na metade direita e o melhor que cruza o meio.

**Recorrência:** T(n) = 2T(n/2) + O(n), que resulta em O(n log n).

### Etapa 2: Par de Pontos Mais Próximos

Dadas as coordenadas de `n` estações de monitoramento em um plano, encontrar as duas estações mais próximas entre si.

1. Dividir os pontos por uma linha vertical na mediana das coordenadas x.
2. Resolver cada lado recursivamente, obtendo a menor distância δ.
3. Verificar só os pontos dentro de uma faixa de largura 2δ em torno da linha, comparando cada ponto com no máximo 7 vizinhos ordenados por y.

A ordenação inicial por x e por y usa a função da biblioteca padrão. O relatório justifica por que bastam 7 comparações por ponto na faixa.

**Recorrência:** T(n) = 2T(n/2) + O(n), que resulta em O(n log n).

## Estrutura do repositório

```
divisao-e-conquista/
├── README.md
├── LICENSE
├── requirements.txt         # dependências (matplotlib, só para os gráficos)
├── etapa1.py                # subarranjo de soma máxima: força bruta, D&C e Kadane
├── etapa2.py                # par de pontos mais próximos: força bruta e D&C
├── medicao.py               # Etapa 3: mede os tempos e gera CSVs, tabela e gráficos
├── resultados.csv           # medições brutas (uma linha por execução)
├── resultados_limiar.csv    # medições do experimento do limiar da Etapa 2
├── maquina.txt              # configuração da máquina usada nas medições
├── graficos/
│   ├── tabela.md            # tempos médios e desvios padrão
│   ├── etapa1_tempo.png     # tempo × n
│   ├── etapa1_razao.png     # tempo dividido pela complexidade esperada
│   ├── etapa2_tempo.png
│   ├── etapa2_razao.png
│   └── etapa2_limiar.png    # tempo da D&C para cada limiar
├── testes/
│   ├── casos_etapa1.txt     # entradas, saídas esperadas e motivo de cada caso
│   ├── casos_etapa2.txt
│   ├── test_etapa1.py
│   └── test_etapa2.py
├── relatorio.tex            # fonte do relatório em LaTeX
└── relatorio.pdf            # relatório compilado, até 8 páginas
```

## Como executar

Requisitos: Python 3.8 ou superior. Só a Etapa 3 precisa de uma biblioteca externa (`matplotlib`, para os gráficos):

```bash
pip install -r requirements.txt
```

### Etapa 1

A entrada é `n` seguido dos `n` inteiros:

```bash
echo "9 -2 1 -3 4 -1 2 1 -5 4" | python etapa1.py
```

Saída esperada (soma, índice inicial, índice final):

```
6 3 6
```

### Etapa 2
A entrada é `n` seguido das `n` coordenadas `x y`:

    printf "3\n0 0\n3 4\n10 10\n" | python etapa2.py

Saída (distância com 6 casas e os dois pontos):

    5.000000 0 0 3 4
### Medições

```bash
python medicao.py
```

Gera o arquivo `resultados.csv` com as medições brutas e os gráficos.

## Testes

```bash
python -m unittest discover -s testes -v
```

Os testes comparam a força bruta com a divisão e conquista e conferem os casos de `testes/casos_*.txt`.

### Casos de borda cobertos (Etapa 1)

| Caso | Por que importa |
|---|---|
| Vetor só com valores negativos | A resposta é o maior elemento, nunca um intervalo vazio de soma 0 |
| Vetor de tamanho 1 | Caso base da recursão |
| Empates entre intervalos de mesma soma | As duas versões precisam escolher o mesmo intervalo |
| Todos os valores positivos | O intervalo é o vetor inteiro |
| Todos os valores zero | Empate total entre todos os intervalos |
| Melhor intervalo cruzando o meio | Exercita a função que combina as duas metades |

### Regra de desempate

Quando vários intervalos têm a mesma soma máxima, escolhemos o que começa mais cedo; se ainda houver empate, o que termina mais cedo. A força bruta e a divisão e conquista seguem a mesma regra.

## Análise experimental

- Cada algoritmo foi medido para tamanhos crescentes de entrada, com média de pelo menos 5 execuções por tamanho. Tamanhos: 100, 200, 400, 800, 1600, 3200 e 6400.
- As medições brutas estão em `resultados.csv`.
- A tabela, os gráficos, a discussão e a justificativa do limiar escolhido na Etapa 2 estão em `relatorio.pdf`.

### Configuração da máquina

| Item | Valor |
|---|---|
| Processador | [modelo] |
| Memória RAM | [quantidade] |
| Sistema operacional | [nome e versão] |
| Python | [versão] |

## Relatório

O `relatorio.pdf` (até 8 páginas) contém:

- A recorrência de cada algoritmo e sua resolução.
- A discussão dos gráficos, comparando o comportamento observado com o previsto pela análise.
- A análise de por que a força bruta ou a técnica vence para tamanhos diferentes.
- A justificativa do limiar escolhido na Etapa 2.

## Critérios de avaliação

| Critério | Peso |
|---|---|
| Código (Etapas 1 e 2, incluindo a versão O(n) da questão desafio) | 30% |
| Testes (bateria própria, com casos de borda justificados) | 40% |
| Análise e relatório | 30% |