"""
  A parte que baixa o arquivo e descompacta-o, como também move o produto 
de tais operações serão colocadas aqui, por motivos de organização(mirando 
a legibilidade).
"""

# o que pode ser importado:
__all__ = ["baixa_e_metadados", "faz_download", "Metadados"]

# biblioteca padrão do Python:
from os import system, getenv, remove, rename
from os.path import join, basename
from sys import platform
from zipfile import ZipFile
import subprocess
from subprocess import run as Run
from shutil import move
from tempfile import gettempdir
from datetime import datetime
import unittest
# importando outros módulos deste programa:
from gerenciador import MiniMapa as MM

# nome do arquivo que será compactado o conteúdo baixado.
if platform == "win32":
   ZIPADO = "zipado.zip"
elif platform == "linux":
   ZIPADO = "main.zip"
else:
   raise Exception("não implementado para tal!")
DESTINO = gettempdir()

# Apelido de alguns tipos de dados:
Caminho = str
# O último item dela é sua versão(em string, porém apenas números e pontos).
Metadados = (Caminho, datetime, str)


def faz_download(link: str, destino) -> Caminho:
   " Faz o download em sí, e, por fim, retorna o caminho do zip baixado."
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

def descompacta(caminho) -> Caminho:
   """
      Descompacta o arquivo baixado. Retorna o caminho do diretório 
   descompactado no fim.
   """
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

def baixa_e_metadados(cabecalho: str, dicio: MM) -> Metadados:
   """
     Baixa e descompacta, dado o específico 'cabeçalho'. O retorno é o
   seguinte: o caminho para tal diretório descompactado; o tempo decorrido 
   desde a última alteração; a versão no caso de um Pacote Rust.
   """
   # bibliotecas importantes:
   from metadados import ( ultima_modificacao as UM, descobre_versao)
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
   remove(caminho)
   # retorna o caminho do diretório que foi baixado, descompactado e 
   # renomeado.
   caminho = novo_nome

   # deletando porque não serão mais utilizadas, nem dentro, nem fora 
   # deste escopo.
   del UM, descobre_versao
   return (caminho, tempo, versao)
...

''' === === === === === === === === === === === === === === === === === ==
                           Testes Unitários
                      e alguns Testes de Features

 === === === === === === === === === === === === === === === === === == '''
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
...

