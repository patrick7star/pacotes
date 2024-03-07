

"""
   O mesmo que o módulo de 'banco de dados', porém tudo será gravado num
 arquivo JSON, sem falar que terá mais metadados importantes do que o
 anterior, como 'timestamp' do último download, números de downloads,
 e etc.
"""

"""
Templates:

  "linguagem de programação:" {

    "pacote_i": {
         "link": "http://...",
         "qtd de downloads": N,
         "último download": TimeStamp,
         "versão": vX.X.X
    },

    "pacote_ii": { ... mesma coisa acima ... },
                   .
                   .
                   .
 }
"""
# o que será exportado?
__all__ = ["cria_novo_repositorio_json"]

from gerenciador import (carrega, CORE_PYTHON)
from pathlib import Path
import json
from banco_de_dados import carregaUR

# caminho compatível tanto com Windows como o Linux.
CAMINHO_JSON_DATA = Path(CORE_PYTHON, "data/repositorios.json")

def cria_novo_repositorio_json() -> None:
   # carrega dicionário com dados a fazer o JSON, também verifica se ele
   # tem algum dado.
   dicionario_dados = carrega()
   assert len (dicionario_dados) > 0

   # adiciona último vez que foi feita uma atualização.
   dicionario_dados["última-atualização"] = carregaUR().timestamp()
   arquivo_json = open (CAMINHO_JSON_DATA, "wt", encoding="utf-8")
   json.dump (
      dicionario_dados, arquivo_json,
      indent='\t', sort_keys=True,
      ensure_ascii = False
   )
   arquivo_json.close()
   assert (CAMINHO_JSON_DATA.exists())

   if __debug__:
      with open (CAMINHO_JSON_DATA, "rt", encoding="utf8") as arquivo:
         obj_json = json.load (arquivo)
         print (obj_json)
      ...
   ...
...

import unittest
from os import remove

class Unitarios (unittest.TestCase):
	def antigo_dados_para_json (self):
		cria_novo_repositorio_json()
		remove (CAMINHO_JSON_DATA)
		assert (not CAMINHO_JSON_DATA.exists())
...
