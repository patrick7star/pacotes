#!/usr/bin/python3 -O
"""
  Programa em sí que baixa os pacotes e arruma no atual diretório. Também
é possível selecionar o arquivo específico a extrair.
"""

# deste programa:
#from obtencao import baixa
from gerenciador import ( carrega, listagem, listagemI, CORE_PYTHON)
from banco_de_dados import (atualiza_bd, grava_pacote_registro)
from obtencao import baixa_e_metadados as baixa

# biblioteca externa:
from python_utilitarios.utilitarios import arvore
GalhoTipo = arvore.GalhoTipo
arvore = arvore.arvore

# biblioteca padrão do Python:
from sys import argv
from os.path import (isdir, abspath, basename, exists, join)
from shutil import (rmtree, move)
from os import chmod
from stat import (S_IRWXU, S_IXGRP, S_IXOTH)
from argparse import (ArgumentParser, SUPPRESS)
import platform

# colocando permisões:
try:
   chmod("pacotes.py", S_IRWXU | S_IXGRP | S_IXOTH)
except FileNotFoundError:
   caminho = join(CORE_PYTHON, "pacotes/pacotes.py")
   chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)
...

# gera link simbólico se não houver algum.
def cria_link_simbolico_no_linux():
   from pathlib import PosixPath
   from os import (getcwd,getenv, symlink,chdir)

   arquivo_execucao = PosixPath(CORE_PYTHON, "pacotes/pacotes.py")
   caminhoI = PosixPath(getenv("HOME"), ".local/usr/sbin")
   caminhoII = PosixPath(getenv("HOME"), ".local/usr/bin")
   inicial = getcwd()

   if caminhoI.exists():
      if __debug__:
         print("atual diretório:", getcwd())
      chdir(caminhoI)
      atual = caminhoI
      if __debug__:
         print("atual diretório:", getcwd())
   elif caminhoII:
      if __debug__:
         print("atual diretório:", getcwd())
      chdir(caminhoII)
      atual = caminhoII
      if __debug__:
         print("atual diretório:", getcwd())
   else:
      raise Exception("caminho não encontrado")
   if __debug__:
      print("criando link até {} de '{}'".format(arquivo_execucao, atual))
   else:
      link_caminho = PosixPath("pacotes")
      if (not link_caminho.is_symlink()):
         if __debug__:
            print("atual diretório:", getcwd())
         symlink(arquivo_execucao, "pacotes")
         assert link_caminho.is_symlink()
         print("link criado!")
      else:
         print("link já existe!")
   ...
   chdir(inicial)
   if __debug__:
      print("atual diretório:", getcwd())
...
def cria_link_simbolico () -> bool:
   sistema_operacional = platform.platform()
   if sistema_operacional == "Linux":
      cria_link_simbolico_no_linux()
   elif sistema_operacional == "Windows":
      print("sem criação de links(ainda) para Windows.")
...

def move_diretorio_rust(caminho, destino) -> None:
   """
     Trabalha específico com o movimento do conteúdo descompactado para o 
   atual diretório. Isto é preciso já que ele poder ter um diretório com o 
   mesmo nome, que então deverá ser substituído, porém com cuidado, já que,
   pode conter artefatos anteriormente compilados que devem ser mantidos.
   """

   # closure que verifica se ambos
   # diretórios dados são Rust.
   eUmDirRust = (
      lambda caminho:
         # existe tal caminho, é um diretório
         # e têm um arquivo Toml do cargo para
         # deixar claro que está trabalhando
         # com um diretório Rust.
         exists(caminho) and
         isdir(caminho) and
         exists(join(caminho, "Cargo.toml"))
   )
   # diretório com mesmo nome no atual.
   mesmo_dir = basename(caminho)
   # condição para deslocamento cuidadoso.
   if eUmDirRust(mesmo_dir) and eUmDirRust(caminho):
      # pasta com testes, debugs e otimizados compilados.
      artefatos = join(mesmo_dir, "target")
      artefato_existente = exists(artefatos)
      if artefato_existente:
         print("movendo 'target' para '{}'...".format(caminho))
         move(artefatos, caminho)
   else:
      print("o pacote neste dir não tem 'artefatos'.")
   if eUmDirRust(mesmo_dir):
      print("removendo '{}'...".format(mesmo_dir))
      rmtree(mesmo_dir, ignore_errors=True)
   print("movendo '{}' para '{}'".format(caminho, abspath(".")))
   move(caminho, ".")
...

def move_diretorio_python(caminho, destino) -> None:
   """
     Mesmo acima, porém que para o Python. Por ser geralmente ignorada o 
   diretório com artefatos, porque também seria bem mais difícil a 
   implementação, o código é bem mais simples.
   """
   mesmo_dir = basename(caminho)
   if exists(mesmo_dir):
      print("excluíndo '{}'...".format(abspath(mesmo_dir)), end=' ')
      rmtree(mesmo_dir)
      print("feito.")
      assert notexists(mesmo_dir)
   ...
   print("movendo '{}' para '{}'".format(caminho, abspath(".")))
   move(caminho, ".")
...

from pathlib import WindowsPath
from time import (sleep, time)

# tempo total de quanto ela durará.
PAUSA = 5.4

def esta_no_diretorio_raiz () -> bool:
   """
   O program provalvemente funciona, já que exige um arquivo e um diretório
   no mínimo. A probabilidade de responder corretamente não é 100%.
   """
   print ("argumentos passados: %s" % argv)
   diretorio_presentes = (
      WindowsPath(".\\data").exists() or
      WindowsPath(".\\repositorios").exists() or
      WindowsPath(".\\python_utilitarios").exists()
   )
   
   arquivos_presentes = (
      WindowsPath (".\\banco_de_dados.py").exists() or
      WindowsPath (".\\gerenciador.py").exists() or
      WindowsPath (".\\metadados.py").exists() or
      WindowsPath (".\\gerenciador.py").exists()
   )

   arquivo_principal = WindowsPath("pacotes.py").exists()
   return diretorio_presentes or arquivos_presentes and arquivo_principal
...

def pausa_para_visualizacao() -> bool:
   """
      Pausa para ver resultado por alguns segundos. Apenas aparece se não
   estiver no diretório raíz do programa.

   """
   if platform.system() == "Windows" and (not esta_no_diretorio_raiz()):
      ti = time()
      atual = time() - ti
      while atual < PAUSA:
         print("\rfechará em {:0.1f}seg".format(atual), end='')
         sleep(0.1)
         atual = time() - ti
      ...
      # confirma que houve apresentação.
      return True
   else:
      # diz que não houve uma, não deve ser válido para a plataforma.
      return False
...

from repositorio import cria_novo_repositorio_json
from menu import (ARGS, GRADE)

# inicializaçã e configuração básica do projeto ...
cria_novo_repositorio_json()
cria_link_simbolico()
   
# disparando o menu:
if ARGS.lista is not None:
   linguagem = ARGS.lista[0]
   listagemI(GRADE, linguagem)
elif ARGS.obtem is not None:
   # organizando ARGS da linha-de-comando.
   cabecalho = ARGS.obtem[1]
   linguagem = ARGS.obtem[0]
   if __debug__:
      print(
         "\n{barra}\nbaixando ... '{}' do {}\n{barra}\n"
         .format(
            cabecalho,
            linguagem.upper(),
            barra='*' * 50
         )
      )
   else:
      # carrega "mapa completo".
      #mapa = carrega()
      mapa = GRADE
      # o mapa específico da linguagem.
      minimapa = mapa[linguagem.lower()]
      # baixa o download, e recebe tanto o
      # caminho com o conteúdo, como seus
      # metadados importantes.
      (caminho, tempo, versao) = baixa(cabecalho, minimapa)
      estrutura = arvore(caminho, True, GalhoTipo.FINO)
      link = minimapa[cabecalho]
      # gravando metadados no banco de dados...
      grava_pacote_registro(
         linguagem.lower(),
         cabecalho, link,
         versao, tempo
      )
      if linguagem.lower() == "rust":
         move_diretorio_rust(caminho, ".")
      elif linguagem.lower() == "python":
         move_diretorio_python(caminho, ".")
      else:
         raise Exception("não implementado para tal linguagem!")
      # info da estrutura do pacote baixado.
      print(
         "{}\n\"{}\" foi baixado com sucesso."
         .format(estrutura, cabecalho),
         end="\n\n"
      )
   ...
elif ARGS.atualiza:
   if __debug__:
      print("atualizando todo BD...")
   else:
      # mapa = carrega()
      mapa = GRADE
      atualiza_bd(mapa)
      print("atualiza foi realizada!")
   ...
else:
   print("nenhuma opção acionada!")

# exucação total depende da plataforma executada.
pausa_para_visualizacao ()

   
