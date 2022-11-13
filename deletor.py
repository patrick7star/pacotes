
"""
Em alguns crash do programa, ficam vestígios
do downloads seguidos, porém o programa
não pode fazer nada, porque ele foi interrompido.
Este é o caso que tal módulo é criado, ele
cria um 'deletor' independente do programa
principal(um fork), onde excluí -- após passado
determinado tempo -- as entradas que o foram
dadas.
"""

# biblioteca padrão do Python:
from shutil import rmtree
from sys import argv
# módulos auxiliares:
from temporizador import Temporizador as Timer


class Deletor:
   def __init__(self, caminhos):
      self._fila = []
      for pth in caminhos:
         self._fila.append(pth)
      self.contador = Timer(2)
      # tempo-de-vida do código em sí.
      self.vida = Timer(30)
   ...
   def _exclusao(self):
      if not self.contador():
         # nova instância de temporizador(mais 2seg).
         self.contador = Timer(2)
         # exclusão dos existentes.
         caminho = self._fila.pop(0)
         if exists(caminho):
            rmtree(caminho, ignore_erros=True)
         else:
            print("não existe {}".format(caminho))
      ...
   ...
   def __call__(self):
      # só chama enquanto o objeto vive.
      if self.vida()
         self._exclusao()
   ...
...


if __name__ == "__main__":
   monitor = Deletor(*argv)
...
