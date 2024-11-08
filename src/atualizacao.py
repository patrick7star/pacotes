"""
  Nova atualização que usa do JSON para verificar os repositórios.
"""
# O que será exportado?
__all__ = ["atualiza_historico"]

# Referentes aos outros módulos deste projeto:
from repositorio import (
   CAMINHO_HISTORICO, LEITURA, ultima_atualizacao_realizada, 
   adiciona_novo_registro, CAMINHO_JSON_DATA, ESCRITA, RECUO
)
from obtencao import (baixa_com_metadados, LinqueError)
# Biblioteca padrão do Python:
from datetime import (datetime as DateTime, timedelta as Duration)
from collections.abc import (Mapping, Iterator, Sequence)
from copy import (deepcopy, )
from unittest import (TestCase, )
from json import (load, loads, dump)
from shutil import (rmtree)
# Bibliotecas externas:
from legivel import (HORA, tempo as tempo_legivel)


def filtro_das_mais_recentes(grade: dict) -> Sequence[Mapping]:
   "Pega as tuplas da adicionadas mais recentes, com referência a 'grade'."
   checagem = {}
   indice = -1
   registro_template = {
      "nome_pacote": None, 
      "selo_de_tempo": None,
      "versão": None,
      "linguagem": None,
   }
   colecao = []

   # Marcando cada pacote, de cada linguagem, como ainda não checado.
   for lang in grade.keys():
      for package in grade[lang]:
         checagem[(package, lang)] = False
   # Percentual limite para considerar como "todos" foram checados.
   FRACAO = 1 / len(checagem)
   LIMITE = 1 - FRACAO
   # Função anônima que calcula o percentual de checagens da grade.
   percentual_checked = (
      lambda valores_verdades: (
         sum(
            map(
               # Função que adiciona uma fração de a entrada já foi checada
               # e 0 percentual caso o contrário.
               lambda V: FRACAO if V else 0, 
               valores_verdades.values()
            )
         )
      )
   )

   with open(CAMINHO_HISTORICO, LEITURA, encoding="latin1") as arquivo:
      dados = load(arquivo)
      
   # Percorrendo para trás na array até que, todos cabeçalhos da 'grade'
   # tenham sido checados, ou tenham se acabado o total de itens da 
   # array com registros:
   while (not all(checagem.values())) and abs(indice) <= len(dados):
      array = dados[indice] 
      registro = deepcopy(registro_template)
      # O três significa a posição que tal dado está na array.
      antes = DateTime.fromtimestamp(array[3])
      hoje = DateTime.today()
      # Computa quanto tempo já passou.
      decorrido = (hoje - antes).total_seconds()

      # Ignorando por hora, entradas que tem um valor de tempo não 
      # convertível. Também conta na seleção.
      try:
         decorridostr = tempo_legivel(decorrido)
      except:
         if __debug__:
            print("Selo de tempo inválido.")
         # A saltar, computa próximo índice da array de registros.
         indice -= 1
         continue

      # Alguns tem a versão, outras não. Estes últimos ficaram tal lacuna
      # em "branco"(os três traços).
      if array[2] is None:
         registro["versão"] = "---"
      else:
         registro["versão"] = "v" + array[2]

      # Tupla com a formatação do tempo decorrido legível na forma humana
      # sim, processado, e o selo de tempo filtrado do banco de dados.
      # Veja que tal string com tempo legível foi processado de forma
      # imediata na chamada desta função, se tiver passado muito tempo
      # para uso, provalvemente o chamador estará usando um valor
      # inválido. A ordem é primeiro o selo, posteriormente a string de 
      #tempo com # o valor decorrido processado. 
      #
      # Se tal dado for inútil, apenas descarte. 
      registro["selo_de_tempo"] = (antes, decorridostr) 
      registro["nome_do_pacote"] = array[0]
      # Nome da linguagem pura para compor a chave que será aplicado um
      # cálculo hash. O outro é ela formada para visualização.
      lang = array[-1]
      registro["linguagem"] = lang.capitalize()
      # Tupla como o 'nome do pacote' e a respectiva 'linguagem' dele
      # são a nova chave a calcular o hash.
      tupla_chave = (registro["nome_do_pacote"], lang)

      try:
         # Apesar de percenter ao grupo de pacotes válidos, neste caso,
         # ele já foi checado.
         if checagem[tupla_chave]:
            indice -= 1
            continue
         else:
            checagem[tupla_chave] = True
            # Também contabilizando...
            indice -= 1
            colecao.append(registro)
      except KeyError:
         # A saltar, computa próximo índice da array de registros.
         indice -= 1
         # Ignora registro inválido, então pula para o próximo.
         continue

      # Se quase a totalidade tiver sido checado, apenas abadona, já 
      # que, qualquer trabalho a mais que isso é disperdício de CPU e
      # tempo.
      if percentual_checked(checagem) >= LIMITE: 
         break
   return colecao

def momento_para_atualizacao() -> (bool, Duration):
   """
   Retorna se é já o momento de atualizar o histórico de registro, se não
   quanto tempo faltam. Caso seja hora, o tempo 'faltante' é inválido.
   """
   LIMITE = Duration(hours=3)
   decorrido = ultima_atualizacao_realizada()
   excedeu_o_limite = (decorrido > LIMITE)
   
   if excedeu_o_limite:
      faltam = LIMITE - decorrido
   else:
      faltam = None

   if __debug__:
      passado_legivel = tempo_legivel(decorrido.total_seconds())
      limite_legivel = tempo_legivel(LIMITE.total_seconds())
      print(
         "Passaram-se %s, execedeu o tempo de %s? %s"
         % (passado_legivel, limite_legivel, excedeu_o_limite)
      )
   return (excedeu_o_limite, faltam)

def registra_nova_atualizacao() -> None:
   momento = DateTime.today()

   with open(CAMINHO_JSON_DATA, LEITURA, encoding='utf-8') as file:
      data = load(file)
      # Momento instatâneo de captura da marca de tempo.
      data["última-atualização"] = momento.timestamp()
   # Verifica de a variável 'data' abandona o context-with...
   assert isinstance(data, dict)

   with open(CAMINHO_JSON_DATA, ESCRITA, encoding='utf-8') as file:
      dump(data, file, indent=RECUO, ensure_ascii=False)

def atualiza_historico(grade: Mapping):
   """
     Dado a grade de linques, realiza o download de cada, então salva
   alguns metadados deles no registro de histórico. Isso não pode ser feito
   o tempo todo, apenas uma vez, por algumas horas/ou dias.
   """
   (permissao_de_atualizacao, restante) = momento_para_atualizacao()
   todos_pacotes = [] 
   lista_de_exclusao = []
   
   # Listando todos pacotes utilizados aqui, numa tupla com o nome do pacote
   # e sua respectiva linguagem(algumas programas têm nomes iguais, porém
   # diferem na linguagem).
   for lang in grade.keys():
      for package in grade[lang]:
         tupla = (package, lang)
         todos_pacotes.append(tupla)

   if permissao_de_atualizacao:
      for (pkg, lang) in todos_pacotes:
         language = lang.capitalize()
         cabecalho = "'{pkg}'".format(pkg=pkg)
         print("\tAtualizando{:.>30}[{}]".format(cabecalho, language))

         try:
            (caminho, tempo, versao) = baixa_com_metadados(pkg, grade[lang])
            linque = grade[lang][pkg]
            # Já cria o dicionário com os devidos campos no escopo da lista
            # de argumentos.
            adiciona_novo_registro({
               "nome": pkg, "linguagem": lang, "tempo": tempo, 
               "versao": versao, "linque": linque
            })
            rmtree(caminho, ignore_errors=True)

         except LinqueError:
            print("{} está com um linque inválido.".format(cabecalho))

      registra_nova_atualizacao()
      print("A atualização foi realizada com sucesso.")
   else:
      print(
         "Foi atualizado recentemente, ainda faltam %s para a próxima"
         % tempo_legivel(restante.total_seconds())
      )
   
# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
# === === === === === === === === === === === === === === === === === === = 
from pprint import (pprint as pretty_print)

class Unitarios(TestCase):
   def setUp(self):
      from repositorio import (carrega_do_json)
      self.grade_geral  = carrega_do_json()
      self.GRADE_C      = self.grade_geral["c++"]
      self.GRADE_RUST   = self.grade_geral["rust"]
      self.GRADE_PYTHON = self.grade_geral["python"]

   def primeiro_filtro(self):
      grade = self.grade_geral

      print(
         "Resultado do primeiro filtro, referente as entradas que foram "
         + "encontradas primeiro:"
      )

      for reg in filtro_das_mais_recentes(grade):
         print('\n')
         pretty_print(reg)

   def verifica_se_e_hora_de_atualizar(self):
      self.assertTrue(
         momento_para_atualizacao()[0] or
         (not momento_para_atualizacao()[0])
      )

   def processo_de_atualizacao(self):
      atualiza_historico(self.grade_geral)
