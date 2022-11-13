

"""
 Um histórico do download aonde, não
apenas registre a versão dos códigos
baixados, mas também dê estatísticas 
sobre os downloads feitos.
"""

from array import array 
from datetime import timedelta
#from datetime import datetime
from serializacao_datetime import (datetime, Array)

# converte uma array de bytes para uma string.
def bytes_to_string(_bytes):
   return "".join(chr(c) for c in _bytes)

class Download:
   """
   registro com dados básicos de um download
   feito. Além de tal ítem poder ser comparado,
   também será serializado/deserializado para
   armazenamento em disco.
   """
   def __init__(self, nome, endereco, versao, selo):
      self.nome = nome
      self.link = endereco 
      self.versao = versao 
      if selo is None:
         self.momento = datetime.today()
      else:
         self.momento = selo
   ...

   def __eq__(self, outro):
      link_bate = self.link == outro.link 
      nome_bate = self.nome == outro.nome
      # diferença de tempo não pode passar 
      # de milisegundos.
      precisao = timedelta(milliseconds=1)
      diferenca = abs(outro.momento - self.momento)
      tempo_bate = diferenca < precisao
      if __debug__:
         print(diferenca)
         print(precisao)
         assert (not tempo_bate)
      return link_bate and nome_bate
   ...

   def serializa(self):
      # total de bytes da string, e a string.
      bytestr = bytes(self.nome, encoding="latin1")
      quanto = len(bytestr)
      _bytes = Array('B', quanto.to_bytes(1, byteorder="big"))
      _bytes.extend(bytestr)

      # o mesmo que acima, apesar de serem quantias
      # distintas. Provavelmente, o tamanho de bytes
      # que a string contém, exigirá no mínimo 2 bytes.
      bytestr = bytes(self.link, encoding="ascii")
      quanto = len(bytestr)
      _bytes.extend(quanto.to_bytes(2, byteorder="big"))
      _bytes.extend(bytestr)
      
      # total de bytes e os bytes, novamente.
      bytestr = bytes(self.versao, encoding="ascii")
      tamanho = len(bytestr)
      _bytes.extend(tamanho.to_bytes(1, byteorder="big"))
      _bytes.extend(bytestr)

      # mais 8 bytes.
      _bytes.extend(self.momento.serializa())

      # array com todos bytes retornadas.
      return _bytes
   ...

   def deserializa(_bytes):
      # primeiro o nome:
      t = int.from_bytes(_bytes[0:1], byteorder="big")
      nome = bytes_to_string(_bytes[0:t])
      # o link:
      t = int.from_bytes(_bytes[0:2], byteorder="big")
      endereco = bytes_to_string(_bytes[0:t])
      # a versão:
      t = int.from_bytes(_bytes[0:1], byteorder="big")
      versao = bytes_to_string(_bytes[0:t])
      # o selo de tempo.
      selo = datetime.deserializa(_bytes[0:8])

      return Download(nome, endereco, versao, selo)
   ...

   def __hash__(self):
      a = sum(ord(_char) for _char in self.nome)
      b = sum(ord(_char) for _char in self.link)
      c = sum(ord(digit) for digit in self.versao)
      return a + b + c
   ...

   def __str__(self):
      return """
      \rnome = "{}"
      \rendereço = '{}'
      \rversão = "{}"
      \rselo = '{}'
      \r--- --- Download ({id_}) --- ---
      """.format(
         self.nome,
         self.link,
         self.versao,
         self.momento,
         id_ = hash(self.__hash__())
      )
   ...
...

import unittest
from time import sleep

class SerializacaoDT(unittest.TestCase):
   def igualdade_intacta (self):
      a = datetime.today()
      sleep(3.11)
      b = datetime.today()
      A = a.serializa()
      B = b.serializa()
      sleep(9.29)
      # verificando uma diferença mínima
      # nada mais que 1 mero milisegundo.
      desvio = abs(a - datetime.deserializa(A))
      milisegundo = timedelta(milliseconds=1)
      self.assertLessEqual(desvio, milisegundo)
   ...

   def igualdade_download(self):
      d = Download(
         "Utilitários", 
         "htttps://www.meulink.com", 
         "1.3.6", None
      )
      e = Download(
         "Utilitarios", 
         "htttps://www.meulinkpython.com", 
         "4.2.0", None
      )
      # para bytes ...
      D = d.serializa()
      E = e.serializa()
      # de bytes ...
      e1 = Download.deserializa(E)
      d1 = Download.deserializa(D)

      print(e1, e,'\n', d, d1)

      self.assertEqual(e, e1)
      self.assertEqual(d, d1)
   ...

...

if __name__ == "__main__":
   unittest.main(verbosity=2)
...
