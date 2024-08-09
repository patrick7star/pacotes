
""" 
   Trazer o menu para cá, pois organiza mais o módulo principal, e também
 estes trechos, referente ao 'menu' digo.
 """

from argparse import ArgumentParser
from repositorio import carrega_do_json

__all__ = ["ARGS", "GRADE"]

# adicionando também versões minúsculas/maiúsculas para que se possa 
# digitar de qualquer ordem.
def expansao(l) -> list:
   quantia_total = len(l)

   while quantia_total > 0:
      remocao = l.pop(0)
      if remocao.lower() in "python-rust":
         l.append(remocao.capitalize())
      else:
         minuscula = remocao.lower()
         maiusculas = remocao.upper()
         l.append(minuscula)
         l.append(maiusculas)
      ...
      l.append(remocao)
      quantia_total -= 1
   ...
   return l
...

def todos_pkg_disponiveis(grid: dict) -> set:
   tudo = set([])
   for lang in grid.keys():
      tudo.add(lang)
      for pkg in grid[lang].keys():
         tudo.add(pkg)
   # fazendo todas versões possíveis.

   if __debug__: print(tudo)
   return tudo
...


menu = ArgumentParser(
   description = """
   baixa pacotes Python ou Rust, diretos do GitHub,
   extraindo-os, e até substituindo os mesmos se já
   houver diretórios e arquivos com o mesmo nome no
   diretório da operação.
   """,
   prog = "Pacotes",

   epilog = """Por uma questão de... preguiça, fiz
   tal programa que tem como objetivo facilitar
   o downlaod da mais atual versão do código, que
   sempre que terminado é subido para o GitHub. Ao
   invés de ficar entre pelo site, e indo diretamente
   no pacote toda vez, este pega tal, faz download
   e descompacta o mesmo, se no diretório onde já têm
   um, substituindo pelo mais novo.
    O modo como faz isso é seguir o link de um
   arquivo 'txt', que fica no diretório principal
   dos códigos de cada linguagem, sem tal, é impossível
   baixar tais, sequer listar-lôs.""",

   usage="%(prog)s [OPÇÃO] <NOME_DO_PKG>"
)

if __debug__: menu.print_help()

menu.add_argument(
   "--lista", type=str,
   help="lista os pacotes disponíveis em cada linguagem.",
   metavar="LANG", nargs=1, default=None,
   choices = expansao(["python", "rust"]),
)

# recarregando mapa de dados. Sim, eu sei que isso aumentará o tempo da
# inicialização do programa, porém é o meio que achei para manter tal
# compatibilidade de trazer todo este código para este módulo. Um modo 
# talvez de tirar tal sobrecarga seria enviar o carregado aqui também
# junto com a instância de menu.
GRADE = carrega_do_json()

menu.add_argument(
   "--obtem", type=str,
   help="""
   baixa um dos pacotes listados no atual diretório. Se
   não houver tal opção, então um erro será emitido. O
   primeiro argumento é a linguagem desejada, e o segundo
   é o pacote desejado.""",
   default=None, nargs=2, metavar=("LANG", "PKG"),
   choices = todos_pkg_disponiveis(GRADE)
)
menu.add_argument(
   "--atualiza", action="store_true",
   help = """atualiza todas versões/e
   última alteração dos pacotes.""",
)

# parseando os argumentos e opções ...
ARGS = menu.parse_args()

if __debug__:
   print(ARGS)
   print(ARGS.lista)
...
