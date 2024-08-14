"""
  Criação de linques para ambas plataformas onde isso é utilizado.
"""

# o que será exportado?
__all__ = ["cria_link_simbolico"]

from pathlib import PosixPath
from os import (getcwd, getenv, symlink, chdir)
import platform
from dados import PROG_DIR

# gera link simbólico se não houver algum.
def cria_link_simbolico_no_linux() -> None:
   NOME_SRC = "main.py"
   NOME_LINQUE = "pacotes"
   DIR_DO_LINK = getenv("LINK")
   executavel = PROG_DIR.joinpath("src", NOME_SRC)
   linque_pth = PosixPath(getenv("HOME"), ".local/usr/bin")
   
   if __debug__:
      print("arquivo script: '%s'" % executavel)

   if linque_pth.exists():
      base = linque_pth
   else:
      raise Exception("caminho não encontrado")
   link_caminho = base.joinpath(NOME_LINQUE)

   if (not link_caminho.exists()):
      if __debug__:
         print("atual diretório:", getcwd())
         print("criando link de '{}' em '{}'".format(executavel, base))
      ...
      symlink(executavel, link_caminho)
   else:
      raise FileExistsError("já existe um linque")

   # criando um também para a base do código do programa...
   link_caminho = PROG_DIR.joinpath(NOME_LINQUE)

   if (not link_caminho.exists()):
      symlink(executavel, link_caminho)
   else:
      raise FileExistsError("já existe um linque")
...

def cria_link_simbolico() -> bool:
   "Cria linque simbólicos, indepedente do sistema."
   sistema_operacional = platform.system()

   # Exibindo onde está fazendo.
   print(
      "Iniciando criação de linques simbólicos(no %s) ..."
      % sistema_operacional
   )

   if sistema_operacional == "Linux":
      COMECO_DIR = getenv("HOME")
      NOME_SRC = "main.py"
      NOME_LINQUE = "pacotes"
      second_linque = PosixPath(COMECO_DIR, ".local/usr/bin", "pacotes")
      third_linque = PROG_DIR.joinpath("pacotes")

      try:
         cria_link_simbolico_no_linux()
      except FileExistsError:
         return second_linque.exists() and third_linque.exists()
      # Manda sinal de confirmação da criação do linque.
      return True

   elif sistema_operacional == "Windows":
      print("sem criação de links(ainda) para Windows.")
      return False
...
