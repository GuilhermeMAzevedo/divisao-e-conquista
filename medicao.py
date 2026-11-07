import argparse
import csv
import functools
import gc
import importlib
import inspect
import math
import os
import platform
import random
import statistics
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
ARQ_CSV = RAIZ / "resultados.csv"
ARQ_CSV_LIMIAR = RAIZ / "resultados_limiar.csv"
ARQ_MAQUINA = RAIZ / "maquina.txt"
PASTA_GRAFICOS = RAIZ / "graficos"

TAMANHOS = [10, 25, 50, 100, 200, 400, 800, 1600, 3200, 6400]
REPETICOES = 5
LIMIARES = [2, 3, 4, 8, 16, 32, 64]
N_LIMIAR = 6400
SEMENTE = 2026

COMPLEXIDADES = {
    "n": lambda n: n,
    "n log n": lambda n: n * math.log2(n),
    "n²": lambda n: n * n,
}


def gerar_vetor(n, rng):
    return [rng.randint(-100, 100) for _ in range(n)]


def gerar_pontos(n, rng):
    return [(rng.uniform(0, 10**6), rng.uniform(0, 10**6)) for _ in range(n)]


def carregar_algoritmos():
    import etapa1
    algoritmos = [
        ("1", "forca_bruta", etapa1.forca_bruta, gerar_vetor, "n²"),
        ("1", "divisao_e_conquista", etapa1.divisao_e_conquista, gerar_vetor, "n log n"),
        ("1", "kadane", etapa1.kadane, gerar_vetor, "n"),
    ]
    try:
        etapa2 = importlib.import_module("etapa2")
        algoritmos += [
            ("2", "forca_bruta", etapa2.forca_bruta, gerar_pontos, "n²"),
            ("2", "divisao_e_conquista", etapa2.divisao_e_conquista, gerar_pontos, "n log n"),
        ]
    except (ImportError, AttributeError) as erro:
        print("Etapa 2 ignorada: {}".format(erro))
    return algoritmos


def cronometrar(funcao, entrada):
    copia = list(entrada)
    gc.collect()
    estava_ativo = gc.isenabled()
    gc.disable()
    try:
        inicio = time.perf_counter()
        funcao(copia)
        return time.perf_counter() - inicio
    finally:
        if estava_ativo:
            gc.enable()


def medir(algoritmos, tamanhos, repeticoes):
    linhas = []
    etapas = sorted({a[0] for a in algoritmos})
    for etapa in etapas:
        da_etapa = [a for a in algoritmos if a[0] == etapa]
        gerador = da_etapa[0][3]
        aquecimento = gerador(100, random.Random(SEMENTE))
        for _, _, funcao, _, _ in da_etapa:
            funcao(list(aquecimento))
        for n in tamanhos:
            for rep in range(1, repeticoes + 1):
                entrada = gerador(n, random.Random(SEMENTE + 1000 * n + rep))
                for _, nome, funcao, _, _ in da_etapa:
                    tempo = cronometrar(funcao, entrada)
                    linhas.append({"etapa": etapa, "algoritmo": nome, "n": n,
                                   "repeticao": rep, "tempo_s": tempo})
            print("  Etapa {}: n = {} concluído".format(etapa, n))
    return linhas


def medir_limiar(repeticoes, n):
    try:
        etapa2 = importlib.import_module("etapa2")
        funcao = etapa2.divisao_e_conquista
    except (ImportError, AttributeError):
        return []
    if "limiar" not in inspect.signature(funcao).parameters:
        print("Experimento do limiar ignorado: divisao_e_conquista não tem o parâmetro limiar.")
        return []
    entradas = [gerar_pontos(n, random.Random(SEMENTE + 7 * rep)) for rep in range(1, repeticoes + 1)]
    linhas = []
    for limiar in LIMIARES:
        versao = functools.partial(funcao, limiar=limiar)
        versao(list(entradas[0]))
        for rep, entrada in enumerate(entradas, start=1):
            linhas.append({"limiar": limiar, "n": n, "repeticao": rep,
                           "tempo_s": cronometrar(versao, entrada)})
        print("  Limiar {} concluído".format(limiar))
    return linhas


def nome_processador():
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if linha.startswith("model name"):
                    return linha.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine() or "preencher manualmente"


def memoria_ram():
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        return "{:.1f} GB".format(total / 1024**3)
    except (AttributeError, ValueError, OSError):
        return "preencher manualmente"


def configuracao_maquina():
    return {
        "Processador": nome_processador(),
        "Memória RAM": memoria_ram(),
        "Sistema operacional": platform.platform(),
        "Python": "{} {}".format(platform.python_implementation(), platform.python_version()),
    }


def salvar_csv(caminho, linhas):
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()),
                                  lineterminator="\n")
        escritor.writeheader()
        for linha in linhas:
            linha = dict(linha)
            linha["tempo_s"] = "{:.9f}".format(linha["tempo_s"])
            escritor.writerow(linha)


def ler_csv(caminho):
    if not caminho.exists():
        return []
    with open(caminho, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))
    for linha in linhas:
        linha["tempo_s"] = float(linha["tempo_s"])
        linha["n"] = int(linha["n"])
        if "limiar" in linha:
            linha["limiar"] = int(linha["limiar"])
    return linhas


def agrupar(linhas, *chaves):
    grupos = {}
    for linha in linhas:
        grupos.setdefault(tuple(linha[c] for c in chaves), []).append(linha["tempo_s"])
    return grupos


def tabela_markdown(linhas):
    grupos = agrupar(linhas, "etapa", "algoritmo", "n")
    partes = []
    for etapa in sorted({l["etapa"] for l in linhas}):
        nomes = sorted({l["algoritmo"] for l in linhas if l["etapa"] == etapa})
        tamanhos = sorted({l["n"] for l in linhas if l["etapa"] == etapa})
        partes.append("### Etapa {}: tempo médio em ms (desvio padrão)\n".format(etapa))
        partes.append("| n | " + " | ".join(nomes) + " |")
        partes.append("|---" * (len(nomes) + 1) + "|")
        for n in tamanhos:
            celulas = []
            for nome in nomes:
                tempos = grupos.get((etapa, nome, n), [])
                media = statistics.mean(tempos) * 1000
                desvio = statistics.stdev(tempos) * 1000 if len(tempos) > 1 else 0.0
                celulas.append("{:.3f} ({:.3f})".format(media, desvio))
            partes.append("| {} | ".format(n) + " | ".join(celulas) + " |")
        partes.append("")
    return "\n".join(partes)


def ponto_de_virada(linhas):
    grupos = agrupar(linhas, "etapa", "algoritmo", "n")
    resultado = {}
    for etapa in sorted({l["etapa"] for l in linhas}):
        tamanhos = sorted({l["n"] for l in linhas if l["etapa"] == etapa})
        virada = None
        for n in reversed(tamanhos):
            bruta = grupos.get((etapa, "forca_bruta", n))
            dc = grupos.get((etapa, "divisao_e_conquista", n))
            if not bruta or not dc or statistics.mean(dc) >= statistics.mean(bruta):
                break
            virada = n
        resultado[etapa] = virada
    return resultado


NOMES_LATEX = {
    "forca_bruta": "Força bruta",
    "divisao_e_conquista": "Divisão e conquista",
    "kadane": "Kadane",
}


def _ms(segundos):
    return "{:.3f}".format(segundos * 1000).replace(".", ",")


def tabelas_latex(linhas, linhas_limiar):
    PASTA_GRAFICOS.mkdir(exist_ok=True)
    grupos = agrupar(linhas, "etapa", "algoritmo", "n")
    for etapa in sorted({l["etapa"] for l in linhas}):
        presentes = {l["algoritmo"] for l in linhas if l["etapa"] == etapa}
        nomes = [n for n in NOMES_LATEX if n in presentes]
        tamanhos = sorted({l["n"] for l in linhas if l["etapa"] == etapa})
        partes = [
            "\\begin{tabular}{r" + "r" * len(nomes) + "}",
            "\\toprule",
            "$n$ & " + " & ".join(NOMES_LATEX[n] for n in nomes) + " \\\\",
            "\\midrule",
        ]
        for n in tamanhos:
            celulas = []
            for nome in nomes:
                tempos = grupos[(etapa, nome, n)]
                desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
                celulas.append("{} $\\pm$ {}".format(_ms(statistics.mean(tempos)), _ms(desvio)))
            partes.append("{} & ".format(n) + " & ".join(celulas) + " \\\\")
        partes += ["\\bottomrule", "\\end{tabular}", ""]
        (PASTA_GRAFICOS / "tabela_etapa{}.tex".format(etapa)).write_text("\n".join(partes), encoding="utf-8")

    if linhas_limiar:
        grupos_l = agrupar(linhas_limiar, "limiar")
        limiares = sorted(k[0] for k in grupos_l)
        melhor = min(limiares, key=lambda l: statistics.mean(grupos_l[(l,)]))
        partes = ["\\begin{tabular}{rr}", "\\toprule", "Limiar & Tempo médio (ms) \\\\", "\\midrule"]
        for limiar in limiares:
            tempos = grupos_l[(limiar,)]
            desvio = statistics.stdev(tempos) if len(tempos) > 1 else 0.0
            texto = "{} $\\pm$ {}".format(_ms(statistics.mean(tempos)), _ms(desvio))
            if limiar == melhor:
                texto = "\\textbf{" + texto + "}"
            partes.append("{} & {} \\\\".format(limiar, texto))
        partes += ["\\bottomrule", "\\end{tabular}", ""]
        (PASTA_GRAFICOS / "tabela_limiar.tex").write_text("\n".join(partes), encoding="utf-8")


def gerar_graficos(linhas, linhas_limiar, complexidades):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado: rode pip install -r requirements.txt")
        return
    PASTA_GRAFICOS.mkdir(exist_ok=True)
    grupos = agrupar(linhas, "etapa", "algoritmo", "n")

    for etapa in sorted({l["etapa"] for l in linhas}):
        nomes = sorted({l["algoritmo"] for l in linhas if l["etapa"] == etapa})
        tamanhos = sorted({l["n"] for l in linhas if l["etapa"] == etapa})

        fig, ax = plt.subplots(figsize=(7, 4.5))
        for nome in nomes:
            medias = [statistics.mean(grupos[(etapa, nome, n)]) * 1000 for n in tamanhos]
            ax.plot(tamanhos, medias, marker="o", label="{} (esperado: {})".format(
                nome, complexidades.get((etapa, nome), "?")))
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks(tamanhos)
        ax.set_xticklabels([str(n) for n in tamanhos], rotation=45)
        ax.minorticks_off()
        ax.set_xlabel("n (tamanho da entrada)")
        ax.set_ylabel("tempo médio (ms)")
        ax.set_title("Etapa {}: tempo de execução".format(etapa))
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(PASTA_GRAFICOS / "etapa{}_tempo.png".format(etapa), dpi=150)
        plt.close(fig)

        grandes = [n for n in tamanhos if n >= 100] or tamanhos
        fig, ax = plt.subplots(figsize=(7, 4.5))
        for nome in nomes:
            f = COMPLEXIDADES[complexidades[(etapa, nome)]]
            razoes = [statistics.mean(grupos[(etapa, nome, n)]) / f(n) for n in grandes]
            ax.plot(grandes, [r / razoes[-1] for r in razoes], marker="o",
                    label="{} / {}".format(nome, complexidades[(etapa, nome)]))
        ax.axhline(1, color="gray", linestyle="--", linewidth=1)
        ax.set_xscale("log")
        ax.set_xticks(grandes)
        ax.set_xticklabels([str(n) for n in grandes], rotation=45)
        ax.minorticks_off()
        ax.set_xlabel("n (tamanho da entrada)")
        ax.set_ylabel("tempo / complexidade esperada\n(normalizado em n = {})".format(grandes[-1]))
        ax.set_title("Etapa {}: comparação com a complexidade prevista".format(etapa))
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(PASTA_GRAFICOS / "etapa{}_razao.png".format(etapa), dpi=150)
        plt.close(fig)

    if linhas_limiar:
        grupos_l = agrupar(linhas_limiar, "limiar")
        limiares = sorted(k[0] for k in grupos_l)
        medias = [statistics.mean(grupos_l[(l,)]) * 1000 for l in limiares]
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.plot(limiares, medias, marker="o")
        ax.set_xscale("log", base=2)
        ax.set_xticks(limiares)
        ax.set_xticklabels([str(l) for l in limiares])
        ax.set_xlabel("limiar (n abaixo do qual a recursão usa força bruta)")
        ax.set_ylabel("tempo médio (ms)")
        ax.set_title("Etapa 2: efeito do limiar (n = {})".format(linhas_limiar[0]["n"]))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(PASTA_GRAFICOS / "etapa2_limiar.png", dpi=150)
        plt.close(fig)

    print("Gráficos salvos em {}".format(PASTA_GRAFICOS))


def complexidades_esperadas():
    return {(a[0], a[1]): a[4] for a in carregar_algoritmos()}


def resumir(linhas, linhas_limiar, salvar=False):
    frases = []
    for etapa, n in ponto_de_virada(linhas).items():
        if n is None:
            frases.append("Etapa {}: a D&C não ficou mais rápida em todos os tamanhos a partir de algum n.".format(etapa))
        else:
            frases.append("Etapa {}: a D&C é mais rápida que a força bruta a partir de n = {}.".format(etapa, n))
    if linhas_limiar:
        grupos_l = agrupar(linhas_limiar, "limiar")
        melhor = min(grupos_l, key=lambda k: statistics.mean(grupos_l[k]))[0]
        frases.append("Etapa 2: o limiar mais rápido foi {}.".format(melhor))
    print()
    print(tabela_markdown(linhas))
    print("\n".join(frases))
    if salvar:
        PASTA_GRAFICOS.mkdir(exist_ok=True)
        (PASTA_GRAFICOS / "resumo.txt").write_text("\n".join(frases) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Medição dos tempos (Etapa 3)")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--rapido", action="store_true", help="conferência rápida, sem salvar")
    grupo.add_argument("--so-graficos", action="store_true", help="refaz gráficos a partir dos CSVs")
    args = parser.parse_args()

    if args.so_graficos:
        linhas, linhas_limiar = ler_csv(ARQ_CSV), ler_csv(ARQ_CSV_LIMIAR)
        if not linhas:
            parser.error("{} não encontrado; rode as medições primeiro".format(ARQ_CSV.name))
        gerar_graficos(linhas, linhas_limiar, complexidades_esperadas())
        tabelas_latex(linhas, linhas_limiar)
        resumir(linhas, linhas_limiar, salvar=True)
        return

    maquina = configuracao_maquina()
    print("Configuração da máquina:")
    for chave, valor in maquina.items():
        print("  {}: {}".format(chave, valor))

    algoritmos = carregar_algoritmos()
    if args.rapido:
        linhas = medir(algoritmos, [10, 50, 100, 200], repeticoes=2)
        linhas_limiar = medir_limiar(repeticoes=2, n=200)
        resumir(linhas, linhas_limiar)
        return

    print("Medindo (a força bruta em n = 6400 demora; deixe o computador sem outros programas pesados)...")
    linhas = medir(algoritmos, TAMANHOS, REPETICOES)
    linhas_limiar = medir_limiar(REPETICOES, N_LIMIAR)

    salvar_csv(ARQ_CSV, linhas)
    if linhas_limiar:
        salvar_csv(ARQ_CSV_LIMIAR, linhas_limiar)
    with open(ARQ_MAQUINA, "w", encoding="utf-8") as arquivo:
        for chave, valor in maquina.items():
            arquivo.write("{}: {}\n".format(chave, valor))
    PASTA_GRAFICOS.mkdir(exist_ok=True)
    (PASTA_GRAFICOS / "tabela.md").write_text(tabela_markdown(linhas), encoding="utf-8")

    gerar_graficos(linhas, linhas_limiar, {(a[0], a[1]): a[4] for a in algoritmos})
    tabelas_latex(linhas, linhas_limiar)
    resumir(linhas, linhas_limiar, salvar=True)


if __name__ == "__main__":
    main()