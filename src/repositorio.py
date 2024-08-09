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
  "transforma_antigo_repositorio_em_json",
  "listagem_do_json"
]

# módulos do próprio programa:
from gerenciador import (Mapa, carrega)
from banco_de_dados import carregaUR
from dados import legivel, CORE_PYTHON 
# biblioteca padrão do Python:
from pathlib import Path, PosixPath
import json, unittest
from os import remove, stat
from io import TextIOBase
from datetime import datetime as DateTime, timedelta as Duration
from dataclasses import dataclass
from collections.abc import (Iterator, Sequence)
from time import time


# caminho compatível tanto com Windows como o Linux.
CAMINHO_JSON_DATA = Path (CORE_PYTHON, "pacotes", "data/repositorios.json")
CAMINHO_HISTORICO = PosixPath(CORE_PYTHON, "pacotes", "data/historico.json")
DADOS_CONDENSADOS_PATH = PosixPath(
   CORE_PYTHON, "pacotes/data", 
   "dados-condensados.txt"
)
# Configurações gerais:
RECUO = ' ' * 4
# Apelidos de alguns retornos:

def transforma_antigo_repositorio_em_json() -> None:
   # carrega dicionário com dados a fazer o JSON, também verifica se ele
   # tem algum dado.
   dicionario_dados = carrega()

   if len (dicionario_dados) == 0:
      REGISTRO_DE_DOWNLOADS = PosixPath(
         CORE_PYTHON, "pacotes/data" 
         "dados-condensados.txt"
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
...

def permitido_realizar_transformacoes() -> (bool, bool):
   """
     Algumas permissões de atualizações, primeiro do 'repositório' que 
   contém os linques dos 'pacotes', e o outro é do histórico de downloads
   feitos dos 'pacotes'.
   """
   from legivel import tempo, HORA, DIA

   info_do_repositorio = stat(CAMINHO_JSON_DATA)
   info_do_historico = stat(CAMINHO_HISTORICO)
   # Quanto se passou desde a última modificação destes arquivos.
   decorrido = time() - info_do_repositorio.st_mtime
   outro_decorrido = time() - info_do_historico.st_mtime
   # O 'registro de histórico' é alterado mais constantemente, então é
   # necessário que seja atualizado mais rápido:
   LIMITE_DO_HISTORICO = 6 * HORA
   # Jà o o repositório é difícil de atualizar, leva dias, semanas,
   # meses,... o que podemos fazer é colocar aqui no mínimo alguns dias
   # para comprovar a diferença.
   LIMITE_DO_REPOSITORIO = 5 * DIA

   if __debug__:
      mais_legivel = lambda t: tempo(t, arredonda=True)
      t = mais_legivel(decorrido)
      T = mais_legivel(outro_decorrido)

      print("atualização do repositório: %s" % t )
      print("atualização do histórico: %s" % T)

      d = LIMITE_DO_REPOSITORIO - decorrido
      D = LIMITE_DO_HISTORICO - outro_decorrido
      # corrigindo para evitar erros:
      D = 0 if D < 0 else D
      d = 0 if d < 0 else d

      print ("D={}".format(D))
      print(
         "quanto faltam para atingir: {}({}) e {}({})"
         .format(t, mais_legivel(d), T, mais_legivel(D))
      )
   ...

   return (
      decorrido > LIMITE_DO_REPOSITORIO, 
      outro_decorrido > LIMITE_DO_HISTORICO
   )
...

def aplica_transicao_para_json() -> None:
   saida = permitido_realizar_transformacoes()
   (repository_allowed, history_allowed) = saida

   try:
      transforma_antigo_repositorio_em_json()
   except FileExistsError:
      print("Já existe tal repositório em JSON.")
      if repository_allowed:
         print("removendo '{} ...'".format(CAMINHO_JSON_DATA))
         remove(CAMINHO_JSON_DATA)
         transforma_antigo_repositorio_em_json()
      ...
   ...

   try:
      transforma_historico_em_json()
   except FileExistsError:
      print("Já existe tal repositório em JSON.")
      if history_allowed:
         print("removendo '{} ...'".format(CAMINHO_HISTORICO))
         remove(CAMINHO_HISTORICO)
         transforma_historico_em_json()
   ...
...

def carrega_do_json() -> Mapa:
   """
     O mesmo resultado do carregamento dos links do antigo repositórios,
   porém agora no novo.
   """
   caminho = str(CAMINHO_JSON_DATA)
   stream = open(caminho, "rt", encoding="utf8")
   mapa = json.load(stream)
   # Excluindo 'selo de tempo' ...
   del mapa["última-atualização"]
   return mapa
...

def ultima_atualicao_realizada() -> Duration:
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
   assert (CAMINHO_HISTORICO.exists())
   assert (
      ("nome" in n) and ("linque" and n) and 
      ("linguagem" in n) and ("versao" in n) and
      ("tempo" in n) and (isinstance(n["tempo"], DateTime))
   )

   with open(CAMINHO_HISTORICO,"rt", encoding='latin1') as arquivo:
      decorrido = DateTime.today() - n["tempo"]
      if __debug__:
         print(
            "visualizando tempo em decimal: {}"
            .format(decorrido.total_seconds())
         )
      ...
      array = [
         # Nome, linque e a versão:
         n["nome"], n["linque"], n["versao"], 
         # Marca-de-tempo e a linguagem:
         decorrido.total_seconds(), n["linguagem"]
      ]
      # A ordem dos dados extraídos são o seguinte: nome, linque, versão,
      # marca-de-tempo(decimal) e linguagem.
      historico_array = json.load(arquivo)

      assert (isinstance(historico_array, list))
      if __debug__:
         quantia_antes = len(historico_array)

      # Serializa o novo, e a põe no final da array.
      historico_array.append(array)

      if __debug__:
         quantia_depois = len(historico_array)
         print(
            "Quantia antes/depois da inserção: %d/%d" 
            % (quantia_antes, quantia_depois)
         )
         n = quantia_depois - 1
         print("Último item: {}".format(historico_array[n]))
         assert (quantia_depois == quantia_antes + 1)
      ...

      assert (all(isinstance(h, list) for h in historico_array))
      json.dump(historico_array, arquivo, indent=RECUO, ensure_ascii=False)
   ...
...

def listagem_do_json(grid: dict) -> None:
   print("\nTodo conteúdo que pode ser baixado:")
   RECUO = " " * 3
   EXCECOES = {"c_e_cplusplus": "C/C++"}

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


#  Testes unitários de funções mesmo que sejam auxiliares; classes e seus 
# métodos acima; até mesmo utilitários da linguagem ou de alguma biblioteca.
#
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
   ...

   def carregamento_agora_do_json(self):
      M = carrega_do_json()
      print(M.keys())
      chave = "c_e_cplusplus"
      print(M[chave])
   ...

   def simples_adicao_e_verificacao_manual(self):
      novo = {
         "nome": "Exemplo Inócuo", 
         "linguagem": "c_e_cplusplus",
         "versao": "0.0.6",
         "linque": "https://www.exemploinocuo.com",
         "tempo": DateTime.today()
      }
      adiciona_novo_registro(novo)

   def obtendo_ultima_atualizacao(self):
      segs = ultima_atualicao_realizada().total_seconds()

      print("{}".format(legivel.tempo(segs)))
...
