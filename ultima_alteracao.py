

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
def ultima_modificacaoDT(archive) -> datetime:
   if type(archive) != ZipFile:
      assert ValueError()
   return min(extraiDT(zI) for zI in archive.infolist())
...
      
__all__ = ["ultima_modificacaoDT"]

if __name__ == "__main__":
   # carrega os links do Python.
   carrega()

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
      archive.close()
   ...

   for (nome, link) in mapa.items():
      caminho = faz_download(link, "/tmp/")
      mais_recente(caminho)
      remove(caminho)
      assert False
   ...
