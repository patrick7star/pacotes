"""
  Quando executado qualquer vez, verifica se há um linque válido deste 
programa no repositório padrão de linques, se não houver algum cria, se 
houver um quebrado(lique a script errado), então conserta ele.
"""
# O que será exportado?
__all__ = [
   "caminho_do_projeto_do_programa",
   "caminho_do_script",
   "cria_linques_simbolicos"
]

# Biblioteca padrão do Python:
from os import (symlink, getenv, abort)
from pathlib import (Path, )
from sys import argv as Argumentos
from platform import (system as qual_e_o_sistema)

# Tenta criar linque com nome do programa para o arquivo no "repositório"
# de linques de programas codificados:
MSG_ERROR           = "Não é possível prosseguir com o teste"
NOME_DO_LINQUE      = Path("pacotes")
SCRIPT_PRINCIPAL    = "main.py"


def caminho_do_projeto_do_programa() -> Path:
   """
     Assumindo que, tal programa estará no subdiretório 'src', dentro de 
   um diretório 'my_project', esta função retornará o caminho até 
   'my_project'. 
   """
   caminho_str = Argumentos[0]
   caminho = Path(caminho_str).resolve()

   return caminho.parent.parent


def caminho_do_script() -> Path:
   """
     Entrega o caminho do arquivo de script de python que está sendo 
   executado no momento. Basicamente o algoritmo pega a primeira linha 
   dado ao interpletador, e resolve o caminho se for algum relativo.
   """
   dir_projeto = caminho_do_projeto_do_programa()
   return dir_projeto.joinpath("src", "main.py")


def cria_linques_simbolicos() -> None:
   try:
      DIR_LINQUES = Path(getenv("HOME"), getenv("LINKS"))
   except TypeError:
      mensagem_erro = "não foi encontrado variável de ambiente 'LINKS'"
      raise ProcessLookupError(mensagem_erro)

   # Por enquanto, uma possível criação de repositório de linques, estará
   # disponível apenas para o sistema Linux.
   if (qual_e_o_sistema() == "Linux") and (not DIR_LINQUES.exists()):
       print("Repositório de linques não existe, então criando-o ...", end=" ")
       DIR_LINQUES.mkdir(parents=True)
       print("feito!")
       assert (DIR_LINQUES.exists())

   # Linque no repositório de linques:
   destino = DIR_LINQUES.joinpath(NOME_DO_LINQUE)
   fonte = caminho_do_script()
   try:
       destino.symlink_to(fonte)
   except FileExistsError:
       print("O linque no repositório já existe.")

   # Linque no diretório do projeto:
   destino = caminho_do_projeto_do_programa().joinpath(NOME_DO_LINQUE)
   try:
      destino.symlink_to(fonte)
   except FileExistsError:
       print("O linque no diretório do projeto já existe.")

   print("Ambos linques criados.")
   
