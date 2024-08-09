#!/usr/bin/python3 -OO
"""
  Programa em sí que baixa os pacotes e arruma no atual diretório. Também
é possível selecionar o arquivo específico a extrair.
"""

# módulos deste programa(foram separados daqui por motivos de organização):
from gerenciador import ( carrega, listagem, listagemI)
from banco_de_dados import (atualiza_bd, grava_pacote_registro, gravaUR)
from obtencao import baixa_e_metadados as baixa
from repositorio import (
   aplica_transicao_para_json, 
   carrega_do_json,
   listagem_do_json
)
# Foram retirados daqui para organizarem o script principal. Como se podem
# ver, tais módulos só serve este arquivo:
from lincagem import *
from menu import ARGS
from windows import *
from manuseio import *
# biblioteca padrão do Python:
from argparse import (ArgumentParser, SUPPRESS)
from datetime import datetime as DT
from pprint import pprint
from pathlib import Path
# biblioteca externa:
from dados import arvore, GalhoTipo


def iniciar_programa() -> None:
   cria_link_simbolico()
   alterando_permissao_do_arquivo()
   GRADE = carrega_do_json()
      
   if ARGS.lista is not None:
      listagem_do_json(GRADE)

   elif ARGS.obtem is not None:
      # organizando ARGS da linha-de-comando.
      header = ARGS.obtem[1]
      lang = ARGS.obtem[0].lower()

      (caminho, tempo, versao) = baixa(header, GRADE[lang])
      # Listagem em árvore do que foi baixado:
      print(arvore(caminho, True, GalhoTipo.FINO))
      # Move o arquivo baixado, e extraído em diretório, para o atual aqui.
      # O resultado certo depende da linguagem.
      move_diretorio(Path(caminho), lang, GRADE)

   elif ARGS.atualiza:
      mapa = GRADE
      atualiza_bd (mapa)
      print ("Atualiza foi realizada!")

   else:
      print("Nenhuma opção acionada!")

   # exucação total depende da plataforma executada.
   pausa_para_visualizacao ()
...

if __name__ == "__main__":
   iniciar_programa()
