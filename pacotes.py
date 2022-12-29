#!/usr/bin/python3 -O
"""
Programa em sí que baixa os pacotes
e arruma no atual diretório. Também
é possível selecionar o arquivo
específico a extrair.
"""

# deste programa:
from gerenciador import carrega, mapa, listagem, carrega_rust
from obtencao import baixa

# biblioteca externa:
from python_utilitarios.utilitarios import arvore
GalhoTipo = arvore.GalhoTipo
arvore = arvore.arvore

# biblioteca padrão do Python:
from sys import argv
from shutil import move
from time import sleep
from os.path import basename, exists, join, isdir
from shutil import rmtree
from os import chmod, getenv
from stat import S_IRWXU, S_IXGRP, S_IXOTH
from tempfile import gettempdir

# colocando permisões:
try:
   chmod("pacotes.py", S_IRWXU | S_IXGRP | S_IXOTH)
except FileNotFoundError:
   caminho = join(
      getenv("PYTHON_CODES"),
      "pacotes", "pacotes.py"
   )
   chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)
...

# listando os pacotes ...
if __debug__:
   print("argumentos passados:", argv, end="\n\n")

# ativa versão para o Rust packages
# caso seja pedido.
versao_rust = False
if "--rust" in argv:
   indice = argv.index("--rust")
   argv.pop(indice)
   versao_rust = True
   assert versao_rust
   print("versão Rust acionada.")
   del carrega
else:
   assert not versao_rust
   if __debug__:
      print("versão Python acionada.")
...

if len(argv) == 1:
   if not versao_rust:
      listagem()
   else:
      carrega_rust()
else:
   if versao_rust:
      if __debug__:
         print("foi acionado?")
      carrega_rust()
   else:
      carrega()

   for arg in argv[1:]:
      caminho = baixa(arg, mapa)
      estrutura = arvore(caminho, True, GalhoTipo.FINO)

      # remove o diretório/arquivo se existente.
      nome_dir = basename(caminho)

      # importante para o manuseio dos pacotes Rust:
      foi_movido = False
      # dentro do diretório do código-fonte.
      artefatos = join(nome_dir, "target")
      artefatoTemp = join(gettempdir(), "target")

      if exists(nome_dir):
         artefato_existe = isdir(artefatos) and exists(artefatos)
         # se for o Rust, verificar se 
         # diretório com artefatos está lá,
         # já que será mantido.
         if versao_rust and artefato_existe:
            assert (not exists(artefatoTemp))
            move(artefatos, gettempdir())
            assert exists(artefatoTemp)
            print("movido para a pasta temporária.")
            foi_movido = True
         ...
         rmtree(nome_dir, ignore_errors=True)
         print("'{}' removido.".format(nome_dir))
      ...

      move(caminho, ".")
      if foi_movido:
         assert (not exists(artefatos))
         print("movendo de volta!")
         move(artefatoTemp, nome_dir)
         assert exists(artefatos)
      ...
      print(
         "{}\n\"{}\" foi baixado com sucesso."
         .format(estrutura, arg),
         end="\n\n"
      )
   ...
...

import platform
# pausa para ver os output por alguns segundos.
if platform.system() == "Windows":
   sleep(5.5)
