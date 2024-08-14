"""
  Baixa o os pacotes no arquivo 'links.txt'. No futuro ele baixará tal 
arquivo, comparará com atual diretório e substituirá pelo novo.
"""

# bibliotecas padrão do Python:
from array import array as FixedArray
from os.path import join
from pathlib import Path
from unittest import TestCase, main
from dados import CORE_PYTHON, CORE_RUST, PROG_DIR

# o que será importado.
__all__ = ["carrega", "listagem", "Mapa", "listagemI"]

# Arquivos contendo links anexados dos pacotes.
BASE_RPT = PROG_DIR.joinpath("data", "repositorios")
LINK_PYTHON = BASE_RPT.joinpath("links_python.txt")
LINK_RUST = BASE_RPT.joinpath("links_rust.txt")

# apelidos para melhorar a codificação:
MiniMapa = {str: str}
Mapa = {str: MiniMapa, str: MiniMapa}

# adicionando método na "array de valores".
class Array(FixedArray):
   def empty(self):
      return len(self) == 0
...

# verifica se todos os cabeçalhos estão corretamente fechados ...
def esta_fechado(string):
   aberto = "[({"
   fechado = "])}"

   # array apresentada com pilha.
   pilha = Array('u',[])

   for char in string:
      if char in aberto:
         pilha.append(char)
      elif char in fechado:
         if pilha.empty():
            return False
         remocao =  pilha.pop()
         (i1, i2) = (aberto.find(char), fechado.find(remocao))
         if i1 != i2:
            return False
      ...
   ...
   return pilha.empty()
...

def filtra(string) -> MiniMapa:
   "Filtra o cabeçalho e seus respectivos conteúdos."
   if not esta_fechado(string):
      raise Exception("erro na sintaxe do arquivo!")

   aglomerador = False
   primeiro_acionado = False
   cabecalho = []
   conteudo = []
   ultima_chave = None
   comecou_comentario = False
   # dicionário inicialmente vázio.
   mapa = {}

   for (i, char) in enumerate(string):
      if char == '#':
         comecou_comentario = True
      # ignora quebra de linhas e partes de comentários.
      if char == '\n':
         comecou_comentario = False
         continue
      elif comecou_comentario:
         continue

      if aglomerador:
         cabecalho.append(char)
      else:
         if primeiro_acionado:
            conteudo.append(char)
      ...

      if char == '[':
         aglomerador = True
         # permite a aglomeração de conteúdo.
         primeiro_acionado = True
         if ultima_chave is not None:
            # remove 'fecha-colchetes'.
            conteudo.pop()
            mapa[ultima_chave] = "".join(conteudo)
            conteudo.clear()
         ...
      elif char == ']':
         aglomerador = False
         chave = ''.join(cabecalho[0:-1])
         cabecalho.clear()
         mapa[chave] = []
         ultima_chave = chave
      ...
   ...

   if len(conteudo) > 0:
      mapa[ultima_chave] = "".join(conteudo)
   return mapa
...

def carrega() -> Mapa:
   """
    primeiro estágio do carregamento dos links dados no programa. Formar um
    grande dicionário, contendo os links de demais de ambos.
   """
   mapa = {"rust": None, "python": None}
   arq = open(LINK_RUST, "rt", encoding="utf8")
   # primeiro do Rust...
   conteudo = arq.read()
   arq.close()
   mapa["rust"] = filtra(conteudo)
   # ... agora do Python.
   arq = open(LINK_PYTHON, "rt", encoding="utf8")
   conteudo = arq.read()
   arq.close()
   mapa["python"] = filtra(conteudo)
   return mapa
...

def listagem(mapa: Mapa, tipo: str) -> None:
   "lista a linguagem exigida, seja ela Python ou Rust"
   if tipo.lower() not in ("python", "rust"):
      raise Exception("não implementada para tal opção")
   print("\nDisponíveis:")
   for chave in mapa[tipo.lower()].keys():
      print("\t\b\b\b{}".format(chave))
   print('')
...

def listagemI(mapa: Mapa, linguagem: str) -> None:
   """
   Listagem com informações completas, usando-se do banco de dados para 
   obter versão, e última mudança feita.
   """
   from banco_de_dados import le_pacote_registro
   from datetime import datetime
   #from python_utilitarios.utilitarios import legivel
   from dados import legivel

   linguagem = linguagem.lower()
   if linguagem not in ("python", "rust"):
      raise Exception("não implementada para tal opção")

   print("\nDisponíveis:", end="\n\n")

   for chave in mapa[linguagem].keys():
      dados = le_pacote_registro(linguagem, chave)
      if dados is not None:
         cabecalho = dados[0]
         versao = dados[2]
         t = (datetime.today() - dados[3]).total_seconds()
         if linguagem == "python":
            print(
               "\t\b\b\b{:<27s} ~{:<15}"
               .format(chave, legivel.tempo(t))
            )
         elif linguagem == "rust":
            print(
               "\t\b\b\b{:<22s} v{:<9} ~{:<15}"
               .format(chave, versao, legivel.tempo(t))
            )
         else:
            raise Exception("não implementada para tal opção")
      else:
         print("\t\b\b\b{}".format(chave))
   ...
   # quebra-de-linha.
   print('')
   # não é preciso mais, então morre neste escopo.
   del le_pacote_registro, datetime, legivel
...

class Funcoes(TestCase):
   def setUpClass():
      import os
      caminho = Path(".")
      if caminho.name != 'src':
         print("Precisa entrar no diretório 'src'.")
         os.chdir("src")
         assert Path().name == "src"
      del os
   ...

   def conteudoDosLinks(self):
      from pprint import pprint

      print(
         "cores: \n\t'{}'\n\t'{}"
         .format(CORE_PYTHON, CORE_RUST)
      )
      for atual in [LINK_RUST, LINK_PYTHON]:
         print("caminho final: {atual}".format(atual=atual))
         with open(atual, "rt", encoding="utf8") as a:
            conteudo = a.read()

         print("\nantes da filtragem:")
         pprint(conteudo)
         conteudo_dicio = filtra(conteudo)
         print("\ndepois da filtragem:")
         pprint(conteudo_dicio)
      ...
      del pprint
   ...
   def carregamentoDoMapa(self):
      from pprint import pprint
      m = carrega()

      self.assertEqual(len(m), 2)
      self.assertTrue("python" in m.keys())
      self.assertTrue("rust" in m.keys())

      pprint(m)

      self.assertTrue(len(m["python"]) > 3)
      self.assertTrue(len(m["rust"]) > 3)
      del pprint
   ...
   def Listagem(self):
      mapa = carrega()
      listagem(mapa, "rust")
      listagem(mapa, "python")
   ...
   def ListagemDetalhada(self):
      from os.path import exists
      from banco_de_dados import CONDENSADO
      M = carrega()

      listagemI(M, "python")
      listagemI(M, "rust")

      self.assertTrue(exists(CONDENSADO))
      del exists, CONDENSADO
   ...
...
