

"""
 Pega as versões de cada pacote, seja
python ou rust, à cada 5min.
"""

# biblioteca padrão:
from datetime import datetime,timedelta
from math import floor, ceil
from random import randint
from shutil import rmtree
from os.path import join as Join
from sys import platform
from os import getenv,remove
# biblioteca externa:
from python_utilitarios.utilitarios import testes
from obtencao import baixa
from gerenciador import core as raiz


# ritmo de busca das versões.
if __debug__:
   RITIMO = timedelta(seconds=15)
else:
   RITIMO = timedelta(minutes=8)
# nome do arquivo contendo última registro.
NOME = Join(raiz, "pacotes/data", "ultima_busca.dat")
# nome do arquivo que guarda info da última
# varredura.
CONDENSADO = Join(raiz, "pacotes/data", "dados_condensados.txt")


# salva 'datetime' em disco.
def grava(dt):
   selo = dt.timestamp()
   # parte-inteira.
   pI = floor(selo)
   # cada parte filtrada.
   (inteiro, decimal) = (pI, selo - pI)

   if __debug__:
      # talvez aceitar-se perder a presição de
      # milisegundos.
      transformacao = ceil(decimal * 10 ** 6)
      print("\nselo = %f(%0.6i)" % (selo, transformacao))
      print("inteiro=%i\tdecimal=%f\n" % (inteiro, decimal))
   ...

   # transforma o decimal em inteiro, apenas
   # para guardar seus bytes. Perde a precisão
   # de milisegundos no processo.
   decimais = int(decimal * (10 ** 6))

   # primeiro grava a parte inteira, e
   # depois a parte decimal.
   with open(NOME, mode="w+b") as arquivo:
      # valor em 1bi, então quatro bytes é o suficiente:
      bytes = inteiro.to_bytes(4, byteorder="big")
      arquivo.write(bytes)
      # também 4 bytes:
      bytes = decimais.to_bytes(4, byteorder="big")
      arquivo.write(bytes)
   ...
...

# recupera do disco.
def carrega() -> datetime:
   with open(NOME, "r+b") as arquivo:
      # primeiro 4 bytes da parte inteira.
      string_bytes = arquivo.read(4)
      inteiro = int.from_bytes(string_bytes, byteorder="big")
      # os 4 últimos bytes da parte decimal.
      bytes = arquivo.read(4)
      decimal = int.from_bytes(bytes, byteorder="big")

      # transformando a parte decimal em...
      # bem, decimal, ora!
      decimal = decimal / (10 ** 6)

      # visualizando construção.
      if __debug__:
         print(
            """strBytes='{}'
            \rinteiro={}
            \rdecimal={}
            """
            .format(
               string_bytes, 
               inteiro,
               decimal
            )
         )
      ...

      # convertendo para o tipo 'datetime'
      # novamente, já que é fácil recriar
      # o valor ejetado pela função 'timstamp'
      selo = inteiro + decimal
      return datetime.fromtimestamp(selo)
...

def inverte_iterador(iterador):
   pilha = []

   for item in iterador:
      pilha.append(item)

   while len(pilha) > 0:
      yield(pilha.pop())
...

# extrai de um arquivo com versões, que
# foram extraídas recentementes.
def ve_antigo_registro(chave):
   # vendo último update no banco.
   ultima_atualizacao = carrega()
   agora = datetime.today()
   transcorrido = agora - ultima_atualizacao

   if transcorrido < RITIMO:
      # apenas mostra tempo restante.
      print(
         "faltam {:^0.7s} para nova atualização."
         .format(str(RITIMO - transcorrido))
      )
      # repositório com última versão registrada.
      with open(CONDENSADO, "rt") as arquivo:
         for linha in inverte_iterador(arquivo):
            # se não contém "::" é inválido.      
            if "::" not in linha:
               continue
            (ch, _, versao) = tuple(linha.split("::"))
            if ch == chave:
               return versao[1:].rstrip("\n")
         ...
      ...
   else:
      grava(agora)
      # delete o arquivo para uma atualização.
      print(
         "this file is empty", 
         file = open(CONDENSADO, "wt")
      )
   ...

   # chave, possivelmente nova, então sem dado.
   return None;
...

# extrai versão após fazer o download do arquivo.
# Ela é tirada do arquivo 'Toml', portanto,
# tal método(função) apenas funciona com pacotes
# de 'Rust'.
def extrai_versao(chave, mapa):
   # lê arquivo já pronto.
   versao = ve_antigo_registro(chave) 
   if versao is not None:
      return versao

   # faz o processo todo de download e 
   # extração do arquivo 'Toml'.
   caminho = baixa(chave, mapa)
   # arquivo 'Toml', apenas diretórios com
   # código Rust terão.
   novo_caminho = Join(caminho, "Cargo.toml")

   with open(novo_caminho, "rt") as arquivo:
      for linha in arquivo:
         # se achar linha, pega o conteúdo
         # após o símbolo de igualdade.
         if linha.startswith("version"):
            trecho = linha.split("=")[1]
            trecho = trecho.strip("\"\n ")
            arquivo.close()
            # deleta diretório(irrelevante agora)
            rmtree(caminho, ignore_errors=True)
            return trecho
         ...
      ...
   ...

   # deleta diretório(irrelevante agora)
   rmtree(caminho, ignore_errors=True)
   return None
...

def completa_mapa(mapa):
   """
   novo mapa contendo também a versão dos pacotes
   Rust. A formatação difere um pouco, o 'cabeçalho'
   que é a chave do 'dicionário', contém uma 'lista
   de referência' ao invés de apenas uma string, o
   primeiro elemento de tal é o antigo 'link', o 
   segundo é a versão.
   """
   novo_mapa = {}
   arquivo = open(CONDENSADO, "at")

   for chave in mapa.keys():
      novo_mapa[chave] = []
      # guarda o conteúdo...
      novo_mapa[chave].append(mapa[chave])
      # e criando versão melhorada.
      versao = extrai_versao(chave, mapa)

      if versao is not None:
         novo_mapa[chave].append(versao)
         print(
            "{}::{}::v{}"
            .format(
               chave, novo_mapa[chave][0], 
               novo_mapa[chave][1]
            ),
            file = arquivo
         )
      ...
   ...
   arquivo.close()
   return novo_mapa
...

__all__ = ["completa_mapa"]

if __name__ == "__main__":
   from time import sleep
   from gerenciador import (mapa as Mapa, carrega_rust)

   def teste_funcao_grava():
      hoje = datetime.today()
      grava(hoje)
   ...

   def teste_funcao_carrega():
      atual = datetime.today()
      grava(atual)
      sleep(5.0)
      atual = datetime.today() 
      decorrido = atual - carrega()
      print(decorrido)
      assert decorrido.seconds == 5.0
   ...

   def teste_de_completa_mapa():
      carrega_rust()
      m = completa_mapa(Mapa)
      for (chave, lista) in m.items():
         assert type(chave) == str
         assert type(lista) == list
         (lista, versao) = lista
         assert (
            "." in lista[1] and 
            lista[1].isdigit()
         )
         print("""
            \rchave = '{}'
            \rlista = '{}'
            \rversão = \"v{}\"
            """.format(chave, lista, versao)
         )
      ...
   ...

   testes.executa_teste(teste_funcao_grava)
   testes.executa_teste(teste_funcao_carrega)
   testes.executa_teste(teste_de_completa_mapa)
...

