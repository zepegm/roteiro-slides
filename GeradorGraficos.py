import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from consultaAcess import executarConsultaGeral

def salvarGrafico(lista, titulo, color, filename):

    nomes = []
    total = []

    for row in lista:
        nomes.append(row['Nome'])
        total.append(row['total'])

    plt.barh(nomes, total, color=color)
    cont = 0
    for t in total:
        plt.annotate(str(t), xy=(t + 0.02, cont + 0.2))
        cont += 1

    plt.xticks([0, lista[0]['total']])

    # A label para o eixo Y
    #plt.ylabel('Renda média')

    # A label para o eixo X
    #plt.xlabel('Quantidade de vezes')

    # O título do gráfico
    plt.title(titulo)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    #fig = plt.gcf()
    #fig.set_size_inches(18.5, 10.5)
    #plt.show()
    plt.savefig('static/images/' + filename)
    plt.close()


def salvarTudo():

    historico = os.path.expanduser('~') + r'\OneDrive - Secretaria da Educação do Estado de São Paulo\IGREJA\Historico.db'
    biblia = executarConsultaGeral(historico, 'select Nome, count(Nome) as total from evento_roteiro where evento = 1 group by Nome order by total desc limit 0, 10')
    musicas = executarConsultaGeral(historico, 'select Nome, count(Nome) as total from evento_roteiro where evento = 3 group by Nome order by total desc limit 0, 10')
    harpa = executarConsultaGeral(historico, 'select Nome, count(Nome) as total from evento_roteiro where evento = 2 group by Nome order by total desc limit 0, 10')

    salvarGrafico(musicas, 'TOP 10 - Músicas', 'green', 'topMusicas.png')
    salvarGrafico(harpa, 'TOP 10 - Harpa', 'blue', 'topHarpa.png')
    salvarGrafico(biblia, 'TOP 10 - Capítulos Bíblicos', 'orange', 'topCapitulos.png')
