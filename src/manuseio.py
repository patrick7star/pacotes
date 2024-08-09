"""
  Após baixar em determinado diretório temporário e extraído, vários destes
diretórios temporários precisam ser movidos para o diretório que executa
o programa, às vezes substituirem o atual projeto com o mesmo nome; 
entretanto, nem sempre é apenas remover e colocar no lugar, alguns
diretório binários, de certas linguagens, precisam ser mantidos, ou seja, 
remoção e alocação especial. Vários protótipos aqui cuidarão disso. Também
alterar a permissão do script principal. O objetivo de tal é mexer com
o arquivos e diretórios.

  Na verdade, o objetivo também é organizar o script principal, porque as 
funções lá ficam muito entrelaçadas, e poluem tal.
"""

from pathlib import (WindowsPath, Path)
from shutil import (rmtree, move)
from stat import (S_IRWXU, S_IXGRP, S_IXOTH)
from os.path import (isdir, abspath, basename, exists, join)
from os import (chmod, getenv)
from gerenciador import CORE_PYTHON

def alterando_permissao_do_arquivo() -> None:
   NOME_SRC = "main.py"
   # colocando permisões:
   try:
      chmod(NOME_SRC, S_IRWXU | S_IXGRP | S_IXOTH)
   except FileNotFoundError:
      if __debug__:
         print("tentando alteração por 'caminho absoluto' ...", end=' ')

      caminho = join(CORE_PYTHON, "pacotes/src", NOME_SRC)
      chmod(caminho, S_IRWXU | S_IXGRP | S_IXOTH)

      if __debug__:
         print("feito.")
   ...
...

def move_diretorio_rust(fonte: Path, destino: Path) -> None:
   """
     Trabalha específico com o movimento do conteúdo descompactado para o 
   atual diretório. Isto é preciso já que ele poder ter um diretório com o 
   mesmo nome, que então deverá ser substituído, porém com cuidado, já que,
   pode conter artefatos anteriormente compilados que devem ser mantidos.
   """

   e_um_projeto_rust = (
      # closure que verifica se diretório dado é do Rust.
      lambda caminho:
         # Existe tal caminho, é um diretório e têm um arquivo Toml do 
         # cargo para deixar claro que está trabalhando com um diretório 
         # Rust.
         caminho.exists() and caminho.is_dir()
         and caminho.joinpath("Cargo.toml").exists()
   )
   # diretório com mesmo nome do extraído no '/tmp'.
   mesmo_diretorio = Path(fonte.name)

   if mesmo_diretorio.exists() and e_um_projeto_rust(mesmo_diretorio):
      # Caso o atual existe, antes da remoção dele para substituição do
      # novo, move-se seus compilados para dentro diretório extraído.
      artefato = mesmo_diretorio.joinpath("target")
      if artefato.exists():
         print("Movendo 'target' para dentro de '{}'".format(fonte))
         move(artefato, fonte)

      print("Removendo '{}'...".format(mesmo_diretorio))
      rmtree(mesmo_diretorio, ignore_errors=True)
   ...

   if fonte.exists():
      atual_diretorio = Path.cwd()
      print("Movendo '{}' para '{}'".format(fonte, atual_diretorio))
      move(fonte, ".")
   else:
      print("Não foi possível mover, porque não está mais aqui!")
...

def move_diretorio_python(caminho, destino) -> None:
   """
     Mesmo acima, porém que para o Python. Por ser geralmente ignorada o 
   diretório com artefatos, porque também seria bem mais difícil a 
   implementação, o código é bem mais simples.
   """
   mesmo_dir = basename(caminho)
   if exists(mesmo_dir):
      print("Excluíndo '{}'...".format(abspath(mesmo_dir)), end=' ')
      rmtree(mesmo_dir)
      print("feito.")
      assert notexists(mesmo_dir)
   ...
   print("Movendo '{}' para '{}'".format(caminho, abspath(".")))
   move(caminho, ".")
...

def move_diretorio(fonte: Path, lang: str, grid: dict) -> bool:
   destino = Path(".")
   msg_de_erro = "Linguagem dada '{}' não funciona aqui(por enquanto)."

   if lang not in grid:
      raise Exception(msg_de_erro.format(lang))
      abort()
   ...

   if lang == "rust":
      move_diretorio_rust(fonte, destino)
   elif lang == "python":
      move_diretorio_python(fonte, destino)
   else:
      # Qualquer outra não trabalhada, cai aqui, entretanto, é bom criar
      # um algoritmo específico para cada caso.
      move(fonte, destino)
...
