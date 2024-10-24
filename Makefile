
VERSAO = viii
CAMINHO = ../versões/pacotes.$(VERSAO).tar
PYTHON = /usr/bin/python3
TESTE = cd ./src && pwd && $(PYTHON) -m unittest

testes_unitarios = simples_adicacao_e_verificacao_manual anexacao_da_parte_de_c_e_cplusplus

importa-bibliotecas:
	cp -v $(PYTHON_CODES)/python-utilitarios/bin/legivel.pyc lib/

salva:
	@echo "salvando mais um backup(não esqueça de mudar a versão) ..."
	@echo $(CAMINHO)
	tar --wildcards --exclude *pycache* -cvf $(CAMINHO) data/ src/ Makefile

$(testes_unitarios):
	#$(TESTE) repositorio.Unitarios.carregamento_agora_do_json
	#$(TESTE) repositorio.Unitarios.simples_adicao_e_verificacao_manual
	$(TESTE) repositorio.Unitarios.$@

backups:
	@ls -1 ../versões/pacotes*

clean:
	@echo "removendo todos linques simbólicos..."
	rm --force --verbose pacotes
	rm --force --verbose $(LINKS)/pacotes
	@echo "removendo pré-compilados bytecodes."
	find -name *pycache* -exec rm -rv '{}' ';'
