"""
  Remove os linques para que seja possível testar várias vezes, em diferentes 
modos a criação de linques referentes ao projeto.
"""

from os import (getenv, unlink)
from pathlib import (Path)


linque_no_respositorio = Path(getenv("LINKS")).joinpath("pacotes")
linque_no_projeto = Path("./pacotes")

linque_no_respositorio.unlink()
print("Excluindo '{}' ...".format(linque_no_respositorio))
print("Excluindo '{}' ...".format(linque_no_projeto))
unlink(linque_no_projeto)

assert (not linque_no_respositorio.exists())
assert (not linque_no_projeto.exists())

