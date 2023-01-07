

"""
Baixa o os pacotes no arquivo 'links.txt'. No
futuro ele baixará tal arquivo, comparará com
atual diretório e substituirá pelo novo.
"""

# bibliotecas padrão do Python:
from array import array
from os import getenv
from os.path import join
import platform

# computando repositório de primeira.
if platform.system() == "Windows":
   CORE_PYTHON = getenv("PythonCodes")
   CORE_RUST = getenv("RustCodes")
elif platform.system() == "Linux":
   CORE_PYTHON = getenv("PYTHON_CODES")
   CORE_RUST = getenv("RUST_CODES")
...

# Arquivos contendo links anexados dos pacotes.
LINK_PYTHON = join(CORE_PYTHON, "links.txt")
LINK_RUST = join(CORE_RUST, "links.txt")

# adicionando método na "array de valores".
class Array(array):
   def empty(self):
      return len(self) == 0
...

# verifica se todos os cabeçalhos estão
# corretamente fechados ...
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

# apelidos para melhorar a codificação:
MiniMapa = {str: str}
Mapa = {str: MiniMapa, str: MiniMapa}

# filtra o cabeçalho e seus respectivos conteúdos.
def filtra(string) -> MiniMapa:
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

# primeiro estágio do carregamento dos
# links dados no programa. Formar um
# grande dicionário, contendo os links
# de demais de ambos.
def carrega() -> Mapa:
   # mapa conteudo conteúdos.
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

# lista a linguagem exigida, seja ela
# Python ou Rust.
def listagem(mapa: Mapa, tipo: str) -> None:
   if tipo.lower() not in ("python", "rust"):
      raise Exception("não implementada para tal opção")
   print("\nDisponíveis:")
   for chave in mapa[tipo.lower()].keys():
      print("\t\b\b\b{}".format(chave))
   print('')
...

# listagem com informações completas, usando-se
# do banco de dados para obter versão, e última
# mudança feita.
def listagemI(mapa: Mapa, linguagem: str) -> None:
   from banco_de_dados import le_pacote_registro
   from datetime import datetime
   from python_utilitarios.utilitarios import legivel
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
   del le_pacote_registro, datetime, legivel
   print('')
...


from unittest import TestCase, main

class Funcoes(TestCase):
   def conteudoDosLinks(self):
      from pprint import pprint
      for atual in [LINK_RUST, LINK_PYTHON]:
         a = open(atual, "rt", encoding="utf8")
         conteudo = a.read()
         a.close()
         pprint(conteudo)
         conteudo = filtra(conteudo)
         pprint(conteudo)
      ...
      del pprint
   ...
   def carregamentoDoMapa(self):
      m = carrega()
      self.assertEqual(len(m), 2)
      self.assertTrue("python" in m.keys())
      self.assertTrue("rust" in m.keys())
      pprint(m)
      self.assertTrue(len(m["python"]) > 3)
      self.assertTrue(len(m["rust"]) > 3)
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

# o que será importado.
__all__ = [
   "carrega", "listagem",
   "CORE_RUST", "CORE_PYTHON",
   "Mapa", "listagemI"
]

if __name__ == "__main__":
   main()
