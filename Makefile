
VERSAO = vii
CAMINHO = ../versões/pacotes.$(VERSAO).tar
PYTHON = /usr/bin/python3
TESTE = cd ./src && pwd && $(PYTHON) -m unittest

testes: repositorio-teste

salva:
	@echo "salvando mais um backup(não esqueça de mudar a versão) ..."
	@echo $(CAMINHO)
	tar --wildcards --exclude *pycache* -cvf $(CAMINHO) data/ src/ Makefile

repositorio-teste:
	#$(TESTE) repositorio.Unitarios.carregamento_agora_do_json
	$(TESTE) repositorio.Unitarios.simples_adicao_e_verificacao_manual

backups:
	@ls -1 ../versões/pacotes*

clean:
	@echo "removendo todos linques simbólicos..."
	rm --force --verbose pacotes
	rm --force --verbose $(LINKS)/pacotes
	@echo "removendo pré-compilados bytecodes."
	find -name *pycache* -exec rm -rv '{}' ';'
