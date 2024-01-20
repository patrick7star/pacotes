#!/usr/bin/python3 -O
"""
Programa em sí que baixa os pacotes
e arruma no atual diretório. Também
é possível selecionar o arquivo
específico a extrair.
"""

# deste programa:
#from gerenciador import carrega, mapa, listagem, carrega_rust
#from obtencao import baixa
from gerenciador import (
   carrega, listagem,
   listagemI, CORE_PYTHON
)
from banco_de_dados import (atualiza_bd, grava_pacote_registro)
from obtencao import baixa_e_metadados as baixa

# biblioteca externa:
from python_utilitarios.utilitarios import arvore
GalhoTipo = arvore.GalhoTipo
arvore = arvore.arvore

# biblioteca padrão do Python:
from sys import argv
from os.path import (isdir, abspath, basename, exists, join)
from shutil import (rmtree, move)
from os import chmod
from stat import (S_IRWXU, S_IXGRP, S_IXOTH)
from argparse import (ArgumentParser, SUPPRESS)

# colocando permisões:
try:
   chmod("pacotes.py", S_IRWXU | S_IXGRP | S_IXOTH)
except FileNotFoundError:
   caminho = join(CORE_PYTHON, "pacotes/pacotes.py")
   chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)
...

import platform
# gera link simbólico se não houver algum.
def cria_link_simbolico():
   from pathlib import PosixPath
   from os import (getcwd,getenv, symlink,chdir)

   arquivo_execucao = PosixPath(CORE_PYTHON, "pacotes/pacotes.py")
   caminhoI = PosixPath(getenv("HOME"), ".local/usr/sbin")
   caminhoII = PosixPath(getenv("HOME"), ".local/usr/bin")
   inicial = getcwd()

   if caminhoI.exists():
      if __debug__:
         print("atual diretório:", getcwd())
      chdir(caminhoI)
      atual = caminhoI
      if __debug__:
         print("atual diretório:", getcwd())
   elif caminhoII:
      if __debug__:
         print("atual diretório:", getcwd())
      chdir(caminhoII)
      atual = caminhoII
      if __debug__:
         print("atual diretório:", getcwd())
   else:
      raise Exception("caminho não encontrado")
   if __debug__:
      print("criando link até {} de '{}'".format(arquivo_execucao, atual))
   else:
      link_caminho = PosixPath("pacotes")
      if (not link_caminho.is_symlink()):
         if __debug__:
            print("atual diretório:", getcwd())
         symlink(arquivo_execucao, "pacotes")
         assert link_caminho.is_symlink()
         print("link criado!")
      else:
         print("link já existe!")
   ...
   chdir(inicial)
   if __debug__:
      print("atual diretório:", getcwd())
...

menu = ArgumentParser(
   description = """
   baixa pacotes Python ou Rust, diretos do GitHub,
   extraindo-os, e até substituindo os mesmos se já
   houver diretórios e arquivos com o mesmo nome no
   diretório da operação.
   """,
   prog = "Pacotes",
   epilog = """Por uma questão de... preguiça, fiz
   tal programa que tem como objetivo facilitar
   o downlaod da mais atual versão do código, que
   sempre que terminado é subido para o GitHub. Ao
   invés de ficar entre pelo site, e indo diretamente
   no pacote toda vez, este pega tal, faz download
   e descompacta o mesmo, se no diretório onde já têm
   um, substituindo pelo mais novo.
    O modo como faz isso é seguir o link de um
   arquivo 'txt', que fica no diretório principal
   dos códigos de cada linguagem, sem tal, é impossível
   baixar tais, sequer listar-lôs.""",
   usage="%(prog)s [OPÇÃO] <NOME_DO_PKG>"
)

if __debug__:
   menu.print_help()

# conteúdo dos arquivos 'txt' com cabeçalhos/links.
grade = carrega()

# adicionando também versões minúsculas/maiúsculas
# para que se possa digitar de qualquer ordem.
def expansao(l) -> list:
   q = len(l)
   while q > 0:
      remocao = l.pop(0)
      if remocao.lower() in "python-rust":
         l.append(remocao.capitalize())
      else:
         minuscula = remocao.lower()
         maiusculas = remocao.upper()
         l.append(minuscula)
         l.append(maiusculas)
      ...
      l.append(remocao)
      q -= 1
   ...
   return l
...

menu.add_argument(
   "--lista", type=str,
   help="lista os pacotes disponíveis em cada linguagem.",
   metavar="LANG", nargs=1, default=None,
   choices = expansao(["python", "rust"]),
)

# todos argumentos permitidos.
permicoes = list(grade["python"].keys())
permicoes.extend(list(grade["rust"].keys()))
permicoes.extend(["python", "rust"])
permicoes = expansao(permicoes)

menu.add_argument(
   "--obtem", type=str,
   help="""
   baixa um dos pacotes listados no atual diretório. Se
   não houver tal opção, então um erro será emitido. O
   primeiro argumento é a linguagem desejada, e o segundo
   é o pacote desejado.""",
   default=None, nargs=2, metavar=("LANG", "PKG"),
   choices = permicoes
)
menu.add_argument(
   "--atualiza", action="store_true",
   help = """atualiza todas versões/e
   última alteração dos pacotes.""",
)
argumentos = menu.parse_args()

if __debug__:
   print(argumentos)
   print(argumentos.lista)
...

# trabalha específico com o movimento do
# conteúdo descompactado para o atual
# diretório. Isto é preciso já que ele
# poder ter um diretório com o mesmo nome,
# que então deverá ser substituído, porém
# com cuidado, já que, pode conter artefatos
# anteriormente compilados que devem ser
# mantidos.
def move_diretorio_rust(caminho, destino) -> None:
   # closure que verifica se ambos
   # diretórios dados são Rust.
   eUmDirRust = (
      lambda caminho:
         # existe tal caminho, é um diretório
         # e têm um arquivo Toml do cargo para
         # deixar claro que está trabalhando
         # com um diretório Rust.
         exists(caminho) and
         isdir(caminho) and
         exists(join(caminho, "Cargo.toml"))
   )
   # diretório com mesmo nome no atual.
   mesmo_dir = basename(caminho)
   # condição para deslocamento cuidadoso.
   if eUmDirRust(mesmo_dir) and eUmDirRust(caminho):
      # pasta com testes, debugs e otimizados compilados.
      artefatos = join(mesmo_dir, "target")
      artefato_existente = exists(artefatos)
      if artefato_existente:
         print("movendo 'target' para '{}'...".format(caminho))
         move(artefatos, caminho)
   else:
      print("o pacote neste dir não tem 'artefatos'.")
   if eUmDirRust(mesmo_dir):
      print("removendo '{}'...".format(mesmo_dir))
      rmtree(mesmo_dir, ignore_errors=True)
   print("movendo '{}' para '{}'".format(caminho, abspath(".")))
   move(caminho, ".")
...

# mesmo acima, porém que para o Python.
# Por ser geralmente ignorada o diretório
# com artefatos, porque também seria bem
# mais difícil a implementação, o código
# é bem mais simples.
def move_diretorio_python(caminho, destino) -> None:
   mesmo_dir = basename(caminho)
   if exists(mesmo_dir):
      print("excluíndo '{}'...".format(abspath(mesmo_dir)), end=' ')
      rmtree(mesmo_dir)
      print("feito.")
      assert notexists(mesmo_dir)
   ...
   print("movendo '{}' para '{}'".format(caminho, abspath(".")))
   move(caminho, ".")
...

sistema_operacional = platform.platform()
if sistema_operacional == "Linux":
   cria_link_simbolico()
elif sistema_operacional == "Windows":
   print("sem criação de links(ainda) para Windows.")
   
# disparando o menu:
if argumentos.lista is not None:
   linguagem = argumentos.lista[0]
   listagemI(grade, linguagem)
elif argumentos.obtem is not None:
   # organizando argumentos da linha-de-comando.
   cabecalho = argumentos.obtem[1]
   linguagem = argumentos.obtem[0]
   if __debug__:
      print(
         "\n{barra}\nbaixando ... '{}' do {}\n{barra}\n"
         .format(
            cabecalho,
            linguagem.upper(),
            barra='*' * 50
         )
      )
   else:
      # carrega "mapa completo".
      mapa = carrega()
      # o mapa específico da linguagem.
      minimapa = mapa[linguagem.lower()]
      # baixa o download, e recebe tanto o
      # caminho com o conteúdo, como seus
      # metadados importantes.
      (caminho, tempo, versao) = baixa(cabecalho, minimapa)
      estrutura = arvore(caminho, True, GalhoTipo.FINO)
      link = minimapa[cabecalho]
      # gravando metadados no banco de dados...
      grava_pacote_registro(
         linguagem.lower(),
         cabecalho, link,
         versao, tempo
      )
      if linguagem.lower() == "rust":
         move_diretorio_rust(caminho, ".")
      elif linguagem.lower() == "python":
         move_diretorio_python(caminho, ".")
      else:
         raise Exception("não implementado para tal linguagem!")
      # info da estrutura do pacote baixado.
      print(
         "{}\n\"{}\" foi baixado com sucesso."
         .format(estrutura, cabecalho),
         end="\n\n"
      )
   ...
elif argumentos.atualiza:
   if __debug__:
      print("atualizando todo BD...")
   else:
      mapa = carrega()
      #atualiza_bd(mapa)
      print("atualiza foi realizada!")
   ...
else:
   print("nenhuma opção acionada!")


PAUSA = 5.4
import platform
from time import (sleep, time)
# pausa para ver resultado por alguns segundos.
if platform.system() == "Windows":
   ti = time()
   atual = time() - ti
   while atual < PAUSA:
      print("\rfechará em {:0.1f}seg".format(atual), end='')
      sleep(0.1)
      atual = time() - ti
   ...
...
