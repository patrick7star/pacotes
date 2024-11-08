"""
  A parte que baixa o arquivo e descompacta-o, como também move o produto 
de tais operações serão colocadas aqui, por motivos de organização(mirando 
a legibilidade).
"""

# o que pode ser importado:
__all__ = [
  "baixa_e_metadados", "faz_download", "Metadados", "LinqueError",
  "realiza_download", "MetadadosI", "baixa_com_metadados",
  "realiza_download_simultaneo"
]

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
from pathlib import (Path, )
from collections.abc import (Sequence)
import _thread as thread
from time import (sleep)
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
Versao = str
# O último item dela é sua versão(em string, porém apenas números e pontos).
Metadados = (Caminho, datetime, str)
MetadadosI = (Path, datetime, Versao)


def faz_download(link: str, destino) -> Caminho:
   " Faz o download em sí, e, por fim, retorna o caminho do zip baixado."
   from metadados import (ultima_modificacao as UM, descobre_versao)
   caminho = join(destino, ZIPADO)

   if platform == "win32":
      array = ["pwsh", "-Command",
      "Invoke-WebRequest -Uri",
      link, "-OutFile", caminho]
   elif platform == "linux":
      array = ["wget", "--no-cookies", "--quiet", "-P", destino, link]

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

   return (caminho, tempo, versao)
...

class LinqueError(Exception):
   "Erro para linque inválido"
   def __int__(self, msg: str) -> None:
      self.mensagem = msg

   def __str__(self) -> str:
      return "LinqueError[\"%s\"]" % self.mensagem

def cria_nome_exotico(In: str) -> str:
   """
     Pega atua nome e formata ele para ser 'único', ou pelo menos um nome 
   novo que é difícil entrar em conflito com outros já existentes.
   """
   caracteres = []
   
   for char in In:
      # Troca seus espaços em brancos, ou separadores, por traços.
      if char.isspace() or char == '/':
         caracteres.append('-')
         continue

      # O tipo da atual letra será determinada randomicamente para cada.
      if choice([True, False]):
         caracteres.append(char.upper())
      else:
         caracteres.append(char)

   return "".join(caracteres)

def realiza_download(cabecalho: str, linque: str, destino: Path) -> Path:
   """
     Faz o download em sí, e, retorna o caminho do zip baixado. A diferença
   deste para o anterior é, que neste, caso o linque não seja válido, ele
   lança uma exceção. No outro, o programa simplesmente quebraria.
   """
   # Criando nome difícil de ser repetido, e adicionando extensão...
   nome_archive = cria_nome_exotico(cabecalho)
   nome_archive += ".zip"
   # Caminho do futuro archive baixado.
   caminho = destino.joinpath(nome_archive)

   if platform == "win32":
      comando = [
         "pwsh", "-Command", "Invoke-WebRequest -Uri", linque, 
         "-OutFile", caminho
      ]
   elif platform == "linux":
      comando = ["wget", "--no-cookies", "--quiet",'-O', caminho, linque]

   # rodando comando em sí.
   resultado = Run(comando)

   if resultado.returncode != 0:
      if __debug__:
         print("Remove resíduo '{}'.".format(caminho.name))
      caminho.unlink()
      raise LinqueError()

   # caminho do zip é retornado.
   return caminho

def realiza_download_simultaneo(entradas: Sequence, destino: Path
 ) -> Path[Sequence]:
   """
     O mesmo que acima, porém pega uma lista de demandas, e também retorna
   uma lista de caminhos de cada download.

     Como a função acima já realiza tal tipo de função -- desculpe-me tal
   redundância --, será apenas criado tuplas com os parâmetros necessários,
   e então chama-lâ, em paralelo, para cada um, coletando seus resultados.
   """
   # Lista de 'pool_de_threads de threads', e retorno de cada uma.
   pool_de_threads = []; saidas = []
   # Guarda de exclusão do uso de recursos:
   mutex = thread.allocate_lock()

   def download(argumentos: tuple[str, str, Path]) -> None:
      """
        Pega uma tupla com todos os principais argumentos necessário para
      chamar a função 'realiza_download'(que é single-thread). Ela será 
      executada paralelamente com o código principal. O resultado dela
      será adicionada na lista da função principal.
      """
      nonlocal pool_de_threads, saidas
      ID = thread.get_ident()
      tupla = argumentos
      
      # Adiciona a atual thread no 'pool de threads' da função "global"
      # desta aqui.
      mutex.acquire(); pool_de_threads.append(ID); mutex.release()
      # Captura o resultado, então escreve na "via" de saída, ou seja,
      # para o chamador(caller) desta função.
      output = realiza_download(tupla[0], tupla[1], tupla[2])
      # Adiciona o resultado da função chamada dentro da lista, então
      # descontabiliza o ID no termino dela.
      mutex.acquire()
      saidas.append(output)
      pool_de_threads.remove(ID)
      mutex.release()

   auxiliar = []
   # Agloromerando argumentos em tuplas de quatro valores, sendo os três
   # primeiros as entradas da função, e o último a saída.
   for p in range(0, len(entradas), 2):
      header = entradas[p]
      link = entradas[p + 1] 
      tupla_arg = (header, link, destino)

      auxiliar.append(tupla_arg)
   # Despejando última lista, e capturando nova com argumentos agrupados
   # para serem passados para função que executa a thread.
   entradas = auxiliar

   # Começar a chocar as threads em sequência.
   for args in entradas:
      id = thread.start_new_thread(download, (args,))
      if __debug__:
         print("Thread[%d] chocada com sucesso." % id)

   # Tempo de exibição de info das threads em execução.
   PAUSA = 0.600 
   # Trecho para aguardar os terminos de todas threads...
   while len(pool_de_threads) > 0:
      print("Downloads em execução(%d)" % len(pool_de_threads))
      sleep(PAUSA)

   return saidas

def baixa_com_metadados(cabecalho: str, grade: MM) -> MetadadosI:
   """
     Baixa e descompacta, dado o específico 'cabeçalho'. O retorno é o
   seguinte: o caminho para tal diretório descompactado; o tempo decorrido 
   desde a última alteração; a versão no caso de um Pacote Rust.
   """
   from metadados import (ultima_modificacao, descobre_versao)

   linque = grade[cabecalho]
   destino = Path(DESTINO)
   caminho_zip = realiza_download(cabecalho, linque, destino)

   # retira a alteração mais recente.
   with ZipFile(caminho_zip) as arquivo_zip:
      tempo = ultima_modificacao(arquivo_zip)
      versao = descobre_versao(arquivo_zip)

   diretorio_da_extracao = Path(descompacta(caminho_zip))
   # Extrai o trecho "-main" do nome do diretório.
   nome_do_dir = diretorio_da_extracao.name
   fim = nome_do_dir.index("-main")
   novo_nome = nome_do_dir[0: fim]
   novo_nome = destino.joinpath(novo_nome)
   # Troca o nome do diretório para ele. O resultado também é o diretório
   # com o conteúdo descompactado.
   caminho = diretorio_da_extracao.rename(novo_nome)
   # Remove zip que já foi extraído.
   caminho_zip.unlink()

   return (caminho, tempo, versao)


# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
#                      e alguns Testes de Features
# === === === === === === === === === === === === === === === === === === = 
import unittest
from gerenciador import carrega
from os.path import exists
from shutil import rmtree
from random import (choice)

class Funcoes(unittest.TestCase):
   def setUp(self):
      from repositorio import (carrega_do_json)

      self.grade_geral  = carrega_do_json()
      self.GRADE_C      = self.grade_geral["c++"]
      self.GRADE_RUST   = self.grade_geral["rust"]
      self.GRADE_PYTHON = self.grade_geral["python"]

      del carrega_do_json

   def downloadEMetadados(self):
      mapa = self.GRADE_RUST
      info = baixa_e_metadados("Utilitários", mapa)

      print(info)
      self.assertTrue(exists(info[0]))
      rmtree(info[0])
      self.assertFalse(exists(info[0]))

   def novoFazDownload(self):
      destino = Path.cwd().parent
      linques = list(self.GRADE_C.keys())

      print("Destino: '%s'" % destino)

      for pkg in linques:
         try:
            link = self.GRADE_C[pkg]
            result = realiza_download(link, destino)

            print("[SUCCESS] Package: '{}'".format(pkg))

            self.assertTrue(result.exists())
            result.unlink()
            self.assertTrue(not result.exists())

         except LinqueError:
            print("[ ERROR ] Package: '{}'".format(pkg))
      self.assertTrue(True)

   def novoBaixadorComMetadados(self):
      resultado = baixa_com_metadados("Utilitários", self.GRADE_RUST)
      print("caminho: '%s'" % resultado[0])
      print(resultado)

      self.assertTrue(resultado[0].exists())
      rmtree(resultado[0])
      self.assertFalse(resultado[0].exists())

   def resolvendoParalelismoNosDownloads(self):
      destino = Path.cwd().parent
      linques = list(self.GRADE_RUST.keys())
      entradas = []

      for pkg in linques:
         link = self.GRADE_RUST[pkg]
         entradas.append(pkg)
         entradas.append(link)

      result = realiza_download_simultaneo(entradas, destino)

      self.assertTrue(True)

   def lowLevelThreadsUse(self):
      from _thread import (start_new_thread, get_ident) 
      from time import sleep
      from random import randint

      pool_threads = []

      def exibidor(msg: str):
         nonlocal pool_threads

         millis = randint(200, 1100) / 1000
         qtd = randint(15, 39)
         ID = get_ident()

         pool_threads.append(ID) 

         for q in range(1, qtd):
            print("[{}º | {}seg | {}] {} ...".format(q, millis, qtd,  msg))
            sleep(millis)
         
         pool_threads.remove(ID)

      args = ["Banana e Tomate", "Minha vó é uma peça", 
            "Homens e Mulhres de preto"]
      cursor = 0
      pausa_thread_principal = 1.3

      for a in args:
         id = start_new_thread(exibidor, (a, ))
         print("Thread n.º {} iniciada com sucesso.".format(id))

      while len(pool_threads) > 0:
         for thready in pool_threads:
            print('\t- ', thready, "ainda está ativa.")
         sleep(pausa_thread_principal)
...
