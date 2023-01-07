"""
A parte que baixa o arquivo e descompacta-o,
como também move o produto de tais operações
serão colocadas aqui, por motivos de 
organização(mirando a legibilidade).
"""

# biblioteca padrão do Python:
from os import system, getenv, remove, rename
from os.path import join, basename
from zipfile import ZipFile
from sys import platform
import subprocess
from subprocess import run as Run
from shutil import move
from tempfile import gettempdir

# nome do arquivo que será compactado o
# conteúdo baixado.
if platform == "win32":
   ZIPADO = "zipado.zip"
elif platform == "linux":
   ZIPADO = "main.zip"
else:
   raise Exception("não implementado para tal!")
DESTINO = gettempdir()


# faz o download em sí, e, por fim,
# retorna o caminho do zip baixado.
def faz_download(link: str, destino):
   caminho = join(destino, ZIPADO)

   if platform == "win32":
      array = ["pwsh", "-Command",
      "Invoke-WebRequest -Uri",
      link, "-OutFile", caminho]
   elif platform == "linux":
      array = [
         "wget", "--no-cookies",
         "--quiet", "-P",
         destino, link
      ]
   ...
   # rodando comando em sí.
   Run(array)
   # caminho do zip é retornado.
   return caminho
...

# descompacta o arquivo baixado. Retorna
# o caminho do diretório descompactado
# no fim.
def descompacta(caminho):
   archive = ZipFile(caminho)
   # nome do diretório geral dentro dele.
   nome_zip = archive.namelist()[0]
   nome = join(DESTINO, nome_zip)
   # extraindo seu conteúdo.
   archive.extractall(path=DESTINO)
   archive.close()
   # nome do diretório do arquivo descompactado.
   return nome
...

# baixa o pacote e descompacta, dado o 
# específico "cabeçalho". Retorna o caminho
# do produto final.
# NOTA: não funciona em multi-thread, ou
# qualquer outro meio de parelelismo.
def baixa(cabecalho, dicio):
   caminho = faz_download(dicio[cabecalho], DESTINO)
   nome_dir = descompacta(caminho)
   # extrai o trecho "-main" do nome do diretório.
   novo_nome = join(DESTINO, nome_dir[0:-6])
   if __debug__:
      nome = basename(nome_dir)
      print(
         "\nnome antigo:{}\nnovo nome:{}"
         .format(nome_dir, novo_nome), end="\n\n"
      )
   ...
   rename(nome_dir, novo_nome)
   # remove o 'archive' baixado.
   remove(caminho)

   # retorna o caminho do diretório que foi
   # baixado, descompactado e renomeado.
   caminho = novo_nome
   return caminho
...

from datetime import datetime
from gerenciador import MiniMapa as MM
# o mesmo que acima, porém também retorna
# a versão no caso de pacotes Rust, e
# o tempo decorrido desde á última alteração.
Metadados = (str, datetime, str)
def baixa_e_metadados(cabecalho: str, dicio: MM) -> Metadados:
   # bibliotecas importantes:
   from metadados import (
      ultima_modificacao as UM,
      descobre_versao
   )
   from zipfile import ZipFile
   caminho = faz_download(dicio[cabecalho], DESTINO)
   # retira a alteração mais recente.
   with ZipFile(caminho) as arquivo_zip:
      tempo = UM(arquivo_zip)
      versao = descobre_versao(arquivo_zip)
   ...
   nome_dir = descompacta(caminho)
   # extrai o trecho "-main" do nome do diretório.
   novo_nome = join(DESTINO, nome_dir[0:-6])
   rename(nome_dir, novo_nome)
   # remove o 'archive' baixado.
   remove(caminho)
   # retorna o caminho do diretório que foi
   # baixado, descompactado e renomeado.
   caminho = novo_nome
   # deletando porque não serão mais utilizadas,
   # nem dentro, nem fora deste escopo.
   del UM, ZipFile, descobre_versao
   return (caminho, tempo, versao)
...

import unittest
class Funcoes(unittest.TestCase):
   def downloadEMetadados(self):
      from gerenciador import carrega
      from os.path import exists
      from shutil import rmtree
      mapa = carrega()["rust"]
      info = baixa_e_metadados("Utilitários", mapa)
      print(info)
      self.assertTrue(exists(info[0]))
      rmtree(info[0])
      self.assertFalse(exists(info[0]))
      del exists,  rmtree, carrega
   ...

if __name__ == "__main__":
   unittest.main()
...

# o que pode ser importado:
__all__ = ["baixa_e_metadados", "faz_download"]
