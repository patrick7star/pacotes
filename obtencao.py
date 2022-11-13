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
def faz_download(link, destino):
   caminho = join(destino, ZIPADO)

   if platform == "win32":
      array = ["pwsh", "-Command",
      "Invoke-WebRequest -Uri",
      link, "-OutFile", caminho]
   elif platform == "linux":
      array = [
         "wget", "--no-cookies",
         "--no-verbose", "-P",
         DESTINO, link
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

if __name__ == "__main__":
   from python_utilitarios.utilitarios import arvore
   from python_utilitarios.utilitarios import testes
   Arvore = arvore.arvore
   GalhoTipo = arvore.GalhoTipo
   del arvore
   from os.path import exists
   from gerenciador import carrega, mapa

   def testa_procedimento_baixa():
      if not carrega():
         print("não possível carregar os 'links'.")
         return None
      ...

      caminho = baixa("Efeito do Matrix", mapa)
      assert exists(caminho)
      caminhoI = baixa("Utilitarios", mapa)
      assert exists(caminhoI)

      print(
         Arvore(
            caminho,
            mostra_arquivos=True,
            tipo_de_galho=GalhoTipo.FINO
         )
      )
      print(Arvore(caminhoI, True))

      # deleta diretórios algum tempo depois.
      print("deletando ...", end=" ")
      Run([
         "pwsh", "-Command",
         "Remove-Item -LiteralPath",
         caminho, ',', caminhoI,
         "-Recurse"
      ])
      assert not exists(caminho)
      assert not exists(caminhoI)
      print("feito com sucesso.")
   ...

   def baixa_demandado_pacote():
      if not carrega():
         print("não possível carregar os 'links'.")
         return None
      ...
      entrada = input("digite o cabeçalho à baixar: ")
      caminho = baixa(entrada, mapa)
      move(caminho, '.')
   ...

   # executa os testes em sí.
   testes.executa_teste(
      #baixa_demandado_pacote,
      testa_procedimento_baixa,
   )
...
