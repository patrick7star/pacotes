

"""
 Pega as versões de cada pacote, seja
python ou rust, à cada 5min.
"""

# biblioteca padrão:
from datetime import datetime, timedelta
from math import floor, ceil
from random import randint
from shutil import rmtree
from os.path import join as Join, exists
from sys import platform
from os import getenv, remove
# biblioteca externa:
from obtencao import baixa
from gerenciador import CORE_PYTHON as RAIZ

# o que será exportado?!
__all__ = [
   "gravaUR", "carregaUR",
   "grava_pacote_registro",
   "le_pacote_registro",
   #"carrega_AB", "grava_AB"
]

# ritmo de busca das versões.
if __debug__:
   RITIMO = timedelta(seconds=15)
else:
   RITIMO = timedelta(minutes=8)
# como é um alternativo ao existente, mudamos
# temporiariamente o redirecionamento de
# gravura/leitura.
CORE = "pacotes/data"
# nome do arquivo contendo última registro.
ULTIMO_REGISTRO = Join(RAIZ, CORE, "ultima_busca.dat")
# nome do arquivo que guarda info da última
# varredura.
(CONDENSADO_PYTHON, CONDENSADO_RUST, CONDENSADO) = (
   Join(RAIZ, CORE, "dados_condensados_python.txt"),
   Join(RAIZ, CORE, "dados_condensados_rust.txt"),
   Join(RAIZ, CORE, "dados-condensados.txt")
)


# salva e lê o último registro que foi
# realizado para qualquer operação que
# seja. É útil para dizer que passou
# minutos, horas ou dias de uma "última
# operação realizada", seja qual for.
def gravaUR(dt: datetime) -> None:
   selo = dt.timestamp()
   # parte-inteira.
   pI = floor(selo)
   # cada parte filtrada.
   (inteiro, decimal) = (pI, selo - pI)

   if __debug__:
      # talvez aceitar-se perder a presição de
      # milisegundos.
      transformacao = ceil(decimal * 10 ** 6)
      print("\nselo = %f(%0.6i)" % (selo, transformacao))
      print("inteiro=%i\tdecimal=%f\n" % (inteiro, decimal))
   ...

   # transforma o decimal em inteiro, apenas
   # para guardar seus bytes. Perde a precisão
   # de milisegundos no processo.
   decimais = int(decimal * (10 ** 6))

   # primeiro grava a parte inteira, e
   # depois a parte decimal.
   with open(ULTIMO_REGISTRO, mode="w+b") as arquivo:
      # valor em 1bi, então quatro bytes é o suficiente:
      bytes = inteiro.to_bytes(4, byteorder="big")
      arquivo.write(bytes)
      # também 4 bytes:
      bytes = decimais.to_bytes(4, byteorder="big")
      arquivo.write(bytes)
   ...
...
def carregaUR() -> datetime:
   with open(ULTIMO_REGISTRO, "r+b") as arquivo:
      # primeiro 4 bytes da parte inteira.
      string_bytes = arquivo.read(4)
      inteiro = int.from_bytes(string_bytes, byteorder="big")
      # os 4 últimos bytes da parte decimal.
      bytes = arquivo.read(4)
      decimal = int.from_bytes(bytes, byteorder="big")

      # transformando a parte decimal em...
      # bem, decimal, ora!
      decimal = decimal / (10 ** 6)

      # visualizando construção.
      if __debug__:
         print(
            """strBytes='{}'
            \rinteiro={}
            \rdecimal={}
            """
            .format(
               string_bytes,
               inteiro,
               decimal
            )
         )
      ...

      # convertendo para o tipo 'datetime'
      # novamente, já que é fácil recriar
      # o valor ejetado pela função 'timstamp'
      selo = inteiro + decimal
      return datetime.fromtimestamp(selo)
...

def inverte_iterador(iterador):
   pilha = []

   for item in iterador:
      pilha.append(item)

   while len(pilha) > 0:
      yield(pilha.pop())
...

# extrai de um arquivo com versões, que
# foram extraídas recentementes.
def ve_antigo_registro(chave):
   # vendo último update no banco.
   ultima_atualizacao = carrega()
   agora = datetime.today()
   transcorrido = agora - ultima_atualizacao

   if transcorrido < RITIMO:
      # apenas mostra tempo restante.
      print(
         "faltam {:^0.7s} para nova atualização."
         .format(str(RITIMO - transcorrido))
      )
      # repositório com última versão registrada.
      with open(CONDENSADO, "rt") as arquivo:
         for linha in inverte_iterador(arquivo):
            # se não contém "::" é inválido.
            if "::" not in linha:
               continue
            (ch, _, versao) = tuple(linha.split("::"))
            if ch == chave:
               return versao[1:].rstrip("\n")
         ...
      ...
   else:
      grava(agora)
      # delete o arquivo para uma atualização.
      print(
         "this file is empty",
         file = open(CONDENSADO, "wt")
      )
   ...

   # chave, possivelmente nova, então sem dado.
   return None;
...

# grava um registro de pacote no banco, para que
# seja facilmente acessado, sem precisar baixar
# o pacote, e extrair metadados toda vez.
def grava_pacote_registro(
linguagem: str, cabecalho: str,
link: str, versao,
ultima_alteracao: datetime) -> None:
   if linguagem not in ("python", "rust"):
      raise Exception("linguagem desconhecida")
   arquivo = open(CONDENSADO, "at", encoding="latin1")
   arquivo.write(cabecalho)
   arquivo.write("::")
   arquivo.write(link)
   arquivo.write("::")
   if versao is None:
      arquivo.write(str(versao))
   else:
      arquivo.write(versao)
   arquivo.write("::")
   tempo = str(ultima_alteracao.timestamp())
   arquivo.write(tempo)
   arquivo.write("::")
   arquivo.write(linguagem)
   arquivo.write('\n')
   arquivo.close()
...
def le_pacote_registro(linguagem: str, cabecalho: str):
   # abre arquivo específico dependendo da linguagem.
   if linguagem in ("python", "rust"):
      assert exists(CONDENSADO)
      arquivo = open(CONDENSADO, "rt", encoding="latin1")
   else:
      raise Exception("linguagem desconhecida")
   for linha in inverte_iterador(iter(arquivo)):
      # retirando quebra de linha.
      linha = linha.rstrip('\n')
      cabecalho_certo = linha.startswith(cabecalho)
      linguagem_certa = linha.endswith(linguagem)
      # respeitando ambas proposições acima:
      if cabecalho_certo and linguagem_certa:
         partes = iter(linha.split("::"))
         header = next(partes)
         link = next(partes)
         version = next(partes)
         last_change = next(partes)
         # evaluando o valor de maneira correta.
         last_change = datetime.fromtimestamp(float(last_change))
         if version == "None":
            version = None
         language = next(partes)
         # fechando arquivo caso ache.
         arquivo.close()
         return (header, link, version, last_change, language)
      ...
   ...
   arquivo.close()
   # se chegar aqui não foi achado, então não
   # é um dado válido.
...

# função para atualizar todo o banco
# de dados baseado nos repositórios.
from gerenciador import Mapa
from obtencao import baixa_e_metadados
from python_utilitarios.utilitarios import legivel

def atualiza_bd(mapa_geral: Mapa) -> None:
   # obtendo informações...
   (e_hora, decorrido, restante) = permitida()
   hoje = datetime.today()

   if (not e_hora):
      restante = int(restante)
      print(
         """
         \rúltima atualização foi feita agora pouco,
         \respere {} até à próxima.
         """.format(legivel.tempo(restante))
      )
      # abandonando tal.
      return None
   ...

   for (linguagem, dicio) in mapa_geral.items():
      print(
         "trabalhando com '{}'..."
         .format(linguagem.capitalize())
      )

      for cabecalho in dicio.keys():
         dados = baixa_e_metadados (cabecalho, dicio)
         (caminho, tempo, versao) = tuple (dados)
         link = dicio[cabecalho]
         # grava metadados do pacote no banco.
         grava_pacote_registro(
            linguagem, cabecalho,
            link, versao, tempo
         )
         decorrido = (hoje - tempo).total_seconds()
         print(
            "\t\b\b'{}', há {} processado."
            .format(cabecalho, legivel.tempo(decorrido))
         )
         rmtree(caminho)
      ...
   ...
   gravaUR(hoje)
...

LIMITE = timedelta(minutes=15)
# função verifica se já passou do 'limite'
# para permitir nova atualização do BD.
def permitida() -> (bool, float, float):
   # quando foi à última atualização feita.
   tUA = carregaUR()
   # momento agora.
   hoje = datetime.today()
   decorrido = hoje - tUA
   return (
      # se já passou do limite.
      decorrido > LIMITE,
      # quanto decorreu desde a atualização.
      decorrido.total_seconds(),
      # quanto falta, se estiver faltando, é claro.
      (LIMITE-decorrido).total_seconds() if decorrido < LIMITE else None
   )
...

# lê/grava se já houve alguma atualização em 
# segundo plano, no limite estabelecido.
def carrega_AB() -> bool:
   caminho = Join(
      RAIZ, CORE, 
      "atualizacao-background.dat"
   )
   try:
      with open(caminho, "rb") as arquivo:
         conteudo = arquivo.read(1)
         if conteudo == 0:
            return False
         elif conteudo == 255:
            return True
         raise Exception(
            "BD[{}] foi corrompido"
            .format(caminho)
         )
      ...
   except FileNotFoundError:
      # em caso de não existe, então nenhuma
      # atualização na frequência foi realizada.
      return True
   ...
...
def grava_AB(valor: bool) -> None:
   caminho = "data/atualizacao-background.dat"
   with open(caminho, "wb") as arquivo:
      if valor:
         arquivo.write(0xFF)
      else:
         arquivo.write(0x0)
   ...
...


from time import sleep
from unittest import main, TestCase
from random import randint
from pprint import pprint

class Funcoes(TestCase):
   def registroDoDatetime(self):
      atual = datetime.today()
      gravaUR(atual)
      sleep(5.0)
      atual = datetime.today()
      decorrido = atual - carregaUR()
      print(decorrido)
      self.assertEqual(decorrido.seconds, 5.0)
   ...
   @staticmethod
   def datetimeAleatorio():
      inicio = 2023
      return datetime(
         inicio + randint(0, 2),
         randint(1, 12),
         randint(1, 28)
      )
   ...
   def ioPacoteRegistro(self):
      import os.path
      grava_pacote_registro(
         "python", "Guarda-Roupa",
         "www.guardaroupa.com", None,
         Funcoes.datetimeAleatorio()
      )
      grava_pacote_registro(
         "python", "Cachorro",
         "www.cachorro.com", None,
         Funcoes.datetimeAleatorio()
      )
      grava_pacote_registro(
         "python", "Anel",
         "www.anel.com", None,
         Funcoes.datetimeAleatorio()
      )
      self.assertTrue(os.path.exists(CONDENSADO_PYTHON))
      # encurta para não ultrapassar tela.
      funcao = le_pacote_registro
      # teste com o Python primeiramente:
      (nome, link, _, _, _) = funcao("python", "Guarda-Roupa")
      self.assertEqual(link, "www.guardaroupa.com")
      self.assertEqual(nome, "Guarda-Roupa")
      (nome, link, _, _, _) = funcao("python", "Anel")
      self.assertEqual(link, "www.anel.com")
      self.assertEqual(nome, "Anel")
      (nome, link, _, _, _) = funcao("python", "Cachorro")
      self.assertEqual(link, "www.cachorro.com")
      self.assertEqual(nome, "Cachorro")
      # teste com o Rust agora:
      grava_pacote_registro(
         "rust", "Guarda-Roupa",
         "www.guardaroupaoutralinguagem.com",
         "v3.0.19",
         Funcoes.datetimeAleatorio()
      )
      grava_pacote_registro(
         "rust", "Teclado",
         "www.meuteclado.com",
         "v0.1.3",
         Funcoes.datetimeAleatorio()
      )
      grava_pacote_registro(
         "rust", "Porta",
         "www.thedoorrings.com",
         "v1.5.9",
         Funcoes.datetimeAleatorio()
      )
      (nome, link, versao, _, _) = funcao("rust", "Guarda-Roupa")
      self.assertNotEqual(link, "www.guardaroupa.com")
      self.assertEqual(link, "www.guardaroupaoutralinguagem.com")
      self.assertEqual(versao, "v3.0.19")
      del os.path
   ...
   def contaLinhasArquivo(arquivo):
      contador = 0
      for _ in arquivo:
         contador += 1
      return contador
   ...
   def atualizaBD(self):
      from gerenciador import carrega
      m = carrega()
      # total de itens.
      q = len(m["python"]) + len(m["rust"])
      with open(CONDENSADO, "rt", encoding="latin1") as arquivo:
         # total de linhas do arquivo.
         a = Funcoes.contaLinhasArquivo(arquivo)
      atualiza_bd(m)
      mensagem = "acabou de ser atualizado!!!"
      self.assertIsNone(atualiza_bd(m), msg=mensagem)
      with open(CONDENSADO, "rt", encoding="latin1") as arquivo:
         # total de linhas do arquivo, após à atualização.
         b = Funcoes.contaLinhasArquivo(arquivo)
      self.assertNotEqual(a, b)
      # contabiliza nova adição ao banco.
      self.assertEqual(b, a + q)
   ...
   def permitidoAtualizacao(self):
      tupla = permitida()
      pprint(tupla)
      (dadoI, dadoII, _) = tupla
      print(dadoI, legivel.tempo(dadoII), sep='\n')
   ...
...

if __name__ == "__main__":
   main(verbosity=0)

