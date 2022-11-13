
""" serialização de dados importantes """

from datetime import datetime
from math import floor
from array import array

class Array(array):
   # não apenas indexa, mas remove os elementos
   # selecionados pelos índices.
   def __getitem__(self, intervalo):
      if type(intervalo) == slice:
         i = intervalo.start 
         f = intervalo.stop
         if intervalo.step is not None:
            if intervalo.step > 1:
               raise Exception("não são permitidos pular índices")
         ...
      ...
      consumo = array(self.typecode)
      total = f - i
      while total > 0:
         consumo.append(self.pop(i))
         total -= 1
      ...
      return consumo
   ...
...


# separa a parte inteira do "selo" da
# parte decimal.
def decompoe(dt):
   selo = dt.timestamp()
   (inteiro, decimal) = (
      int(floor(selo)),
      int((selo - floor(selo)) * (10**6))
   )
   return (inteiro, decimal)
...

# forma "selo" novamente(com alguma perda de precisão).
def forma(partes) -> datetime:
   return partes[0] + partes[1] / (10**6)

class datetime(datetime):
   # o resultado final é uma array com 
   # 8 bytes.
   def serializa(self):
      (inteiro, decimos) = decompoe(self)
      _bytes = Array('B', inteiro.to_bytes(4, byteorder="big"))
      _bytes.extend(decimos.to_bytes(4, byteorder="big"))
      return _bytes
   ...

   @staticmethod
   # pega uma array com 8 bytes e transforma-a
   # num datetime.
   def deserializa(_bytes):
      i = int.from_bytes(_bytes[0:4:1], byteorder="big")
      d = int.from_bytes(_bytes[0:4], byteorder="big")
      selo = i + (d * 10**(-6))
      return datetime.fromtimestamp(selo)
   ...
...

__all__ = ["Array", "datetime"]

if __name__ == "__main__":
   dt = datetime.today()
   print(dt.timestamp())
   print(decompoe(datetime.today()))

   print(dt.serializa())
   x = dt.serializa()
   print(datetime.deserializa(x).timestamp())
...
