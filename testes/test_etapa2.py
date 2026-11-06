import math
import random
import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from etapa2 import distancia, divisao_e_conquista, forca_bruta

ALGORITMOS = {
    "forca_bruta": forca_bruta,
    "divisao_e_conquista": divisao_e_conquista,
}
ARQUIVO_CASOS = Path(__file__).resolve().parent / "casos_etapa2.txt"
TOLERANCIA = 1e-6


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


def pontos_do_caso(caso):
    numeros = [float(x) for x in caso["entrada"].split()]
    n, coordenadas = int(numeros[0]), numeros[1:]
    if len(coordenadas) != 2 * n:
        raise ValueError("caso '{}': n = {}, mas há {} coordenadas".format(
            caso["caso"], n, len(coordenadas)))
    return [(coordenadas[2 * i], coordenadas[2 * i + 1]) for i in range(n)]


def par_do_caso(caso):
    if "par" not in caso:
        return None
    v = [float(x) for x in caso["par"].split()]
    return ((v[0], v[1]), (v[2], v[3]))


class VerificacoesDeResposta(unittest.TestCase):

    def conferir_resposta(self, pontos, resposta, distancia_esperada):
        d, (p, q) = resposta
        self.assertTrue(math.isclose(d, distancia_esperada, rel_tol=1e-9, abs_tol=1e-9),
                        "distância {} diferente de {}".format(d, distancia_esperada))
        self.assertTrue(math.isclose(distancia(p, q), d, rel_tol=1e-9, abs_tol=1e-9))
        restantes = list(pontos)
        restantes.remove(p)
        self.assertIn(q, restantes)


class TestCasosDeBorda(VerificacoesDeResposta):

    def test_arquivo_tem_casos(self):
        self.assertGreater(len(ler_casos(ARQUIVO_CASOS)), 0)

    def test_casos_do_arquivo(self):
        for caso in ler_casos(ARQUIVO_CASOS):
            pontos = pontos_do_caso(caso)
            esperado = float(caso["distancia"])
            par_esperado = par_do_caso(caso)
            for nome, algoritmo in ALGORITMOS.items():
                with self.subTest(caso=caso["caso"], algoritmo=nome):
                    d, par = algoritmo(pontos)
                    self.assertLess(abs(d - esperado), TOLERANCIA)
                    self.conferir_resposta(pontos, (d, par), d)
                    if par_esperado is not None:
                        self.assertEqual(tuple(sorted(par)), par_esperado)


class TestDiferencial(VerificacoesDeResposta):

    def comparar(self, semente, quantidade, tamanho_max, gerar_coordenada, limiares=(3,)):
        rng = random.Random(semente)
        for _ in range(quantidade):
            n = rng.randint(2, tamanho_max)
            pontos = [(gerar_coordenada(rng), gerar_coordenada(rng)) for _ in range(n)]
            esperado, _ = forca_bruta(pontos)
            for limiar in limiares:
                with self.subTest(pontos=pontos, limiar=limiar):
                    resposta = divisao_e_conquista(pontos, limiar=limiar)
                    self.conferir_resposta(pontos, resposta, esperado)

    def test_grade_pequena_com_duplicados_e_empates(self):
        self.comparar(semente=2026, quantidade=2000, tamanho_max=40,
                      gerar_coordenada=lambda rng: rng.randint(0, 10))

    def test_coordenadas_reais(self):
        self.comparar(semente=7, quantidade=300, tamanho_max=200,
                      gerar_coordenada=lambda rng: rng.uniform(-1000, 1000))

    def test_varios_limiares(self):
        self.comparar(semente=11, quantidade=500, tamanho_max=60,
                      gerar_coordenada=lambda rng: rng.randint(-20, 20),
                      limiares=(1, 2, 3, 4, 8, 16, 64))

    def test_todos_no_mesmo_x(self):
        self.comparar(semente=13, quantidade=300, tamanho_max=50,
                      gerar_coordenada=lambda rng: rng.choice([0, rng.randint(0, 100)]))


class TestEntradaInvalida(unittest.TestCase):

    def test_menos_de_dois_pontos(self):
        for nome, algoritmo in ALGORITMOS.items():
            for pontos in ([], [(1.0, 1.0)]):
                with self.subTest(algoritmo=nome, pontos=pontos):
                    with self.assertRaises(ValueError):
                        algoritmo(pontos)

    def test_limiar_invalido(self):
        with self.assertRaises(ValueError):
            divisao_e_conquista([(0.0, 0.0), (1.0, 1.0)], limiar=0)


class TestLinhaDeComando(unittest.TestCase):

    def rodar(self, entrada, *argumentos):
        return subprocess.run(
            [sys.executable, str(RAIZ / "etapa2.py"), *argumentos],
            input=entrada, capture_output=True, text=True, timeout=30,
        )

    def test_casos_do_arquivo_pela_linha_de_comando(self):
        for caso in ler_casos(ARQUIVO_CASOS):
            numeros = caso["entrada"].split()
            entrada = numeros[0] + "\n" + "\n".join(
                " ".join(numeros[1 + 2 * i:3 + 2 * i]) for i in range(int(numeros[0]))) + "\n"
            with self.subTest(caso=caso["caso"]):
                resultado = self.rodar(entrada)
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                saida = resultado.stdout.split()
                self.assertEqual(saida[0], caso["distancia"])
                if "par" in caso:
                    self.assertEqual(" ".join(saida[1:]), caso["par"])

    def test_entrada_em_uma_linha(self):
        resultado = self.rodar("3 0 0 3 4 10 10\n")
        self.assertEqual(resultado.stdout.strip(), "5.000000 0 0 3 4")

    def test_forca_bruta_pela_linha_de_comando(self):
        resultado = self.rodar("3 0 0 3 4 10 10\n", "--algoritmo", "forca-bruta")
        self.assertEqual(resultado.stdout.strip(), "5.000000 0 0 3 4")

    def test_entrada_incompleta(self):
        resultado = self.rodar("3\n0 0\n3 4\n")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("erro", resultado.stderr)

    def test_um_ponto_so(self):
        resultado = self.rodar("1\n5 5\n")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("erro", resultado.stderr)


if __name__ == "__main__":
    unittest.main()