import math
import sys

LIMIAR = 3


# ---------------------------------------------------------------
# Auxiliar
# ---------------------------------------------------------------
def distancia(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# ---------------------------------------------------------------
# 1. Força bruta: compara todos os pares, O(n²)
# ---------------------------------------------------------------
def forca_bruta(pontos):
    n = len(pontos)
    melhor = distancia(pontos[0], pontos[1])
    par = (pontos[0], pontos[1])
    for i in range(n - 1):
        for j in range(i + 1, n):
            d = distancia(pontos[i], pontos[j])
            if d < melhor:
                melhor = d
                par = (pontos[i], pontos[j])
    return melhor, par


# ---------------------------------------------------------------
# 2. Divisão e conquista, O(n log n)
#    Funções na ordem em que são resolvidas: da combinação
#    até a função principal.
# ---------------------------------------------------------------
def combinacao_por_y(esquerda_por_y, direita_por_y):
    resultado_ordenado = []
    i = 0
    j = 0
    while i < len(esquerda_por_y) and j < len(direita_por_y):
        if esquerda_por_y[i][1] <= direita_por_y[j][1]:
            resultado_ordenado.append(esquerda_por_y[i])
            i += 1
        else:
            resultado_ordenado.append(direita_por_y[j])
            j += 1
    resultado_ordenado.extend(esquerda_por_y[i:])
    resultado_ordenado.extend(direita_por_y[j:])
    return resultado_ordenado


def verificar_faixa_central(pontos_ordenados_por_y, x_da_linha_divisoria, menor_distancia, melhor_par):
    pontos_na_faixa = [p for p in pontos_ordenados_por_y
                       if abs(p[0] - x_da_linha_divisoria) < menor_distancia]

    for i in range(len(pontos_na_faixa)):
        for j in range(i + 1, min(i + 8, len(pontos_na_faixa))):
            if pontos_na_faixa[j][1] - pontos_na_faixa[i][1] >= menor_distancia:
                break
            d = distancia(pontos_na_faixa[i], pontos_na_faixa[j])
            if d < menor_distancia:
                menor_distancia = d
                melhor_par = (pontos_na_faixa[i], pontos_na_faixa[j])

    return menor_distancia, melhor_par


def divisao_e_conquista_recursiva(pontos_ordenados_por_x):
    n = len(pontos_ordenados_por_x)

    # caso base
    if n <= LIMIAR:
        menor_distancia, melhor_par = forca_bruta(pontos_ordenados_por_x)
        pontos_ordenados_por_y = sorted(pontos_ordenados_por_x, key=lambda p: p[1])
        return menor_distancia, melhor_par, pontos_ordenados_por_y

    # dividir
    meio = n // 2
    x_da_linha_divisoria = pontos_ordenados_por_x[meio][0]
    metade_esquerda = pontos_ordenados_por_x[:meio]
    metade_direita = pontos_ordenados_por_x[meio:]

    # conquistar
    menor_distancia_esquerda, par_esquerda, esquerda_por_y = divisao_e_conquista_recursiva(metade_esquerda)
    menor_distancia_direita, par_direita, direita_por_y = divisao_e_conquista_recursiva(metade_direita)

    # combinar
    pontos_ordenados_por_y = combinacao_por_y(esquerda_por_y, direita_por_y)

    if menor_distancia_esquerda <= menor_distancia_direita:
        menor_distancia = menor_distancia_esquerda
        melhor_par = par_esquerda
    else:
        menor_distancia = menor_distancia_direita
        melhor_par = par_direita

    menor_distancia, melhor_par = verificar_faixa_central(
        pontos_ordenados_por_y, x_da_linha_divisoria, menor_distancia, melhor_par)

    return menor_distancia, melhor_par, pontos_ordenados_por_y


def divisao_e_conquista(pontos):
    pontos_ordenados_por_x = sorted(pontos, key=lambda p: p[0])
    menor_distancia, melhor_par, _ = divisao_e_conquista_recursiva(pontos_ordenados_por_x)
    return menor_distancia, melhor_par


# ---------------------------------------------------------------
# Entrada e saída
# ---------------------------------------------------------------
if __name__ == "__main__":
    dados = sys.stdin.read().split()
    n = int(dados[0])
    pontos = [(float(dados[1 + 2 * i]), float(dados[2 + 2 * i])) for i in range(n)]
    menor_distancia, melhor_par = divisao_e_conquista(pontos)
    print(menor_distancia, melhor_par)
