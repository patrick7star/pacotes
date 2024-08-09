"""
  Criação de linques para ambas plataformas onde isso é utilizado.
"""

# o que será exportado?
__all__ = ["cria_link_simbolico"]

#from gerenciador import CORE_PYTHON
from pathlib import PosixPath
from os import (getcwd, getenv, symlink, chdir)
import platform
from dados import CORE_PYTHON

# gera link simbólico se não houver algum.
def cria_link_simbolico_no_linux() -> None:
   NOME_SRC = "main.py"
   NOME_LINQUE = "pacotes"
   executavel = PosixPath(CORE_PYTHON, "pacotes/src", NOME_SRC)
   first_pth = PosixPath(getenv("HOME"), ".local/usr/sbin")
   second_pth = PosixPath(getenv("HOME"), ".local/usr/bin")
   
   if __debug__:
      print("arquivo script: '%s'" % executavel)

   if first_pth.exists():
      base = PosixPath(first_pth)
   elif second_pth.exists():
      base = PosixPath(second_pth)
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
   link_caminho = PosixPath("..").joinpath(NOME_LINQUE)
   if (not link_caminho.exists()):
      symlink(executavel, link_caminho)
   else:
      raise FileExistsError("já existe um linque")
...

def cria_link_simbolico() -> bool:
   "Cria linque simbólicos, indepedente do sistema."
   sistema_operacional = platform.system()

   print("Iniciando criação de linques simbólicos ...")
   print ("Sistema Operacional atual: '%s'" % sistema_operacional)

   if sistema_operacional == "Linux":
      COMECO_DIR = getenv("HOME")
      NOME_SRC = "main.py"
      NOME_LINQUE = "pacotes"
      first_linque = PosixPath(COMECO_DIR, ".local/usr/sbin", "pacotes")
      second_linque = PosixPath(COMECO_DIR, ".local/usr/bin", "pacotes")
      third_linque = CORE_PYTHON.joinpath("pacotes", "pacotes")

      try:
         cria_link_simbolico_no_linux()
      except FileExistsError:
         return ((first_linque or second_linque) and third_linque)
      # Manda sinal de confirmação da criação do linque.
      return True

   elif sistema_operacional == "Windows":
      print("sem criação de links(ainda) para Windows.")
      return False
...
