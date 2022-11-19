

"""
 É a questão do versionamento, mas para 
o Python. Ao invés da versão, coloca em 
valores legíveis o tempo da última 
alteração realizada.
"""

# módulos do código-fonte:
from obtencao import faz_download, baixa
from gerenciador import carrega, mapa

# biblioteca do Python:
from os import remove
from zipfile import ZipInfo, ZipFile
from datetime import datetime

# biblioteca externa:
from python_utilitarios.utilitarios import legivel

# pega o 'datetime' da estrutura 'ZipInfo',
# que pode referência um arquivo, ou diretório
# dentro do 'ZipFile'.
def extraiDT(zipinfo):
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
def ultima_modificacaoDT(archive) -> datetime:
   if type(archive) != ZipFile:
      assert ValueError()
   return min(extraiDT(zI) for zI in archive.infolist())
...
      
def mais_recente(caminho):
   archive = ZipFile(caminho)
   ultima_modificacao = ultima_modificacaoDT(archive).timestamp()
   hoje = datetime.today().timestamp()
   decorrido = hoje - ultima_modificacao

   tempo_info = legivel.tempo(decorrido)
   print(
      "nome:'{0}'\ntempo:{1:>12.14s}\n"
      .format(archive.filename, tempo_info)
   )
...

def completa_mapa_python(mapa):
   novo_mapa = {}
   for (chave, link) in mapa.items():
      caminho = faz_download(link, "/tmp")
      zipado = ZipFile(caminho)
      ultima_modificacao = ultima_modificacaoDT(zipado)
      hoje = datetime.today()
      decorrido = hoje - ultima_modificacao
      zipado.close()
      remove(caminho)
      novo_mapa[chave] = [link, decorrido]
   ...
   return novo_mapa
...

from unittest import TestCase, main
from pprint import pprint
from datetime import timedelta

__all__ = ["ultima_modificacaoDT", "completa_mapa_python"]

class Testes(TestCase):
   def TodaBiblioteca(self):
      # carrega os links do Python.
      carrega()
      for (nome, link) in mapa.items():
         caminho = faz_download(link, "/tmp/")
         Testes.mais_recente(caminho)
         remove(caminho)
         self.assertTrue(True)
      ...
   ...

   def mais_recente(caminho):
      archive = ZipFile(caminho)
      ultima_modificacao = ultima_modificacaoDT(archive).timestamp()
      hoje = datetime.today().timestamp()
      decorrido = hoje - ultima_modificacao

      tempo_info = legivel.tempo(decorrido)
      print(
         "nome:'{0}'\ntempo:{1:>12.14s}\n"
         .format(archive.filename, tempo_info)
      )
   ...

   def CarregaMapaPython(self):
      carrega()
      M = completa_mapa_python(mapa)
      pprint(M)
      self.assertNotEqual(M, mapa)
      for conteudo in M.values():
         A = type(conteudo[0]) == str
         B = type(conteudo[1]) == timedelta
         self.assertTrue(A)
         self.assertTrue(B)
      ...
   ...

   def ResultadoDesejadoCMP(self):
      carrega()
      M = completa_mapa_python(mapa)
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
      
...

if __name__ == "__main__":
   main(verbosity=2)
