import argparse
import sys
from typing import List, Optional, Tuple

Resultado = Tuple[int, int, int]


def _validar(vetor: List[int]) -> None:
    if not vetor:
        raise ValueError("o vetor precisa ter pelo menos um elemento")


def forca_bruta(vetor: List[int]) -> Resultado:
    _validar(vetor)
    n = len(vetor)
    melhor = vetor[0]
    inicio = 0
    fim = 0
    for i in range(n):
        soma = 0
        for j in range(i, n):
            soma = soma + vetor[j]
            if soma > melhor:
                melhor = soma
                inicio = i
                fim = j
    return melhor, inicio, fim


def cruzando(vetor: List[int], low: int, meio: int, high: int) -> Resultado:
    soma = 0
    melhor_esq = vetor[meio]
    inicio = meio
    for i in range(meio, low - 1, -1):
        soma = soma + vetor[i]
        if soma >= melhor_esq:
            melhor_esq = soma
            inicio = i

    soma = 0
    melhor_dir = vetor[meio + 1]
    fim = meio + 1
    for j in range(meio + 1, high + 1):
        soma = soma + vetor[j]
        if soma > melhor_dir:
            melhor_dir = soma
            fim = j

    return melhor_esq + melhor_dir, inicio, fim


def divisao_e_conquista(vetor: List[int], low: int = 0, high: Optional[int] = None) -> Resultado:
    if high is None:
        _validar(vetor)
        high = len(vetor) - 1
    if low == high:
        return vetor[low], low, low
    meio = (low + high) // 2
    esquerda = divisao_e_conquista(vetor, low, meio)
    direita = divisao_e_conquista(vetor, meio + 1, high)
    cruz = cruzando(vetor, low, meio, high)
    return max(esquerda, direita, cruz, key=lambda x: (x[0], -x[1], -x[2]))


def kadane(vetor: List[int]) -> Resultado:
    _validar(vetor)
    melhor = (vetor[0], 0, 0)
    soma_atual = vetor[0]
    inicio_atual = 0
    for j in range(1, len(vetor)):
        if soma_atual < 0:
            soma_atual = vetor[j]
            inicio_atual = j
        else:
            soma_atual = soma_atual + vetor[j]
        if soma_atual > melhor[0]:
            melhor = (soma_atual, inicio_atual, j)
    return melhor


ALGORITMOS = {
    "dc": divisao_e_conquista,
    "forca-bruta": forca_bruta,
    "kadane": kadane,
}


def ler_entrada(texto: str) -> List[int]:
    dados = texto.split()
    if not dados:
        raise ValueError("entrada vazia")
    n = int(dados[0])
    valores = dados[1:n + 1]
    if len(valores) < n:
        raise ValueError("esperava {} inteiros, recebi {}".format(n, len(valores)))
    return [int(x) for x in valores]


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Subarranjo de soma máxima")
    parser.add_argument("--algoritmo", choices=ALGORITMOS, default="dc",
                        help="versão a executar (padrão: dc)")
    args = parser.parse_args(argv)
    try:
        vetor = ler_entrada(sys.stdin.read())
        soma, inicio, fim = ALGORITMOS[args.algoritmo](vetor)
    except ValueError as erro:
        sys.exit("erro: {}".format(erro))
    print(soma, inicio, fim)


if __name__ == "__main__":
    main()