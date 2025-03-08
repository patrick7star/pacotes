"""
  Fica várias constantes, funções simples, bibliotecas externas que são 
importadas aquias e reexportadas, caminhos importantes(constantes), e várias
outras coisas que não exigem muito elaboração, e são usadas por vários 
módulos.
"""

from sys import path, argv
from os import getenv, readlink
from pathlib import Path
import platform

__all__ = ["arvore", "GalhoTipo", "legivel", "CORE_PYTHON", "CORE_RUST",
   "PACOTES_DIR", "PROG_DIR"
]

def computa_caminho_do_programa() -> Path:
   "Retorna o caminho do diretório que contém este programa."
   linha_de_execucao = Path(argv[0]).resolve()

   # Volta dois diretórios.
   componentes_path = linha_de_execucao.parents
   # Pegando o que exclui o 'script file' e o subdiretório que o contém.
   avo = componentes_path[1]
   return avo
...

if platform.system() == "Windows":
   # caso seja um sistema Windows ...
   CORE_PYTHON = Path(getenv("PythonCodes"))
   CORE_RUST = Path(getenv("RustCodes"))

elif platform.system() == "Linux":
   # caso seja uma sistema Linux ...
   CORE_PYTHON = Path(getenv("PYTHON_CODES"))
   CORE_RUST = Path(getenv("RUST_CODES"))
...

# Diretório com o código-fonte deste programa.
PACOTES_DIR = Path(CORE_PYTHON, "pacotes")
PROG_DIR = computa_caminho_do_programa()

# Lincando biblioteca que estão na array de busca padrão:
#caminho_lib = Path(CORE_PYTHON, "pacotes", "lib") 
caminho_lib = PROG_DIR.joinpath("lib")
caminho_lib_str = str(caminho_lib)
#path.append(str(caminho_lib))
path.append(caminho_lib_str)
# Importando lib externas ao programa:
import legivel
from arvore import (arvore, GalhoTipo)

# Como é um alternativo ao existente, mudamos temporiariamente o 
# redirecionamento de gravura/leitura.
CORE = "pacotes/data"
# Nome do arquivo contendo última registro.
ULTIMO_REGISTRO = PROG_DIR.joinpath(CORE, "ultima_busca.dat")


''' === === === === === === === === === === === === === === === === === ==
                           Verificação
 === === === === === === === === === === === === === === === === === == '''
from unittest import TestCase

class Features(TestCase):
   def pegar_a_raiz_deste_pacote(self):
      import sys
      print("caminho(teste):", sys.executable)
      print("caminho(teste):", sys.argv[0])
      print("caminho atual:", PACOTES_DIR)
   ...
...
