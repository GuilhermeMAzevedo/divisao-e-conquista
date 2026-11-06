import argparse
import math
import sys

LIMIAR = 3

def distancia(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def _comparar_todos(pontos):
    n = len(pontos)
    melhor = math.inf
    par = None
    for i in range(n - 1):
        for j in range(i + 1, n):
            d = distancia(pontos[i], pontos[j])
            if d < melhor:
                melhor = d
                par = (pontos[i], pontos[j])
    return melhor, par


def forca_bruta(pontos):
    if len(pontos) < 2:
        raise ValueError("são necessários pelo menos 2 pontos")
    return _comparar_todos(pontos)


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


def divisao_e_conquista_recursiva(pontos_ordenados_por_x, limiar):
    n = len(pontos_ordenados_por_x)

    if n <= limiar:
        menor_distancia, melhor_par = _comparar_todos(pontos_ordenados_por_x)
        pontos_ordenados_por_y = sorted(pontos_ordenados_por_x, key=lambda p: p[1])
        return menor_distancia, melhor_par, pontos_ordenados_por_y

    meio = n // 2
    x_da_linha_divisoria = pontos_ordenados_por_x[meio][0]
    metade_esquerda = pontos_ordenados_por_x[:meio]
    metade_direita = pontos_ordenados_por_x[meio:]

    menor_distancia_esquerda, par_esquerda, esquerda_por_y = divisao_e_conquista_recursiva(metade_esquerda, limiar)
    menor_distancia_direita, par_direita, direita_por_y = divisao_e_conquista_recursiva(metade_direita, limiar)

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


def divisao_e_conquista(pontos, limiar=LIMIAR):
    if len(pontos) < 2:
        raise ValueError("são necessários pelo menos 2 pontos")
    if limiar < 1:
        raise ValueError("o limiar precisa ser pelo menos 1")
    pontos_ordenados_por_x = sorted(pontos, key=lambda p: p[0])
    menor_distancia, melhor_par, _ = divisao_e_conquista_recursiva(pontos_ordenados_por_x, limiar)
    return menor_distancia, melhor_par


ALGORITMOS = {
    "dc": divisao_e_conquista,
    "forca-bruta": forca_bruta,
}


def ler_entrada(texto):
    dados = texto.split()
    if not dados:
        raise ValueError("entrada vazia")
    n = int(dados[0])
    if n < 2:
        raise ValueError("são necessários pelo menos 2 pontos")
    valores = dados[1:1 + 2 * n]
    if len(valores) < 2 * n:
        raise ValueError("esperava {} coordenadas, recebi {}".format(2 * n, len(valores)))
    return [(float(valores[2 * i]), float(valores[2 * i + 1])) for i in range(n)]


def _numero(valor):
    return str(int(valor)) if valor.is_integer() else repr(valor)


def formatar_saida(menor_distancia, par):
    p, q = sorted(par)
    return "{:.6f} {} {} {} {}".format(menor_distancia, _numero(p[0]), _numero(p[1]),
                                       _numero(q[0]), _numero(q[1]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Par de pontos mais próximos")
    parser.add_argument("--algoritmo", choices=ALGORITMOS, default="dc",
                        help="versão a executar (padrão: dc)")
    args = parser.parse_args(argv)
    try:
        pontos = ler_entrada(sys.stdin.read())
        menor_distancia, par = ALGORITMOS[args.algoritmo](pontos)
    except ValueError as erro:
        sys.exit("erro: {}".format(erro))
    print(formatar_saida(menor_distancia, par))


if __name__ == "__main__":
    main()