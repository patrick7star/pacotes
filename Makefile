
VERSAO = viii
CAMINHO = ../versões/pacotes.$(VERSAO).tar
PYTHON = /usr/bin/python3
TESTE = cd ./src && pwd && $(PYTHON) -m unittest

# Coletanea de testes-unitários de cada arquivo:
testes_unitarios = simples_adicao_e_verificacao_manual \
						 anexacao_da_parte_de_c_e_cplusplus \
						 diz_se_jsons_podem_ser_atualizados \
						 nova_info_dos_pacotes_em_json \
						 obtendo_ultima_atualizacao
testes_unitarios_atualizacao = primeiro_filtro segundo_filtro \
										 verifica_se_e_hora_de_atualizar \
										 processo_de_atualizacao
testes_unitarios_obtencao = downloadEMetadados novoFazDownload \
									 novoBaixadorComMetadados \
									resolvendoParalelismoNosDownloads \
									lowLevelThreadsUse

importa-bibliotecas:
	cp -v $(PYTHON_CODES)/python-utilitarios/bin/legivel.pyc lib/

salva:
	@echo "salvando mais um backup(não esqueça de mudar a versão) ..."
	@echo $(CAMINHO)
	tar --wildcards --exclude *pycache* -cvf $(CAMINHO) data/ src/ Makefile

$(testes_unitarios):
	$(TESTE) repositorio.Unitarios.$@

$(testes_unitarios_atualizacao):
	$(TESTE) atualizacao.Unitarios.$@

$(testes_unitarios_obtencao):
	$(TESTE) obtencao.Funcoes.$@

backups:
	@ls -1 ../versões/pacotes*

clean:
	@echo "removendo todos linques simbólicos..."
	rm --force --verbose pacotes
	rm --force --verbose $(LINKS)/pacotes
	@echo "removendo pré-compilados bytecodes."
	find -name *pycache* -exec rm -rv '{}' ';'

extrai-lib:
	@tar -xf lib/externo.tar
	@echo "O tarball 'externo' foi extraído."
	@mv tree/ legivel.py arvore.py lib/
	@echo "Os arquivos despejados foram movidos prá 'lib'."
