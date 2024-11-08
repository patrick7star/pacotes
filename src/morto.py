"""
  Decorador para indicar tais tipos de códigos como descontinuados, toda
vez que um do tipo for chamado, uma exceção será lançada, exatamente
alertando sobre isso, que o trecho do código foi desconfiado.
"""
__all__ = ["dead_code", "codigo_morto"]

class Descontinuada(Exception):
   pass

def dead_code(funcao):
   "Aponta que tal código não está sendo mais mantida."
   assert hasattr(funcao, "__name__")

   barra = '-' * 67 
   print(
      "\n{}\nTrecho de tal código '{}' não é mais mantido!\n{}"
      .format(barra, funcao.__name__, barra)
   )

   return funcao

def codigo_morto(F):
   "O mesmo que o acima, porém em português."
   dead_code(F)

from unittest import (TestCase, expectedFailure)

AMOSTRAS = ["maçã", "uva", "morango"]

def capitalizandoStrings():
   print("\nMudando 'case' apenas da primeira letra:")

   for X in AMOSTRAS:
      print('\t',X, "==>", X.capitalize())

@dead_code
def deixandoMaiusculas():
   print("\nDeixando tudo em caixa-alta:")

   for X in AMOSTRAS:
      print('\t', X, "==>", X.upper())

class TestesUnitarios(TestCase):
   def emitindo_excecao(self):
      capitalizandoStrings()
      try:
         deixandoMaiusculas()
      except Descontinuada:
         print("Foi acionada.")
         self.assertTrue(True)

   @expectedFailure
   def faz_a_funcao_falhar(self):
      self.deixandoMaiusculas()
