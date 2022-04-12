from consultaAcess import executarConsulta

teste = executarConsulta('Roteiro.db', 'select md5("teste")')[0]

print(teste)