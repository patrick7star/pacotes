

"""
Baixa o os pacotes no arquivo 'links.txt'. No
futuro ele baixará tal arquivo, comparará com
atual diretório e substituirá pelo novo.
"""

# bibliotecas padrão do Python:
from array import array
from os import system, getenv, remove, rename, popen
from os.path import join, basename, normcase, normpath
from zipfile import ZipFile
import subprocess
from subprocess import run as Run
from shutil import move
from copy import copy
import platform

# computando repositório de primeira.
if platform.system() == "Windows":
   core = getenv("PythonCodes")
   core_i = getenv("RustCodes")
elif platform.system() == "Linux":
   core = getenv("PYTHON_CODES")
   core_i = getenv("RUST_CODES")
...

LINKS = join(core, "links.txt")
LINKS_RUST = join(core_i, "links.txt")

# adicionando método na "array de valores".
class Array(array):
   def empty(self):
      return len(self) == 0
...

# guarda cabeçalhos e seus respectivos
# links anexados.
mapa = {}

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

# filtra o cabeçalho e seus respectivos conteúdos.
def filtra(string):
   if not esta_fechado(string):
      raise Exception("erro na sintaxe do arquivo!")

   aglomerador = False
   primeiro_acionado = False
   cabecalho = []
   conteudo = []
   ultima_chave = None
   comecou_comentario = False

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
...

# carrega devidos 'cabeçalhos' e seus possíveis
# respectivos conteúdos(links dos dados). Retonra
# um valor lógico dizendo se a tarefa de ser
# carregado foi um sucesso ou não.
def carrega():
   if len(mapa) > 0:
      return False

   caminho = normpath(LINKS)

   with open(caminho, "rt", encoding="utf8") as arquivo:
      filtra(arquivo.read())

   # veficando 'cabeçalhos'.
   for chave in mapa.keys():
      if mapa.get(chave) == []:
         print("'{}' não têm qualquer link.")
         print("então deletando-o ...", end=" ")
         del mapa[chave]
         assert chave not in mapa
         print("feito.")
      ...
   ...
   return True
...

def carrega_rust():
   if __debug__:
      print("foi acionado?")
   with open(LINKS_RUST, "rt", encoding="utf8") as arquivo:
      if __debug__:
         conteudo = arquivo.read()
         print(conteudo)
         filtra(conteudo)
      else:
         filtra(arquivo.read())
   ...
   # aplicando versão também.
   from versoes import completa_mapa
   novo_mapa = completa_mapa(mapa)
   del completa_mapa

   # veficando 'cabeçalhos'.
   print("\nDISPONÍVEIS(Rust):")
   for chave in list(mapa.keys()):
      if mapa[chave] == "":
         print("'%s' não têm qualquer link." % chave)
         print("então deletando-o ...", end=" ")
         del mapa[chave]
         assert chave not in mapa
         print("feito.")
      else:
         versao = novo_mapa[chave][1]
         print("\t\b\b\b%s(v%s)" % (chave, versao))
      ...
   ...
   print("")
...

def listagem():
   if not carrega():
      print("já foi carregado.")
   assert len(mapa.keys()) > 0

   print("\nDisponíveis:\n".upper())
   for chave in mapa.keys():
      print(
         "{espaco:>4s}{}\t{}"
         .format(
            chave, "~ tempo",
            end="\n\n",
            espaco = ' '
         )
      )
   ...
   print("\n")
...

__all__ = [
   "listagem", "carrega",
   "core" "mapa",
   "carrega_rust"
]

if __name__ == "__main__":
   from python_utilitarios.utilitarios import testes

   # executa os testes em sí.
   testes.executa_teste(listagem)
...
