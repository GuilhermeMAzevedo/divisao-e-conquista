def forca_bruta(vetor):
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


def cruzando(vetor, low, meio, high):
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


def divisao_e_conquista(vetor, low, high):
    if low == high:
        return vetor[low], low, low
    meio = (low + high) // 2
    esq = divisao_e_conquista(vetor, low, meio)
    dir = divisao_e_conquista(vetor, meio + 1, high)
    cruz = cruzando(vetor, low, meio, high)
    return max(esq, dir, cruz, key=lambda x: (x[0], -x[1], -x[2]))


if __name__ == "__main__":
    dados = input().split()
    n = int(dados[0])
    vetor = [int(x) for x in dados[1:n + 1]]
    soma, inicio, fim = divisao_e_conquista(vetor, 0, n - 1)
    print(soma, inicio, fim)