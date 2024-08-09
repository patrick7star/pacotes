"""
  Fica várias constantes, funções simples, bibliotecas externas que são 
importadas aquias e reexportadas, caminhos importantes(constantes), e várias
outras coisas que não exigem muito elaboração, e são usadas por vários 
módulos.
"""

from sys import path
from os import getenv
from pathlib import Path
import platform

__all__ = ["arvore", "GalhoTipo", "legivel", "CORE_PYTHON", "CORE_RUST"]

# Lincando biblioteca que estão na array de busca padrão:
caminho_lib =Path(getenv("PYTHON_CODES"),"pacotes", "lib") 
path.append(str(caminho_lib))
# Importando lib externas ao programa:
import legivel
from arvore_ii import (arvore, GalhoTipo)

if platform.system() == "Windows":
   # caso seja um sistema Windows ...
   CORE_PYTHON = Path(getenv("PythonCodes"))
   CORE_RUST = Path(getenv("RustCodes"))

elif platform.system() == "Linux":
   # caso seja uma sistema Linux ...
   CORE_PYTHON = Path(getenv("PYTHON_CODES"))
   CORE_RUST = Path(getenv("RUST_CODES"))
...

# Como é um alternativo ao existente, mudamos temporiariamente o 
# redirecionamento de gravura/leitura.
CORE = "pacotes/data"
# Nome do arquivo contendo última registro.
#ULTIMO_REGISTRO = Join(RAIZ, CORE, "ultima_busca.dat")
ULTIMO_REGISTRO = Path(CORE_PYTHON, CORE, "ultima_busca.dat")

