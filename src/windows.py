"""
Funções do diretório que tem funções especiais para fazer compatível com
o sistema operacional da Microsoft.
"""
import platform
from time import (sleep, time)
from pathlib import (WindowsPath, Path)

#o que será exportado:
__all__ = [
   "esta_no_diretorio_raiz", 
   "pausa_para_visualizacao"
]

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
   # tempo total de quanto ela durará.
   PAUSA = 5.4

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
