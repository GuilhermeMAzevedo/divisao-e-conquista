import random
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from etapa1 import divisao_e_conquista, forca_bruta, kadane

ALGORITMOS = {
    "forca_bruta": forca_bruta,
    "divisao_e_conquista": divisao_e_conquista,
    "kadane": kadane
}
ARQUIVO_CASOS = Path(__file__).resolve().parent / "casos_etapa1.txt"


def ler_casos(caminho):
    casos = []
    atual = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines() + [""]:
        linha = linha.strip()
        if linha.startswith("#"):
            continue
        if not linha:
            if atual:
                casos.append(atual)
                atual = {}
            continue
        chave, _, valor = linha.partition(":")
        atual[chave.strip()] = valor.strip()
    return casos


def vetor_do_caso(caso):
    numeros = [int(x) for x in caso["entrada"].split()]
    n, vetor = numeros[0], numeros[1:]
    if len(vetor) != n:
        raise ValueError("caso '{}': n = {}, mas há {} valores".format(caso["caso"], n, len(vetor)))
    return vetor


def saida_do_caso(caso):
    return tuple(int(x) for x in caso["saida"].split())


class TestCasosDeBorda(unittest.TestCase):

    def test_arquivo_tem_casos(self):
        self.assertGreater(len(ler_casos(ARQUIVO_CASOS)), 0)

    def test_casos_do_arquivo(self):
        for caso in ler_casos(ARQUIVO_CASOS):
            vetor = vetor_do_caso(caso)
            esperado = saida_do_caso(caso)
            for nome, algoritmo in ALGORITMOS.items():
                with self.subTest(caso=caso["caso"], algoritmo=nome):
                    self.assertEqual(algoritmo(vetor), esperado)


class TestDiferencial(unittest.TestCase):

    def comparar(self, semente, quantidade, tamanho_max, menor, maior):
        rng = random.Random(semente)
        for _ in range(quantidade):
            n = rng.randint(1, tamanho_max)
            vetor = [rng.randint(menor, maior) for _ in range(n)]
            esperado = forca_bruta(vetor)
            with self.subTest(vetor=vetor):
                self.assertEqual(divisao_e_conquista(vetor), esperado)
                self.assertEqual(kadane(vetor), esperado)

    def test_valores_pequenos_com_muitos_empates(self):
        self.comparar(semente=2026, quantidade=3000, tamanho_max=15, menor=-3, maior=3)

    def test_valores_grandes(self):
        self.comparar(semente=7, quantidade=300, tamanho_max=80, menor=-10**6, maior=10**6)

    def test_so_negativos_aleatorios(self):
        rng = random.Random(11)
        for _ in range(300):
            vetor = [rng.randint(-50, -1) for _ in range(rng.randint(1, 40))]
            maior = max(vetor)
            esperado = (maior, vetor.index(maior), vetor.index(maior))
            for nome, algoritmo in ALGORITMOS.items():
                with self.subTest(vetor=vetor, algoritmo=nome):
                    self.assertEqual(algoritmo(vetor), esperado)

    def test_so_positivos_aleatorios(self):
        rng = random.Random(13)
        for _ in range(300):
            vetor = [rng.randint(1, 50) for _ in range(rng.randint(1, 40))]
            esperado = (sum(vetor), 0, len(vetor) - 1)
            for nome, algoritmo in ALGORITMOS.items():
                with self.subTest(vetor=vetor, algoritmo=nome):
                    self.assertEqual(algoritmo(vetor), esperado)


class TestEntradaInvalida(unittest.TestCase):

    def test_vetor_vazio(self):
        for nome, algoritmo in ALGORITMOS.items():
            with self.subTest(algoritmo=nome):
                with self.assertRaises(ValueError):
                    algoritmo([])


class TestLinhaDeComando(unittest.TestCase):

    def rodar(self, entrada, *argumentos):
        return subprocess.run(
            [sys.executable, str(RAIZ / "etapa1.py"), *argumentos],
            input=entrada, capture_output=True, text=True, timeout=30,
        )

    def test_casos_do_arquivo_pela_linha_de_comando(self):
        for caso in ler_casos(ARQUIVO_CASOS):
            vetor = vetor_do_caso(caso)
            entrada = "{}\n{}\n".format(len(vetor), " ".join(map(str, vetor)))
            with self.subTest(caso=caso["caso"]):
                resultado = self.rodar(entrada)
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                self.assertEqual(resultado.stdout.strip(), caso["saida"])

    def test_entrada_em_uma_linha(self):
        resultado = self.rodar("9 -2 1 -3 4 -1 2 1 -5 4\n")
        self.assertEqual(resultado.stdout.strip(), "6 3 6")

    def test_entrada_em_varias_linhas(self):
        resultado = self.rodar("9\n-2 1 -3 4\n-1 2 1 -5 4\n")
        self.assertEqual(resultado.stdout.strip(), "6 3 6")

    def test_cada_algoritmo(self):
        for nome in ["dc", "forca-bruta", "kadane"]:
            with self.subTest(algoritmo=nome):
                resultado = self.rodar("9 -2 1 -3 4 -1 2 1 -5 4\n", "--algoritmo", nome)
                self.assertEqual(resultado.stdout.strip(), "6 3 6")

    def test_entrada_incompleta(self):
        resultado = self.rodar("5\n1 2\n")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("erro", resultado.stderr)


if __name__ == "__main__":
    unittest.main()