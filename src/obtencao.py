"""
  A parte que baixa o arquivo e descompacta-o, como também move o produto
de tais operações serão colocadas aqui, por motivos de organização(mirando
a legibilidade).
"""

# o que pode ser importado:
__all__ = [
  "Metadados", "LinqueError", "realiza_download", "baixa_com_metadados",
  "realiza_download_simultaneo", "realiza_download_via_curl"
]

# Biblioteca padrão do Python:
from os import system, getenv, remove, rename
from os.path import join, basename
from sys import (platform, stderr)
from zipfile import ZipFile
import subprocess
from subprocess import run as Run
from shutil import move
from tempfile import gettempdir
from datetime import datetime
from pathlib import (Path, )
from typing import (Sequence, List)
import _thread as thread
from time import (sleep)
from platform import (release, system)
from subprocess import (Popen)
# Importando outros módulos deste programa:
from gerenciador import MiniMapa as MM
# Bibliotecas de terceiro.
try:
   import pycurl, certifi
except ModuleNotFoundError:
   print("Bibliotecas 'pycurl' e 'certifi' não disponíveis.")

# Apelido de alguns tipos de dados:
Versao = str
Caminho = Path
# O último item dela é sua versão(em string, porém apenas números e pontos).
Metadados = (Caminho, datetime, Versao)


def descompacta(caminho) -> Caminho:
   """
      Descompacta o arquivo baixado. Retorna o caminho do diretório
   descompactado no fim.
   """
   DESTINO = local_de_despejo()
   archive = ZipFile(caminho)
   # Nome do diretório geral dentro dele.
   nome_zip = archive.namelist()[0]

   # Extraindo seu conteúdo.
   archive.extractall(path=DESTINO)
   archive.close()

   # nome do diretório do arquivo descompactado.
   return Path(DESTINO).joinpath(nome_zip)

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
      msg_de_erro = "linque inválido: '{}'".format(linque)

      raise LinqueError(msg_de_erro)

   # caminho do zip é retornado.
   return caminho

def realiza_download_simultaneo(entradas: Sequence, destino: Path
  ) -> Sequence[Path]:
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

def realiza_download_via_curl(cabecalho: str, linque: str) -> Path:
   """
   Já realiza o download do arquivo no diretório temporário. Isso com um
   nome até muito difícil de criar 'race conditions'. Retorna o caminho do
   arquivo que foi baixado(como já dito, este no diretório temporário do
   atual OS).
   """
   obj     = pycurl.Curl()
   nome    = "{}.zip".format(cria_nome_exotico(cabecalho))
   #caminho = Path(tempfile.gettempdir(), nome)
   caminho = local_de_despejo().joinpath(nome)
   target  = open(caminho, "wb")

   obj.setopt(obj.URL, linque)
   obj.setopt(obj.WRITEDATA, target)
   obj.setopt(obj.CAINFO, certifi.where())
   obj.setopt(obj.FOLLOWLOCATION, True)
   obj.perform()

   if obj.getinfo(obj.RESPONSE_CODE) != 200:
      obj.close()
      target.close()
      raise LinqueError("Linque inválido")

   obj.close()
   target.close()

   return caminho

def baixa_com_metadados(cabecalho: str, grade: MM) -> Metadados:
   """
     Baixa e descompacta, dado o específico 'cabeçalho'. O retorno é o
   seguinte: o caminho para tal diretório descompactado; o tempo decorrido 
   desde a última alteração; a versão no caso de um Pacote Rust. O mesmo que
   a antiga versão, porém agora mudou o motor de downloads.
   """
   from metadados import (ultima_modificacao, descobre_versao)

   linque = grade[cabecalho]
   try:
      # O algoritmo padrão é a biblioteca externa 'pycurl' pro Python.
      caminho_zip = realiza_download_via_curl(cabecalho, linque)
   except NameError:
      # Caso não dê, tente achar o programa, e embrulha-lo como uma lib.
      algoritmo_de_download = realiza_download_via_curl_por_interface
      caminho_zip = algoritmo_de_download(cabecalho, linque)
      print("Usou 'curl' via interface.")
   else:
      pass

   # retira a alteração mais recente.
   with ZipFile(caminho_zip) as arquivo_zip:
      tempo = ultima_modificacao(arquivo_zip)
      versao = descobre_versao(arquivo_zip)

   diretorio_da_extracao = descompacta(caminho_zip)
   destino = diretorio_da_extracao.parent
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

def local_de_despejo() -> Path:
   """
     Arranja um diretório de despejo próprio, ao invés de apenas baixar estes
   pacotes de forma nú no diretório temporário. Tal antiga forma causa
   conflito por exemplo se o download for realizado no próprio diretório
   temporário.
   """
   RAIZ = Path(tempfile.gettempdir())
   NOME = "pacotes-baixados"
   result = RAIZ.joinpath(NOME)

   try:
      result.mkdir()
   except FileExistsError:
      if __debug__:
         print("O diretório de despejo já está lá!")
   finally:
      return result

def realiza_download_via_curl_por_interface(cabecalho: str,
  linque: str) -> Path:
   """
     O resultado é o mesmo que a função original, porém, ao invés de usar uma
   biblioteca pronta, geralmente por que não há, ele usa os programas
   instalados do programa que provalvemente já fazem parte. Ele tenta usar
   tanto a versão do Linux(WSL), como a versão do Windows; muito difícil
   alguns deles não estarem instalados.
     O porquê desta função, quando já se tem a original? Bem, quando tentando
   portar tal software por Windows, mesmo usando WSL, esbarrei com tais
   restrições. Elas são facilmente contornável, mas exisgem instalar as
   bibliotecas, o que rejeitei a princípio.
   """
   #if (not LIB_CURL_NAO_ENCONTRADA):
   #   raise ImportError("não foi dado condição para está função")

   CURL_DO_WINDOWS = Path("/mnt/c/Windows/system32/curl.exe")
   CURL_DO_LINUX = Path("/usr/bin/curl")
   NOME_PKG = cria_nome_exotico(cabecalho) + ".zip"
   DESTINO = Path(gettempdir()).joinpath(NOME_PKG)
   # Proposições sobre o sistema operacional utilizado:
   NUMA_WSL = ("WSL2" in release() or "microsoft" in release())
   PLATAFORMA_WINDOWS = (system() == "Windows")
   PLATAFORMA_LINUX = (system() == "Linux" and (not NUMA_WSL))
   PLATAFORMA_WSL = (system() == "Linux" and NUMA_WSL)

   if PLATAFORMA_LINUX:
      EXE = "/usr/bin/curl"

      if not CURL_DO_LINUX.exists():
         raise SystemError("não há um programa '%s'" % CURL_DO_LINUX)
      if __debug__:
         print("Você está em Linux puro.")

   elif PLATAFORMA_WSL:
      EXE = str(CURL_DO_LINUX)

      if not CURL_DO_LINUX.exists():
         raise SystemError("não há um programa '%s'" % CURL_DO_LINUX)
      if __debug__:
         print("Você está num Linux(WSL)")

   elif system() == "Windows":
      raise NotImplementedError()
      if not CURL_DO_WINDOWS.exists():
         raise SystemError("não há um programa '%s'" % CURL_DO_WINDOWS)

   if DESTINO.exists():
      raise FileExistsError("arquivo '%s' já foi baixado." % NOME_PKG)

   Popen([EXE, "-s", "-L", "-o", DESTINO, linque]).wait()
   return DESTINO
# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
#                      e alguns Testes de Features
# === === === === === === === === === === === === === === === === === === = 
import unittest, tempfile
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
      info = baixa_com_metadados("Utilitários", mapa)

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

class DownloadViaCurl(Funcoes):
   def setUp(self):
      from repositorio import (carrega_do_json)

      self.grade_geral  = carrega_do_json()
      self.GRADE_C      = self.grade_geral["c++"]
      self.GRADE_RUST   = self.grade_geral["rust"]
      self.GRADE_PYTHON = self.grade_geral["python"]
      self.contador = 0

      del carrega_do_json

   def tearDown(self):
      diretorio = Path(tempfile.gettempdir())

      print("\nTodos arquivos baixados estão sendo removidos ...")
      for item in diretorio.iterdir():
         if str(item).endswith("zip"):
            print("\t\b\b\b- {}".format(item))
            self.assertTrue(item.exists())
            item.unlink()
            self.assertFalse(item.exists())

   def escolha_pacote_aleatorio() -> (str, str):
      todas_opcoes = list([]).extend(
         list(self.GRADE_C.keys()) +
         list(self.GRADE_PYTHON.keys()) +
         list(self.GRADE_RUST.keys())
      )

      return choice(todas_opcoes)

   def um_simples_download(self):
      print("\nDownload todos pacotes Rust ...")

      for (pacote, linque) in self.GRADE_RUST.items():
         print("Pacote: {}".format(pacote))
         realiza_download_via_curl(pacote, linque)

   def download_de_linque_invalido(self):
      for (pacote, linque) in self.GRADE_C.items():
         print("Pacote: {}".format(pacote))
         try:
            realiza_download_via_curl(pacote, linque)
         except LinqueError:
            print("Algum problema ao baixar de tal linque.")

class LocalDeDespejo(unittest.TestCase):
   def setUp(self):
      self.diretorio = None

   def tearDown(self):
      if self.diretorio is not None:
         self.diretorio.rmdir()
         self.assertFalse(self.diretorio.exists())

   def runTest(self):
      caminho = local_de_despejo()
      self.diretorio = caminho
      dir_str = str(caminho)

      self.assertTrue(caminho.exists())
      print("Caminho dos downloads: %s" % dir_str)

class DownloadDoProprioProgramaNoLocal(unittest.TestCase):
   def setUp(self):
      from repositorio import (carrega_do_json)

      self.grade_geral  = carrega_do_json()
      self.GRADE        = self.grade_geral["python"]
      self.download     = baixa_com_metadados
      self.diretorio    = None

      del carrega_do_json

   def tearDown(self):
      self.assertTrue(self.dir.exists())

      if self.dir is not None:
         rmtree(self.dir)
         self.assertFalse(self.dir.exists())
         # Excluindo também local de despejo:
         local = self.dir.parent
         print("Despejo: '%s'" % str(local))
         self.assertTrue(local.exists())
         self.dir.parent.rmdir()
         self.assertFalse(local.exists())

   def runTest(self):
      pkg      = "Pacotes"
      result   = self.download(pkg, self.GRADE)
      (self.dir, _, _) = result

      self.assertTrue(self.dir.exists())

class RealizaDownloadViaCurlPorInterface(DownloadViaCurl):
   def setUp(self):
      # Executando o antigo ...
      super().setUp();

      escolha = choice([
         self.GRADE_C, 
         self.GRADE_RUST, 
         self.GRADE_PYTHON
      ])
      self.cabecalho = choice(list(escolha.keys()))
      self.linque = escolha[self.cabecalho]

   def runTest(self):
      SEP = "\n\t\b\b- "
      L = self.linque
      C = self.cabecalho

      print(
         "\nO que foi escolhido é:", 
         self.cabecalho, self.linque, 
         sep=SEP, end="\n\n"
      )
      result = realiza_download_via_curl_por_interface(C, L)
      print("Baixado: '{}'".format(result))
    
