

"""
 É a questão do versionamento, mas para 
o Python. Ao invés da versão, coloca em 
valores legíveis o tempo da última 
alteração realizada.
"""

# módulos do código-fonte:
from obtencao import faz_download 
from gerenciador import carrega

# biblioteca do Python:
from os import remove
from zipfile import ZipInfo, ZipFile
from datetime import datetime

# biblioteca externa:
from python_utilitarios.utilitarios import legivel

# pega o 'datetime' da estrutura 'ZipInfo',
# que pode referência um arquivo, ou diretório
# dentro do 'ZipFile'.
def extraiDT(zipinfo) -> datetime:
   if type(zipinfo) != ZipInfo:
      assert ValueError()
   tupla = zipinfo.date_time
   return datetime(
      tupla[0], tupla[1], tupla[2], 
      hour = tupla[3],
      minute =  tupla[4], 
      second = tupla[5]
   )
...

# retorna 'datetime' do arquivo mais recente 
# adicionado ao 'ZipFile', ou modificado dentro 
# dele mesmo.
def ultima_modificacao(archive) -> datetime:
   if type(archive) != ZipFile:
      assert ValueError()
   return min(extraiDT(zI) for zI in archive.infolist())
...
# adiciona o tempo da última modificação
# que foi realizado no código em geral.
# No caso, ele pega o mapa dado, e insere
# nele o tempo, numa lista, sendo o primeiro
# elemento dela o link.
def adiciona_tempoUM(mapa) -> {str: [str, datetime]}:
   novo_mapa = {}
   for (chave, link) in mapa.items():
      caminho = faz_download(link, "/tmp")
      zipado = ZipFile(caminho)
      um = ultima_modificacao(zipado)
      hoje = datetime.today()
      decorrido = hoje - um
      zipado.close()
      remove(caminho)
      novo_mapa[chave] = [link, decorrido]
   ...
   return novo_mapa
...

# pega o arquivo zipado que foi baixado, então 
# extrai a versão do pacote, se e somente se,
# ele for um pacote Rust.
def descobre_versao(arquivo_zip) -> str:
   if type(arquivo_zip) != ZipFile:
      assert ValueError()
   # buscando pelo arquivo 'Cargo.toml',...
   # se não achado retorna 'nada'.
   arquivo = None
   for caminho in arquivo_zip.namelist():
      if caminho.endswith("Cargo.toml"):   
         arquivo = arquivo_zip.open(caminho, "r")
         if __debug__:
            print("arquivo encontrado!")
         break
      ...
   else:
      return None
   for linha in arquivo:
      # se achar linha, pega o conteúdo
      # após o símbolo de igualdade.
      if linha.startswith(b"version"):
         trecho = linha.split(b"=")[1]
         trecho = trecho.strip(b"\"\n ")
         arquivo.close()
         return trecho.decode(encoding="ascii")
      ...
   ...
   arquivo.close()
   # chega até o fim, sem disparar nada!
   # Então não há tal linha no arquivo Toml.
   return None
...

from unittest import TestCase, main
from pprint import pprint
from datetime import timedelta

__all__ = [
   "ultima_modificacao",
   "adiciona_tempoUM",
   "descobre_versao"
]

class Testes(TestCase):
   def TodaBiblioteca(self):
      # carrega os links do Python.
      mapa = carrega()
      for (nome, link) in mapa["python"].items():
         caminho = faz_download(link, "/tmp/")
         Testes.mais_recente(caminho)
         remove(caminho)
         self.assertTrue(True)
      ...
   ...
   def mais_recente(caminho):
      archive = ZipFile(caminho)
      uM = ultima_modificacao(archive).timestamp()
      hoje = datetime.today().timestamp()
      decorrido = hoje - uM

      tempo_info = legivel.tempo(decorrido)
      print(
         "nome:'{0}'\ntempo:{1:>12.14s}\n"
         .format(archive.filename, tempo_info)
      )
   ...
   def CarregaMapaPython(self):
      mapa = carrega()
      M = adiciona_tempoUM(mapa["python"])
      pprint(M)
      self.assertNotEqual(M, mapa)
      for conteudo in M.values():
         A = type(conteudo[0]) == str
         B = type(conteudo[1]) == timedelta
         self.assertTrue(A)
         self.assertTrue(B)
      ...
   ...
   def ResultadoDesejadoATUM(self):
      mapa = carrega()
      M = adiciona_tempoUM(mapa["python"])
      print("\nListagem de Mentirinha:")
      for (cabecalho, array) in M.items():
         t = array[1].total_seconds()
         print(
            "{recuo}{}\t~ {}"
            .format(
               cabecalho, 
               legivel.tempo(t),
               recuo = ' ' * 5
            )
         )
      # avaliação manual.
      self.assertTrue(True)
      ...
   ...
   def DescobreVersao(self):
      from os import remove
      mapa = carrega()["rust"]
      pprint(mapa)
      caminho = faz_download(mapa['Bate-Bola'], ".")
      arquivoZip = ZipFile(open(caminho, "rb"))
      print(descobre_versao(arquivoZip))
      print(caminho)
      remove(caminho)
   ...
...

if __name__ == "__main__":
   main(verbosity=2)
