"""
   O mesmo que o módulo de 'banco de dados', porém tudo será gravado num
 arquivo JSON, sem falar que terá mais metadados importantes do que o
 anterior, como 'timestamp' do último download, números de downloads,
 e etc.
"""

"""
Templates:

  "linguagem de programação:" {

    "pacote_i": {
         "link": "http://...",
         "qtd de downloads": N,
         "último download": TimeStamp,
         "versão": vX.X.X
    },

    "pacote_ii": { ... mesma coisa acima ... },
                   .
                   .
                   .
 }
"""
# o que será exportado?
__all__ = [
 "aplica_transicao_para_json", "Historico",
  "transforma_antigo_repositorio_em_json", "listagem_do_json", 
  "adiciona_novo_registro", "listagem_info_dos_pacotes", 
  "ultima_atualizacao_realizada"
  # Constantes:
  "RECUO", "LEITURA", "ESCRITA", "C_CHAVE", "CAMINHO_JSON_DATA",
  "CAMINHO_HISTORICO"
]

# módulos do próprio programa:
from gerenciador import (Mapa, carrega)
from banco_de_dados import carregaUR
from dados import (legivel, PROG_DIR)
# biblioteca padrão do Python:
from pathlib import Path, PosixPath
import json
from os import remove, stat
from io import TextIOBase
from datetime import (datetime as DateTime, timedelta as Duration)
from dataclasses import dataclass
from collections.abc import (Iterator, Sequence)
from time import time
# Bibliotecas externas:
from legivel import (tempo, HORA, DIA)

# caminho compatível tanto com Windows como o Linux.
CAMINHO_JSON_DATA = PROG_DIR.joinpath("data", "repositorios.json")
CAMINHO_HISTORICO = PROG_DIR.joinpath("data", "historico.json")
DADOS_CONDENSADOS_PATH = PROG_DIR.joinpath( "data", "dados-condensados.txt")
# Configurações gerais:
RECUO = ' ' * 4
# Apelidos de alguns retornos:
(ESCRITA, LEITURA) = ("wt", "rt")
C_CHAVE = "c++"


def transforma_antigo_repositorio_em_json() -> None:
   # carrega dicionário com dados a fazer o JSON, também verifica se ele
   # tem algum dado.
   dicionario_dados = carrega()

   if len (dicionario_dados) == 0:
      REGISTRO_DE_DOWNLOADS = PROG_DIR.joinpath(
         "data", "dados-condensados.txt"
      )
      if (not REGISTRO_DE_DOWNLOADS.exists()):
         raise FileExistsError("arquivo com registro não existe!")
   ...

   if PosixPath(CAMINHO_JSON_DATA).exists():
      raise FileExistsError("já foi feito")

   # adiciona último vez que foi feita uma atualização no JSON.
   segundos = carregaUR().timestamp()
   chave = "última-atualização"
   dicionario_dados[chave] = segundos

   # criando arquivo JSON no determinado diretório...
   arquivo_json = open (CAMINHO_JSON_DATA, "wt", encoding="utf-8")
   COUNT = 3
   json.dump (
      dicionario_dados, arquivo_json,
      indent=' ' * COUNT, sort_keys=True,
      ensure_ascii = False
   )
   arquivo_json.close()
   assert (CAMINHO_JSON_DATA.exists())

   if __debug__:
      ESPACO = "." * COUNT
      with open (CAMINHO_JSON_DATA, "rt", encoding="utf8") as arquivo:
         obj_json = json.load (arquivo)
         print(json.dumps(obj_json, indent=ESPACO, ensure_ascii=False))
         print("tipo = {}".format(type(obj_json)))
      ...
   ...
...

@dataclass(frozen=True)
class Historico(json.JSONEncoder):
   nome: str
   linque: str
   versao: str
   tempo: DateTime
   linguagem: str

   def __str__(self) -> str:
      if self.versao is None:
         return "'{}' em {}".format(self.nome, self.linguagem)
      else:
         return ("'{}'({}) em {}".format(
            self.nome, self.versao, 
            self.linguagem
         ))
   ...

   def serializa(self) -> dict[str: Sequence]:
      decimal = self.tempo.timestamp()
      return [self.nome, self.linque, self.versao, decimal, self.linguagem]
   ...
...

def extracao_do_antigo_arquivo(conteudo: str) -> Iterator[Historico]:
   SEP = '::'
   def interpleta(s: str) -> str:
      if (s == "None") or (s.startswith("None")):
         return None
      return s.strip('v')
   ...
   # função anônima que pega uma string grandona, reparte ela em baseado
   # nas suas quebras-de-linha, então reverte a ordem de todas. O retorno
   # é obviamente uma lista de tudo isso.
   divide_em_linhas = lambda s: reversed(s.split('\n'))
   str_to_datetime = lambda s: DateTime.fromtimestamp(float(s))

   return map(
      # finalmente convertendo para a estrutura de dado apropriada...
      lambda args: Historico(*args),
      map( 
         # convertendo lista recebido de forma mais legível...
         lambda tupla: (
            # nome do Registro, seu linque e, a versão:
            tupla[0], tupla[1], interpleta(tupla[2]),
            # registro que foi feito e, a linguagem utilizada:
            str_to_datetime(tupla[3]), tupla[4]
         ), 
         # separa cada elemento da linha pelo baseado no seu separador.
         # parte as linhas.
         map(
            lambda line: line.split(SEP), 
            # filtra apenas linhas válidas, ou seja, não vázias.
            filter(
               lambda linha: linha != '',
               divide_em_linhas(conteudo)
            )
         )
      )
   )
...

def transforma_historico_em_json() -> None:
   if (not DADOS_CONDENSADOS_PATH.exists()):
      if __debug__:
         print("path: '{}'".format(DADOS_CONDENSADOS_PATH))
      raise FileNotFoundError("não há um registro de downloads feitos")
   ...

   antigo_arquivo = open(DADOS_CONDENSADOS_PATH, "rt", encoding="latin1")
   conteudo = antigo_arquivo.read(None)
   antigo_arquivo.close()

   if len(conteudo) == 0:
      BytesWarning("arquivo não tem qualquer conteúdo")

   lote_em_processamento = extracao_do_antigo_arquivo(conteudo)
   lista_de_arrays = list(a.serializa() for a in  lote_em_processamento)

   if __debug__:
      print(json.dumps(lista_de_arrays, indent="..", ensure_ascii=False))
   else:
      arquivo = open(CAMINHO_HISTORICO, "wt", encoding="latin1")
      json.dump(lista_de_arrays, arquivo, indent=RECUO, ensure_ascii=False)
...

def permitido_realizar_transformacoes() -> (bool, bool):
   """
     O algoritmo de atualização segue o seguinte critério: Se tais arquivos
   existem, então verifica o tempo decorrido desde a última modificação.
   Caso não tenha sido atualizado até um período limite, então pode-se 
   permitir atualizar mesmo que o arquivo exista.
   """
   info_do_repositorio = stat(CAMINHO_JSON_DATA)
   info_do_historico = stat(CAMINHO_HISTORICO)
   # Quanto se passou desde a última modificação destes arquivos.
   decorrido_a = time() - info_do_repositorio.st_mtime
   decorrido_b = time() - info_do_historico.st_mtime
   # O 'registro de histórico' é alterado mais constantemente, então é
   # necessário que seja atualizado mais rápido:
   LIMITE_DO_HISTORICO   = 6 * HORA
   # Jà o o repositório é difícil de atualizar, leva dias, semanas,
   # meses,... o que podemos fazer é colocar aqui no mínimo alguns dias
   # para comprovar a diferença.
   LIMITE_DO_REPOSITORIO = 5 * DIA
   historico_nao_existe   = (not CAMINHO_HISTORICO.exists())
   repositorio_nao_existe = (not CAMINHO_JSON_DATA.exists())

   if __debug__:
      mais_legivel = lambda t: tempo(t, acronomo=True, arredonda=True)

      d = LIMITE_DO_REPOSITORIO - decorrido_a
      D = LIMITE_DO_HISTORICO - decorrido_b
      # corrigindo para evitar erros:
      D = 0 if D < 0 else D
      d = 0 if d < 0 else d

      print(
         """
         Quando já passou, e o máximo que precisa para atualizar:
            - histórico:   \t{} | {}
            - repositório: \t{} | {}
         """.format(
            mais_legivel(decorrido_a), 
            mais_legivel(LIMITE_DO_HISTORICO),
            mais_legivel(decorrido_b),
            mais_legivel(LIMITE_DO_REPOSITORIO)
         )
      )

   return (
      repositorio_nao_existe, 
      historico_nao_existe
   )

def aplica_transicao_para_json() -> None:
   (OKAY, FAIL) = ('\u2713', '\U00010102')
   saida = permitido_realizar_transformacoes()
   (repository_allowed, history_allowed) = saida

   if repository_allowed:
      try:
         transforma_antigo_repositorio_em_json()
         print("O respositório em JSON foi gerado com sucesso ... %s"%OKAY)
      except FileExistsError:
         print("Já existe tal repositório em JSON ... %s" % FAIL)
         print("Removeu '{}'.".format(CAMINHO_JSON_DATA))
         remove(CAMINHO_JSON_DATA)
         transforma_antigo_repositorio_em_json()

   if history_allowed:
      try:
         transforma_historico_em_json()
         print("O histórico em JSON foi gerado com sucesso ... %s" % OKAY)
      except FileExistsError:
         print("Já existe tal histórico em JSON ... %s" % FAIL)
         print("Removeu '{}'".format(CAMINHO_HISTORICO))
         remove(CAMINHO_HISTORICO)
         transforma_historico_em_json()

   # Trecho verifica se o JSON têm a chave c&cplusplus, se não tiver, então
   # adiciona uma com o único linque até o momento.
   anexa_c_repositorio()
...

def carrega_do_json() -> Mapa:
   """
     O mesmo resultado do carregamento dos links do antigo repositórios,
   porém agora no novo.
   """
   caminho = str(CAMINHO_JSON_DATA)
   stream = open(caminho, "rt", encoding="utf8")
   mapa = json.load(stream)

   stream.close()
   # Excluindo 'selo de tempo' ...
   del mapa["última-atualização"]
   return mapa
...

def ultima_atualizacao_realizada() -> Duration:
   """
     Pega a última atualização, porém não do arquivo original que fazia tal,
   e sim aquele condesado no JSON.
     É uma operação bem pesada, o parsing do JSON digo, entretanto, podemos
   reduzir isso, se necessário é claro -- não é uma operação que qualquer 
   outro trecho chama constantemente; armazenando some fetches por algums
   minutos, e sempre consutar valores dela.
   """
   caminho = str(CAMINHO_JSON_DATA)
   stream = open(caminho, "rt", encoding="utf8")
   mapa = json.load(stream)

   valor_seg = mapa["última-atualização"]
   ultima_marca = DateTime.fromtimestamp(valor_seg)
   hoje = DateTime.today()

   stream.close()
   return hoje - ultima_marca
...

def adiciona_novo_registro(n: dict) -> None:
   """
     Converte o dicionário com novo registro baixado para uma array, então
   o coloca no histórico em JSON do programa.

   Nota: É preciso que o dicionário passado tenha os seguintes campos: nome,
   linque, linguagem, versão e selo de tempo.
   """
   assert (CAMINHO_HISTORICO.exists())
   assert (
      ("nome" in n) and ("linque" and n) and 
      ("linguagem" in n) and ("versao" in n) and
      ("tempo" in n) and (isinstance(n["tempo"], DateTime))
   )

   with open(CAMINHO_HISTORICO, LEITURA, encoding='latin1') as arquivo:
      array = [
         # Nome, linque e a versão:
         n["nome"], n["linque"], n["versao"], 
         # Marca-de-tempo e a linguagem:
         n["tempo"].timestamp(), n["linguagem"]
      ]
      # A ordem dos dados extraídos são o seguinte: nome, linque, versão,
      # marca-de-tempo(decimal) e linguagem.
      historico_array = json.load(arquivo)

      assert (isinstance(historico_array, list))
      if __debug__:
         quantia_antes = len(historico_array)
         print("Array a ser incluída:\n{}".format(array))

      # Serializa o novo, e a põe no final da array.
      historico_array.append(array)

      if __debug__:
         quantia_depois = len(historico_array)
         print(
            "Quantia antes/depois da inserção: %d/%d" 
            % (quantia_antes, quantia_depois)
         )
         n = quantia_depois - 1
         print("Penúltimo item: {}".format(historico_array[n - 1]))
         print("Último item: {}".format(historico_array[n]))
         assert (quantia_depois == quantia_antes + 1)

   with open(CAMINHO_HISTORICO, ESCRITA, encoding='latin1') as arquivo:
      assert (all(isinstance(h, list) for h in historico_array))
      json.dump(historico_array, arquivo, indent=RECUO, ensure_ascii=False)

def listagem_do_json(grid: dict) -> None:
   print("\nTodo conteúdo que pode ser baixado:")
   RECUO = " " * 3
   EXCECOES = {C_CHAVE: "C/C++"}

   def reprocessar(key: str) -> str:
      if key in EXCECOES:
         return EXCECOES[key]
      else:
         return key.capitalize()
   ...

   for lang in grid.keys():
      # Reprocessamento para impressão...
      formatada = reprocessar(lang)
      print("{}{}:".format(RECUO, formatada))

      for pkg in grid[lang].keys():
         print("{}- {}".format(RECUO * 2, pkg))

      # Quebra-de-linha por linguagem...
      print("")
   ...
...

def anexa_c_repositorio() -> None:
   REPOSITORIO = [
      (
         "Utilitários em C",
         "https://github.com/patrick7star/utilitarios-em-c/archive/refs"
         + "/heads/main.zip"
      ),
      (
         "Outros Linques ...",
         "https://github.com/patrick7star/outros-linques-archive"
      )
   ]
   # Lendo e analisando o JSON dado...
   with open(CAMINHO_JSON_DATA, LEITURA, encoding="utf8") as stream:
      data = json.load(stream, parse_float=float)  
      existe_tal_chave = C_CHAVE in data
      houve_alguma_mudancao = False

      if __debug__:
         print("\nListando as chaves ...")

         for key in data.keys():
            print("\t - {}".format(key))

         print("\nHá uma chave 'C/C++'?", existe_tal_chave)

      # Se não houver tal repostório para C/C++, então colocarei um.
      if (not existe_tal_chave):
         for (nome, linque) in REPOSITORIO:
            try:
               data[C_CHAVE][nome] = linque 
            except KeyError:
               # Neste caso cria o dicionário primeiramente...
               data[C_CHAVE] = {}
               data[C_CHAVE][nome] = linque

         houve_alguma_mudancao = True

   # Escrevendo a mudança decorrida nele...
   if houve_alguma_mudancao:
      stream = open(CAMINHO_JSON_DATA, ESCRITA, encoding='utf8')
      json.dump (
         data, stream, indent=RECUO, sort_keys=True,
         ensure_ascii = False
      )
      stream.close()

      if __debug__:
         print("Dados do JSON foram atualizados com sucesso.")

def listagem_info_dos_pacotes(grade: dict) -> None:
   """
     Listagem de todos pacotes, porém com mais informação, tipo: o tempo
   da última vez que ele foi atualizado no GitHub; a linguagem que tal
   pacote é relacionado; e se houver, a versão do pacote.
   """
   checagem = {}
   indice = -1

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

   if __debug__:
      print(
         "FRAÇÃO: {:0.2f}%\tLIMITE:{:0.2f}%\nchecagem: {}"
         .format(FRACAO * 100, 100 * LIMITE, checagem)
      )

   with open(CAMINHO_HISTORICO, LEITURA, encoding="latin1") as arquivo:
      dados = json.load(arquivo)
      hoje = DateTime.today()
      
      print("\n\nListagem de todos pacotes mais detalhada:", end='\n\n')
      # Percorrendo para trás na array até que, todos cabeçalhos da 'grade'
      # tenham sido checados, ou tenham se acabado o total de itens da 
      # array com registros:
      while (not all(checagem.values())) and abs(indice) <= len(dados):
         array = dados[indice] 
         # O três significa a posição que tal dado está na array.
         antes = DateTime.fromtimestamp(array[3])
         # Computa quanto tempo já passou.
         decorrido = (hoje - antes).total_seconds()

         # Ignorando por hora, entradas que tem um valor de tempo não 
         # convertível.
         try:
            decorridostr = tempo(decorrido)
         except:
            if __debug__:
               print("Selo de tempo inválido.")
            # A saltar, computa próximo índice da array de registros.
            indice -= 1
            continue

         # Alguns tem a versão, outras não. Estes últimos ficaram tal lacuna
         # em "branco".
         if array[2] is None:
            versao = "---"
         else:
            versao = "v" + array[2]

         nome_do_pacote = array[0]
         # Nome da linguagem pura para compor a chave que será aplicado um
         # cálculo hash. O outro é ela formada para visualização.
         lang = array[-1]
         linguagem = array[-1].capitalize()
         # Tupla como o 'nome do pacote' e a respectiva 'linguagem' dele
         # são a nova chave a calcular o hash.
         tupla_chave = (nome_do_pacote, lang)

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
         except KeyError:
            # A saltar, computa próximo índice da array de registros.
            indice -= 1
            # Ignora registro inválido, então pula para o próximo.
            continue

         print(
               "{3} - {0:<30} ~ {1}\t{4:>12} | {2}".format(
            nome_do_pacote, decorridostr, linguagem, 
            RECUO, versao.center(8)
         ))

         # Se quase a totalidade tiver sido checado, apenas abadona, já 
         # que, qualquer trabalho a mais que isso é disperdício de CPU e
         # tempo.
         if percentual_checked(checagem) >= LIMITE: 
            break
      # Última quebra-de-linha para separar bem a saída de tal função de
      # demais durante a execução.
      print("")


# === === === === === === === === === === === === === === === === === === =
#                           Testes Unitários
# --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- - 
#  Testes unitários de funções mesmo que sejam auxiliares; classes e seus 
# métodos acima; até mesmo utilitários da linguagem ou de alguma biblioteca.
# === === === === === === === === === === === === === === === === === === = 
import unittest

class Unitarios (unittest.TestCase):
   def antigo_dados_para_json (self):
      transforma_antigo_repositorio_em_json()
      remove (CAMINHO_JSON_DATA)
      assert (not CAMINHO_JSON_DATA.exists())

   def extracao_do_antigo_banco(self):
      with open(DADOS_CONDENSADOS_PATH, "rt", encoding="latin1") as arq:
         conteudo = arq.read(None)
         output = extracao_do_antigo_arquivo(conteudo)
         for r in output: print(r)

   def conversao_do_historico_de_registros(self):
      transforma_historico_em_json()

   def diz_se_jsons_podem_ser_atualizados(self):
      output = permitido_realizar_transformacoes()
      repository_allowed = output[0]
      history_allowed = output[1]

      print("\nO 'repositório' será atualizado?", repository_allowed)
      print("O 'histórico' será atualizado?", history_allowed, end="\n\n")

   def carregamento_agora_do_json(self):
      M = carrega_do_json()
      print(M.keys())
      chave = "c_e_cplusplus"
      print(M[chave])

   def simples_adicao_e_verificacao_manual(self):
      novo = {
         "nome": "Exemplo Inócuo", 
         "linguagem": "c_e_cplusplus",
         "versao": "0.0.6",
         "linque": "https://www.exemploinocuo.com",
         "tempo": DateTime.today()
      }
      print(novo)
      adiciona_novo_registro(novo)

   def obtendo_ultima_atualizacao(self):
      segs = ultima_atualizacao_realizada().total_seconds()

      print("{}".format(legivel.tempo(segs)))

   @unittest.skip("Altera o repositório de forma que pode causar futuros"
   + " erros ao executar o programa.")
   def anexacao_da_parte_de_c_e_cplusplus(self):
      anexa_c_repositorio()

   def nova_info_dos_pacotes_em_json(self):
      grade = carrega_do_json()
      listagem_info_dos_pacotes(grade)
...
