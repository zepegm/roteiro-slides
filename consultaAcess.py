from queue import Empty
import sqlite3

def retornarCategoria(livro):
    if livro == 'Gênesis' or livro == 'Êxodo' or livro == 'Levítico' or livro == 'Deuteronômio' or livro == 'Números':
        return 'PENTATEUCO'
    elif livro == 'Josué' or livro == 'Juízes' or livro == 'Rute' or livro == 'I Samuel' or livro == 'II Samuel' or livro == 'I Reis' or livro == 'II Reis' or livro == 'I Crônicas' or livro == 'II Crônicas' or livro == 'Esdras' or livro == 'Neemias' or livro == 'Ester':
        return 'Históricos'
    elif livro == 'Jó' or livro == 'Salmos' or livro == 'Provérbios' or livro == 'Eclesiastes' or livro == 'Cantares':
        return 'Poéticos'
    elif livro == 'Isaías' or livro == 'Jeremias' or livro == 'Lamentações' or livro == 'Ezequiel' or livro == 'Daniel' or livro == 'Oseias' or livro == 'Joel' or livro == 'Amós' or livro == 'Obadias' or livro == 'Jonas' or livro == 'Miqueias' or livro == 'Naum' or livro == 'Habacuque' or livro == 'Sofonias' or livro == 'Ageu' or livro == 'Zacarias' or livro == 'Malaquias':
        return 'PROFETAS'
    elif livro == 'Mateus' or livro == 'Marcos' or livro == 'Lucas' or livro == 'João' or livro == 'Atos':
        return '[Evangelhos & Atos]'
    elif livro == "Apocalipse":
        return 'Revelação'
    else:
        return 'Epístolas'

def executarConsulta(banco, sql):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    #print(sql)
    cursor.execute(sql)

    return cursor.fetchone()
    #return 'afs'

def executarConsultaBibliaFormat(banco, livro, cap):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    codigoSQL = "select * from [" + livro + "] where Cap = " + cap + " order by ver"
    #print(codigoSQL)
    cursor.execute(codigoSQL)

    return cursor.fetchall()    

def inserirListaRoteiro(banco, lista):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()

    if type(lista) == list:
        cursor.execute('DELETE FROM lista')

        for l in lista:
            codigoSQL = "INSERT INTO lista VALUES('%s', '%s', %s)" % (l['caminho'], l['nome'], l['check'])
            cursor.execute(codigoSQL)

    else:
        codigoSQL = "INSERT INTO lista VALUES('%s', '%s', %s)" % (lista['caminho'], lista['nome'], lista['check'])
        cursor.execute(codigoSQL)

    conn.commit()

def executarConsultaLista(banco):
    conn = sqlite3.connect(banco)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    codigoSQL = "SELECT * FROM lista"
    cursor.execute(codigoSQL)
    return [dict(row) for row in cursor.fetchall()]

def executarConsultaGeral(banco, sql):
    conn = sqlite3.connect(banco)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql)
    return [dict(row) for row in cursor.fetchall()]    

def alterarConfig(banco, valor, pagina, config):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    codigoSQL = "UPDATE Config set valor = " + str(valor) + " where Pagina = '" + pagina + "' and configuration = '" + config + "'"
    cursor.execute(codigoSQL)
    conn.commit()

def alterarConfigViewBiblia(banco, valor, pagina, config):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    codigoSQL = "UPDATE Config set valor = " + str(valor) + ", configuration = '" + config + "' where Pagina = '" + pagina + "'"
    cursor.execute(codigoSQL)
    conn.commit()

def alterarConfigViewMusica(banco, nome, pdf, id):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    codigoSQL = "UPDATE ConfigMusica set nome = '" + nome + "', pdf = '" + pdf + "', id = '" + id + "'"
    cursor.execute(codigoSQL)
    conn.commit()    

def inserirDadosBasico(banco, sql):
    conn = sqlite3.connect(banco)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

def consultarHarpaBD(min, max):
    conn = sqlite3.connect('Musicas.db')
    cursor = conn.cursor()
    codigoSQL = 'select hino, tipo, conteúdo from Harpa where Hino >= ' + str(min) + ' and Hino <= ' + str(max) + ' order by Hino, ordem'
    cursor.execute(codigoSQL)

    listafinal = []
    estrofes = []
    titulo = ''
    hino = ''

    for row in cursor.fetchall():

        if row[1] == "Titulo":

            if estrofes != []:
                conteudo = {'Titulo':titulo, 'Hino':hino, 'Estrofes':estrofes}
                listafinal.append(conteudo)
                estrofes = []

            titulo = row[2]
            hino = '{:03d}'.format(row[0])
        else:
            estrofes.append({'Tipo':row[1], 'Texto':row[2]})

    conteudo = {'Titulo':titulo, 'Hino':hino, 'Estrofes':estrofes}
    listafinal.append(conteudo)
    estrofes = []

    return listafinal

def consultarListaFiltrada(Banco, sql):
    conn = sqlite3.connect(Banco)
    cursor = conn.cursor()

    cursor.execute(sql)
    resultado = cursor.fetchall()
    new_list = []
    for item in resultado:
        novo = list(filter(None, item))
        new_list.append(novo)

    return new_list