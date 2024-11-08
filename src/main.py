#!/usr/bin/python3 -OO
"""
  Programa em sí que baixa os pacotes e arruma no atual diretório. Também
é possível selecionar o arquivo específico a extrair.
"""

# módulos deste programa(foram separados daqui por motivos de organização):
from gerenciador import (listagem, listagemI)
from banco_de_dados import (atualiza_bd, grava_pacote_registro, gravaUR)
from obtencao import (baixa_e_metadados as baixa, baixa_com_metadados)
from repositorio import (
   aplica_transicao_para_json, 
   carrega_do_json,
   listagem_do_json,
   adiciona_novo_registro,
   listagem_info_dos_pacotes
)
from atualizacao import (atualiza_historico)
# Foram retirados daqui para organizarem o script principal. Como se podem
# ver, tais módulos só serve este arquivo:
from lincagem import *
from menu import ARGS
from windows import *
from manuseio import *
# biblioteca padrão do Python:
from pathlib import Path
# biblioteca externa:
from dados import arvore, GalhoTipo, PROG_DIR


def iniciar_programa() -> None:
   caminho_link = cria_link_simbolico()
   alterando_permissao_do_arquivo()
   aplica_transicao_para_json()
   GRADE = carrega_do_json()

   if __debug__:
      print("O linque foi criado com sucesso?", caminho_link)
      
   if ARGS.lista is not None:
      listagem_do_json(GRADE)

   elif ARGS.obtem is not None:
      # organizando ARGS da linha-de-comando.
      header = ARGS.obtem[1]
      lang = ARGS.obtem[0].lower()

      #(caminho, tempo, versao) = baixa(header, GRADE[lang])
      (caminho, tempo, versao) = baixa_com_metadados(header, GRADE[lang])
      # Adicionando metadados do pacote baixado no histórico...
      linque = GRADE[lang][header]
      metadados = {
         "nome": header, "linguagem": lang, "tempo": tempo, 
         "versao": versao, "linque": linque
      }
      adiciona_novo_registro(metadados)
      # Listagem em árvore do que foi baixado:
      print(arvore(caminho, True, GalhoTipo.FINO))
      # Move o arquivo baixado, e extraído em diretório, para o atual aqui.
      # O resultado certo depende da linguagem.
      move_diretorio(Path(caminho), lang, GRADE)

   elif ARGS.atualiza:
      atualiza_historico(GRADE)

   elif ARGS.lista_info:
      listagem_info_dos_pacotes(GRADE)

   else:
      print("Nenhuma opção acionada!")

   # exucação total depende da plataforma executada.
   pausa_para_visualizacao ()
...

if __name__ == "__main__":
   iniciar_programa()
