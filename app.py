from email.utils import parsedate_to_datetime
import os
import csv
import locale
from io import StringIO
from unittest import result
from PDF import verificarHash
from powerpoint import ppt, pegarSlidesAbertos, pegarSlideShow, pegarIndexSlideshow, avancarIndexSlideShow, pegarTextoSlideShow, verificarCalendario, encerrarTodasApresentacoes, pegarNomeSlideShow
from consultaAcess import executarConsultaBibliaFormat, executarConsulta, executarConsultaLista, inserirListaRoteiro, executarConsultaGeral, alterarConfig, alterarConfigViewBiblia, consultarHarpaBD, alterarConfigViewMusica, inserirDadosBasico, consultarListaFiltrada
from flask import Flask, render_template, request, redirect, url_for, jsonify
# from waitress import serve
from math import ceil
from datetime import date
from GeradorGraficos import salvarTudo
from threading import Lock
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import eventlet.wsgi


# vou ver se consigo abrir certinho
app=Flask(__name__)
app.secret_key = "abc123"
app.config['SECRET_KEY'] = 'justasecretkeythatishouldputhere'
socketio = SocketIO(app)
CORS(app)
thread = None
thread_lock = Lock()

diretorio = os.path.expanduser('~') + r'\OneDrive - Secretaria da Educação do Estado de São Paulo\IGREJA'
historico = os.path.expanduser('~') + r'\OneDrive - Secretaria da Educação do Estado de São Paulo\IGREJA\Historico.db'
locale.setlocale(locale.LC_ALL, "")

def eNoturno(noturno):
    if noturno != '':
        return '2'
    else:
        return '1'

def estaVazio(valor):
    if valor == '':
        return 0
    else:
        return 1

def retornarFiltro(id, termo):
    if int(id) > 0:
        return termo + id
    else:
        return ''

def retornarFiltroInner(nome, termos, texto):
    total = 0
    for i in termos:
        total += int(i)
        
    if total > 0 or nome != '':
        return texto
    else:
        return ''

def background_thread():
    #Example of how to send server generated events to clients.
    index = 0
    while True:
        socketio.sleep(0.5)
        new_index = pegarIndexSlideshow()
        #print(new_index)
        if (index != new_index):
            index = new_index
            socketio.emit('legenda', pegarTextoSlideShow())

@app.route('/', methods=['GET', 'POST'])
def index():

    # quer dizer que desejo recarregar a lista
    if request.method == 'POST':
        lista = pegarSlidesAbertos()
        inserirListaRoteiro('Roteiro.db', lista)

    listaPPT = executarConsultaLista('Roteiro.db')
    return render_template('index.jinja', listaPPT=listaPPT, total=len(listaPPT))


@app.route('/proximoSlide', methods=['GET', 'POST'])
def proximoSlide():
    if request.method == 'POST':
        #print('got a post request!')

        if request.is_json: # application/json
            # handle your ajax request here!
            novalista = request.json
            inserirListaRoteiro('Roteiro.db', novalista)

            #return render_template('index.jinja', listaPPT=novalista)
        else: 
            # handle your form submit here!
            prs = ppt(request.form['proximaPRS'])
            prs.iniciarApresentacao()
            #return render_template('index.jinja', listaPPT=executarConsultaLista('Roteiro.db'))
    
    return redirect(url_for('index'))

@app.route('/atualizarTabela', methods=['GET', 'POST'])
def atualizarTabela():
    if request.method == 'POST':
        #print('got a post request!')

        if request.is_json: # application/json
            # handle your ajax request here!
            novalista = request.json
            inserirListaRoteiro('Roteiro.db', novalista)
            return jsonify(success=True)
        else:
            # handle your form submit here!
            print(request.form)
        
    return jsonify(sucess=False)
        
@app.route('/carregarSlideAdicional',  methods=['GET', 'POST'])
def carregarSlideAdicional():
    listaAtual = executarConsultaLista('Roteiro.db')
    slides = pegarSlidesAbertos()
    caminhos = []

    for sld in listaAtual:
        caminhos.append(sld['caminho'])

    for sld in slides:
        if not sld['caminho'] in caminhos:
            inserirListaRoteiro('Roteiro.db', sld)


    return redirect(url_for('index'))


@app.route('/abrirbiblia', methods=['GET', 'POST'])
def abrirbiblia():
    if request.method == 'POST':
        livro = request.form['livro'].replace('1', 'I').replace('2', 'II').replace('3', 'III')
        capitulo = request.form['capitulo']
        versao = request.form['versao']
        versiculo =  request.form['versiculo']

        if 'noturno' in request.form:
            noturno = r'\Modo Escuro'
            alterarConfig('Roteiro.db', 1, 'Biblia', 'Noturno')
        else:
            noturno = ''
            alterarConfig('Roteiro.db', 0, 'Biblia', 'Noturno')

        if 'rapido' in request.form:
            alterarConfig('Roteiro.db', 1, 'Biblia', 'Rapido')
        else:
            alterarConfig('Roteiro.db', 0, 'Biblia', 'Rapido')

        caminho = diretorio + noturno + r'\Bíblia' + '\\' + versao + '\\' + livro + '\\' + livro + ' - ' + '{0:03}'.format(int(capitulo)) + '.pptx'

        if os.path.isfile(caminho):
            prs = ppt(caminho)
            if 'rapido' in request.form:
                sld = prs.pegarSlideVersiculo(versiculo)
                prs.avancarApresentacao(sld)
                #prs.iniciarApresentacao()
                #prs.avancarSlideVersiculo(prs.quantidadeSlides(), versiculo)
                
            #consultaBD = executarConsulta('Biblia.db', retornarCategoria(livro), livro, capitulo, 'ver', 'livro', 'cap')
            consultaBD = executarConsultaBibliaFormat('BibliaFormat.db', livro, capitulo)
            # registrar no log
            inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), '" + livro + ' - ' + '{0:03}'.format(int(capitulo)) + ".pptx', 1, " + eNoturno(noturno) + ", '" + livro + ', cap. ' + capitulo + " - " + versao + "', 1)")
            return render_template('biblianew.jinja', status='Arquivo aberto com sucesso!', corstatus='text-primary', livro=request.form['livro'], capitulo=capitulo, versao=versao, noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Noturno'")[0], rapido=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Rapido'")[0], versiculo=versiculo, sucesso='ok', consultaBD=consultaBD)

        else:
            # registrar no log
            inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), '" + livro + ' - ' + '{0:03}'.format(int(capitulo)) + ".pptx', 1, " + eNoturno(noturno) + ", '" + livro + ', cap. ' + capitulo + " - " + versao + "', 2)")
            return render_template('biblianew.jinja', status='Esse capítulo não existe!', corstatus='text-danger', livro=request.form['livro'], capitulo=capitulo, versao=versao, noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Noturno'")[0], rapido=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Rapido'")[0], versiculo=versiculo, sucesso='', consultaBD='')

    return render_template('biblianew.jinja', status='', corstatus='', livro='', capitulo='', versao='', noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Noturno'")[0], rapido=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Rapido'")[0], versiculo='', sucesso='', consultaBD='')
    

@app.route('/abrirharpa', methods=['GET', 'POST'])
def abrirharpa():

    listahinos = []
    with open('listaharpa.csv', newline='', encoding="latin1") as csvfile:
        content = csvfile.read().replace('\\', '\\\\').replace('""', r'\"')
        spamreader = csv.reader(StringIO(content), doublequote=False, escapechar='\\', delimiter=';')
        
        for row in spamreader:
            listahinos.append(row)


    if request.method == 'POST':
        lista = request.form['numero']
        hinos = lista.split(';')
        sucesso = 0
        status = 'Você não digitou um número válido!'
        corstatus = 'text-danger'
        resultado = ''

        if 'noturno' in request.form:
            noturno = r'\Modo Escuro'
            alterarConfig('Roteiro.db', 1, 'Harpa', 'Noturno')
        else:
            noturno = ''
            alterarConfig('Roteiro.db', 0, 'Harpa', 'Noturno')

        for hino in hinos:
            if hino.isdigit():
                #print(hino)
                if int(hino) > 0 and int(hino) < 641:
                    #print(diretorio + noturno + '\\HARPA\\HINO ' + hino.zfill(3) + '.pptx')
                    prs = ppt(diretorio + noturno + '\\HARPA\\HINO ' + hino.zfill(3) + '.pptx')
                    sucesso += 1
                    resultado += hino.zfill(3) + ', '
                    # registrar no log
                    inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), 'HINO " + hino.zfill(3) + ".pptx', 2, " + eNoturno(noturno) + ", '" + executarConsulta('Musicas.db', "select Conteúdo from [Harpa] where Hino = {} and Tipo = 'Titulo'".format(hino))[0].replace("'", "''") + "', 1)")

        if sucesso == 1:
            status = 'Hino ' + resultado[0:-2] + ' aberto com sucesso!'
            corstatus = 'text-primary'
        elif sucesso > 1:
            status = 'Hinos ' + resultado[0:-2] + ' abertos com sucesso!'
            corstatus = 'text-primary' 
        return render_template('new harpa.jinja', listahinos=listahinos, status=status, corstatus=corstatus, noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Harpa' and configuration = 'Noturno'")[0])


    return render_template('new harpa.jinja', listahinos=listahinos, status='', corstatus='', noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Harpa' and configuration = 'Noturno'")[0])

@app.route('/abrirslidemusica', methods=['GET', 'POST'])
def abrirslidemusica():
    sucesso = 0

    pastas = os.listdir(diretorio + r'\Corinhos, Equipe de Louvor, etc')
    pastasEl = []

    for pasta in pastas:
        total = len(next(os.walk(diretorio + r'\Corinhos, Equipe de Louvor, etc' + '\\' + pasta))[2])
        #print(raiz + r'\Corinhos, Equipe de Louvor, etc' + '\\' + pasta)
        pastasEl.append({'nome':pasta, 'total':total, 'dir':'Corinhos, Equipe de Louvor, etc'})

    listaEL = []
    for p in pastasEl:
        files = []
        for file in os.listdir(diretorio + r'\Corinhos, Equipe de Louvor, etc' + '\\' + p['nome']):
            if not file[0:2] == '~$' and os.path.isfile(diretorio + r'\Corinhos, Equipe de Louvor, etc' + '\\' + p['nome'] + '\\' + file):
                files.append(file)
        listaEL.append(sorted(files, key=locale.strxfrm))

    pastas = os.listdir(diretorio + r'\DEPARTAMENTOS (LETRAS)')
    pastasDP = []

    for pasta in pastas:
        total = len(next(os.walk(diretorio + r'\DEPARTAMENTOS (LETRAS)' + '\\' + pasta))[2])
        #print(raiz + r'\Corinhos, Equipe de Louvor, etc' + '\\' + pasta)
        pastasDP.append({'nome':pasta, 'total':total, 'dir':'DEPARTAMENTOS (LETRAS)'})

    listaDP = []
    for p in pastasDP:
        files = []
        for file in os.listdir(diretorio + r'\DEPARTAMENTOS (LETRAS)' + '\\' + p['nome']):
            if not file[0:2] == '~$' and os.path.isfile(diretorio + r'\DEPARTAMENTOS (LETRAS)' + '\\' + p['nome'] + '\\' + file):
                files.append(file)
        listaDP.append(sorted(files, key=locale.strxfrm))     

    #print(listaEL[0])

    if request.method == 'POST' and 'checkEL' in request.form or 'checkDP' in request.form:

        if 'noturno' in request.form:
            noturno = r'\Modo Escuro'
            alterarConfig('Roteiro.db', 1, 'Musicas', 'Noturno')
        else:
            noturno = ''
            alterarConfig('Roteiro.db', 0, 'Musicas', 'Noturno')

        musicas_corinhos = request.form.getlist('checkEL')
        musicas_dep = request.form.getlist('checkDP')

        musicasAbertas = ''

        for m in musicas_corinhos:
            prs = ppt(diretorio + noturno + '\\' + m)
            sucesso += 1
            musicasAbertas += '"' + m[m.rfind('\\') + 1:-5] + '", '
            inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), '" + m[m.rfind('\\') + 1:].replace("'", "''") + "', 3, " + eNoturno(noturno) + ", '" + m[m.rfind('\\', 1, m.rfind('\\')) + 1:m.rfind('\\')] + "', 1)")

        for m in musicas_dep:
            prs = ppt(diretorio + noturno + '\\' + m)
            sucesso += 1
            musicasAbertas += '"' + m[m.rfind('\\') + 1:-5] + '", '
            inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), '" + m[m.rfind('\\') + 1:].replace("'", "''") + "', 3, " + eNoturno(noturno) + ", '" + m[m.rfind('\\', 1, m.rfind('\\')) + 1:m.rfind('\\')] + "', 1)")

        if sucesso > 1:
            status = 'Arquivos ' + musicasAbertas[:-2] + ' abertos com sucesso!'
            corstatus = 'text-primary'
        elif sucesso == 1:
            status = 'Arquivo ' + musicasAbertas[:-2] + ' aberto com sucesso!'
            corstatus = 'text-primary'
        else:
            status = 'Erro gravíssimo na hora de abrir arquivo'
            corstatus = 'text-danger'
            inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), 'ERRO GRAVE!', 3, " + eNoturno(noturno) + ", '-', 3)")


        return render_template('corinhos.jinja', listaEL=listaEL, pastasEL=pastasEl, listaDP=listaDP, pastasDP=pastasDP, corstatus=corstatus, status=status, noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Musicas' and configuration = 'Noturno'")[0])
        


    return render_template('corinhos.jinja', listaEL=listaEL, pastasEL=pastasEl, listaDP=listaDP, pastasDP=pastasDP, corstatus='', status='', noturno=executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Musicas' and configuration = 'Noturno'")[0])

@app.route('/apresentador', methods=['GET', 'POST'])
def apresentador():

    # pegar o index e recarregar tudo
    if request.method == "POST" and 'index_atual' in request.form:
        avancarIndexSlideShow(int(request.form['index_atual']))
        listaSlideShow = pegarSlideShow(False)
    else:
        listaSlideShow = pegarSlideShow(True)
    index = pegarIndexSlideshow()

    return render_template('apresentador.jinja', listaSlideShow=listaSlideShow, index=index)

@app.route('/proxPRS', methods=['GET', 'POST'])
def proxPRS():
    if request.method == "POST" and 'prs' in request.form:
        # pegar lista atual
        lista = executarConsultaLista('Roteiro.db')
        for l in lista:
            if l['check'] == 0:
                prs = ppt(l['caminho'])
                prs.iniciarApresentacao()
                l['check'] = 1
                inserirListaRoteiro('Roteiro.db', lista)
                return redirect(url_for('apresentador'))


    # não localizou nenhum novo slide para projetar, então basta encerrar o atual e voltar para o index
    encerrarTodasApresentacoes()
    return redirect(url_for('index'))

@app.route('/verificarMudanca', methods=['GET', 'POST'])
def verificarMudanca():
    
    if request.method == 'POST':
        #print('got a post request!')

        if request.is_json: # application/json
            # handle your ajax request here!
            lista = request.json
            listaAtual = executarConsultaLista('Roteiro.db')               

            if lista != listaAtual:
                valor = {'sucess':True}
            else:
                valor = {'sucess':False}

            return jsonify(valor)

@app.route('/subtitle')
def exibirLegenda():
    legenda = pegarTextoSlideShow()

    if legenda['index'] > 0:
    
        if len(legenda['texto']) > 199:
            tamanho = 30
        else:
            tamanho = 20
    else:
        tamanho = 0

    return render_template('new_subtitle.jinja', legenda=legenda['texto'], cabecalho=legenda['cabecalho'], tamanho=tamanho)

@app.route('/calendar', methods=['GET', 'POST'])
def exibirCalendario():

    if request.method == 'POST':
        if request.is_json:
            info = request.json
            prs_name = pegarNomeSlideShow()

            try:
                if info['filename'] == prs_name:
                    if info['index'] != pegarIndexSlideshow():
                        valor = {'sucess':True}
                    else:
                        valor = {'sucess':False}
                else:
                    if info['index'] != 0 or prs_name == executarConsulta('Roteiro.db', 'select * from OBS')[0]:
                        valor = {'sucess':True}
                    else:
                        valor = {'sucess':False}
            except:
                valor = {'sucess':False}

            return jsonify(valor)

    resultado = verificarCalendario()
    return render_template('calendar.jinja', resultado=resultado['resultado'], index=resultado['index'], filename=resultado['filename'])

@app.route('/newHarpa')
def abrirNewHarpa():
    listahinos = []
    with open('listaharpa.csv', newline='', encoding="latin1") as csvfile:
        content = csvfile.read().replace('\\', '\\\\').replace('""', r'\"')
        spamreader = csv.reader(StringIO(content), doublequote=False, escapechar='\\', delimiter=';')
        
        for row in spamreader:
            listahinos.append(row)

    return render_template('new harpa.jinja', listahinos=listahinos)

@app.route('/viewer', methods=['GET', 'POST'])
def receberView():
    
    if 'voltar' in request.args:
        alterarConfig('Roteiro.db', 1, 'View', 'visita')
        return redirect(url_for('receberView'))

    if 'destino' in request.args:
        # isso aqui é para as músicas
        if request.args['destino'] == 'musicas':
            alterarConfig('Roteiro.db', 3, 'View', 'visita')
            categoria = executarConsulta('Roteiro.db', 'select * from ConfigMusica')

            if request.method == 'POST':
                pesquisa = request.form['pesquisa']
                # primeiro vamos verificar o hash dos pdfs
                verificarHash()
                # agora que o banco está estabilizado, eu posso fazer a consulta
                pesquisa = '%' + str(request.form['pesquisa']).lower().replace("'", "’").replace('%', '').replace(' ', '%').replace('á','_').replace('à','_').replace('â','_').replace('ã','_').replace('é','_').replace('ê','_').replace('í','_').replace('ó','_').replace('ô','_').replace('õ','_').replace('ú','_').replace('ç','_') + '%'
                sql = "select * from MusicasPDF where texto like '" + pesquisa + "' order by arquivo, pag"
                resultados = executarConsultaGeral('Musicas.db', sql)

                if len(resultados) == 0:
                    mensagem = '<span class="text-danger">Nenhum resultado!</span>'
                elif len(resultados) == 1:
                    mensagem = '<span class="text-primary">Total de 1 resultado!</span>'
                else:
                    mensagem = '<span class="text-primary">Total de ' + str(len(resultados)) + ' resultados!</span>'

                return render_template('viewerMusicas.jinja', categoria=categoria, pesquisa=request.form['pesquisa'].replace("'", "’"), resultados=resultados, mensagem=mensagem, total=len(resultados))


            return render_template('viewerMusicas.jinja', categoria=categoria, pesquisa='', resultados=None)

        # isso aqui é para a harpa
        if request.args['destino'] == 'harpa':
            # salvar no banco o ultimo endereço de visita
            alterarConfig('Roteiro.db', 2, 'View', 'visita')

            # caso esteja sendo chamado pelo form de pesquisa
            if request.method == 'POST':
                pesquisa = '%' + str(request.form['pesquisa']).lower().replace("'", "''").replace('%', '').replace(' ', '%').replace('á','_').replace('à','_').replace('â','_').replace('ã','_').replace('é','_').replace('ê','_').replace('í','_').replace('ó','_').replace('ô','_').replace('õ','_').replace('ú','_').replace('ç','_') + '%'
                sql = "select hino, tipo, conteúdo from harpa where conteúdo like '" + pesquisa + "' group by hino order by hino, ordem"
                resultados = executarConsultaGeral('Musicas.db', sql)
                total = len(resultados)
                if total == 0:
                    mensagem = '<span class="text-danger">Nenhum resultado!</span>'
                elif total == 1:
                    mensagem = '<span class="text-primary">Total de 1 resultado!</span>'
                else:
                    mensagem = '<span class="text-primary">Total de ' + str(total) + ' resultados!</span>'

                return render_template('viewerHarpa.jinja', harpa=None, pesquisa=resultados, txtPesquisa=request.form['pesquisa'], mensagem=mensagem, total=total)


            # caso seja uma consulta padrão sem pesquisa
            pagina = int(request.args['pag'])
            if pagina == 1:
                resultHarpa = consultarHarpaBD(1, 200)
            elif pagina == 2:
                resultHarpa = consultarHarpaBD(201, 400)
            else:
                resultHarpa = consultarHarpaBD(401, 640)

            return render_template('viewerHarpa.jinja', harpa=resultHarpa, pagina=pagina, pesquisa=None, txtPesquisa='', mensagem=None, total=None)

    # ele não vai pra Bíblia caso a última págin de visita seja outra
    visita = executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'View' and configuration = 'visita'")[0]
    if visita == 2:
        return redirect(url_for('receberView', destino='harpa', pag=1))
    elif visita == 3:
        return redirect(url_for('receberView', destino='musicas'))

    # isso aqui é pra bíblia, lá encima eu dou um jeito dele redirecionar pros outros
    livro = executarConsulta('Roteiro.db', 'select configuration, valor from Config where pagina = "viewBiblia"')[0]
    capitulo = executarConsulta('Roteiro.db', 'select configuration, valor from Config where pagina = "viewBiblia"')[1]

    if request.method == 'POST':
        if 'livroBiblia' in request.form and 'capitulo' in request.form:
            livro = request.form['livroBiblia']
            capitulo = request.form['capitulo']

            if livro != 'None':
                consultaBD = executarConsultaBibliaFormat('BibliaFormat.db', livro, capitulo)
                if len(consultaBD) < 1:
                    true_cap = executarConsulta('BibliaFormat.db', 'select max(cap) from [' + livro + ']')[0]
                    return render_template('viewer.jinja', consultaBD=None, consultaPesquisa=None, txtPesquisa='', livro=livro, capitulo=true_cap, mensagem='Capítulo <strong>"' + capitulo + '"</strong> de <strong>"' + livro + '"</strong> inexistente! <br>O maior capítulo desse livro é o <strong>"' + str(true_cap) + '"</strong>', pagina=1, totalPaginas=0, total=0)
                else:
                    alterarConfigViewBiblia('Roteiro.db', capitulo, 'viewBiblia', livro)

                return render_template('viewer.jinja', consultaBD=consultaBD, consultaPesquisa=None, txtPesquisa='', livro=livro, capitulo=capitulo, mensagem=None, pagina=1)
        elif 'pesquisa' in request.form:
            pesquisa = '%' + str(request.form['pesquisa']).lower().replace('%', '').replace(' ', '%').replace('á','_').replace('à','_').replace('â','_').replace('ã','_').replace('é','_').replace('ê','_').replace('í','_').replace('ó','_').replace('ô','_').replace('õ','_').replace('ú','_').replace('ç','_') + '%'
            pagina = int(request.form['paginaInicial']) * 100 - 100
        
            # pegar no começo o total dos resultados da pesquisa
            sql = 'select (' + \
            '(select count(*) from [Pentateuco] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '") + ' + \
            '(select count(*) from [Históricos] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '") + ' + \
            '(select count(*) from [Poéticos] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '") + ' + \
            '(select count(*) from [Profetas] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '") + ' + \
            '(select count(*) from [Evangelhos & Atos] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '") + ' + \
            '(select count(*) from [Epístolas] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '") + ' + \
            '(select count(*) from [Revelação] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '")' + \
            ') as total'
            
            total = executarConsulta('Biblia.db', sql)[0]

            # agora recuperar os dados
            sql = 'select * from [Pentateuco] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '"' + \
            ' union all ' + \
            'select * from [Históricos] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '"' + \
            ' union all ' + \
            'select * from [Poéticos] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '"' + \
            ' union all ' + \
            'select * from [Profetas] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '"' + \
            ' union all ' + \
            'select * from [Evangelhos & Atos] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '"' + \
            ' union all ' + \
            'select * from [Epístolas] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa + '"' + \
            ' union all ' + \
            'select * from [Revelação] where ARC like "' + pesquisa + '" or NAA like "' + pesquisa + '" or NVI like "' + pesquisa + '" or NVT like "' + pesquisa  + '"' +  ' LIMIT ' + str(pagina) + ', 100'

            resultados = executarConsultaGeral('Biblia.db', sql)
            #total = len(resultados)
            msg = 'Resultados da pesquisa: '
            cor = 'text-secondary'
            if total == 0:
                msg = 'Resultados da pesquisa: sem resultado nenhum!'
                cor = 'text-danger'
            elif total == 1:
                msg = 'Resultados da pesquisa: 1 resultado!'
            else:
                msg = 'Resultados da pesquisa: ' + str(pagina + 1) + ' de ' + str(pagina + len(resultados)) + ' <span class="text-danger">(total de ' + str(total) + ' resultados!)</span>'
            totalPaginas = ceil(total/100)

            return render_template('viewer.jinja', consultaBD=None, consultaPesquisa=resultados, total=total, txtPesquisa=request.form['pesquisa'], msg=msg, cor=cor, livro=livro, capitulo=str(capitulo), mensagem=None, pagina=int(request.form['paginaInicial']), totalPaginas=totalPaginas)

    return render_template('viewer.jinja', consultaBD=executarConsultaBibliaFormat('BibliaFormat.db', livro, str(capitulo)), consultaPesquisa=None, txtPesquisa='' , livro=livro, capitulo=str(capitulo), mensagem=None, pagina=1)

@app.route('/abrirSlideExternamente', methods=['GET', 'POST'])
def abrirSlideExternamente():
    if request.method == 'POST':
    #print('got a post request!')

        if request.is_json: # application/json
            # handle your ajax request here!
            lista = request.json    
            
            if lista['origem'] == 'Biblia':
                noturno = executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Biblia' and configuration = 'Noturno'")[0]
                if noturno > 0:
                    modoNoturno = r'\Modo Escuro'
                else:
                    modoNoturno = ''
                
                caminho = diretorio + modoNoturno + r'\Bíblia' + '\\' + lista['versao'] + '\\' + lista['livro'] + '\\' + lista['livro'] + ' - ' + '{0:03}'.format(int(lista['capitulo'])) + '.pptx'
                # criar sql do log
                sql = "insert into log values (datetime('now', 'localtime'), '" + lista['livro'] + ' - ' + '{0:03}'.format(int(lista['capitulo'])) + ".pptx', 1, " + eNoturno(modoNoturno) + ", '" + lista['livro'] + ', cap. ' + str(lista['capitulo']) + " - " + lista['versao'] + "', 1)"
            elif lista['origem'] == 'Harpa':
                noturno = executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Harpa' and configuration = 'Noturno'")[0]
                if noturno > 0:
                    modoNoturno = r'\Modo Escuro'
                else:
                    modoNoturno = ''

                caminho = diretorio + modoNoturno + r'\HARPA' + r'\HINO ' + lista['hino'] + '.pptx'
                # criar sql do log
                sql = "insert into log values (datetime('now', 'localtime'), 'HINO " + lista['hino'] + ".pptx', 2, " + eNoturno(modoNoturno) + ", '" + executarConsulta('Musicas.db', "select Conteúdo from [Harpa] where Hino = {} and Tipo = 'Titulo'".format(lista['hino']))[0].replace("'", "''") + "', 1)"


            if os.path.isfile(caminho):
                try:
                    prs = ppt(caminho)
                    valor = {'sucess':True}
                    # gravar no log
                    inserirDadosBasico(historico, sql)
                except:
                    valor = {'sucess':False}
                    inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), 'ERRO GRAVE!', 4, " + eNoturno(noturno) + ", '-', 3)")
            
            return jsonify(valor)

    
    if 'hino' in request.args:
        noturno = executarConsulta("Roteiro.db", "select valor from Config where Pagina = 'Musicas' and configuration = 'Noturno'")[0]
        if noturno > 0:
            modoNoturno = r'\Modo Escuro'
        else:
            modoNoturno = ''        

        caminho = diretorio + modoNoturno + '\\' + request.args['hino']
        
        if os.path.isfile(caminho):
            try:
                prs = ppt(caminho)
                valor = {'sucess':True}
                inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), '" + request.args['hino'][request.args['hino'].rfind('/') + 1:].replace("'", "''") + "', 3, " + eNoturno(modoNoturno) + ", '" + request.args['hino'][request.args['hino'].rfind('/', 1, request.args['hino'].rfind('/')) + 1:request.args['hino'].rfind('/')] + "', 1)")
            except:
                inserirDadosBasico(historico, "insert into log values (datetime('now', 'localtime'), 'ERRO GRAVE!', 4, " + eNoturno(modoNoturno) + ", '-', 3)")
                valor = {'sucess':False}

    return ('', 204)


@app.route('/alterarConfigExternamente', methods=['GET', 'POST'])
def alterarConfigExternamente():
    if request.method == 'POST':
    #print('got a post request!')

        if request.is_json: # application/json
            # handle your ajax request here!
            try:
                categoria = request.json  
                alterarConfigViewMusica('Roteiro.db', categoria['nome'], categoria['pdf'], categoria['id'])
                valor = {'sucess':True}  
            except:
                valor = {'sucess':False}

        return jsonify(valor) 


@app.route('/loading', methods=['GET', 'POST'])
def loading():
    return render_template('carregando.html')


@app.route('/obs', methods=['GET', 'POST'])
def obs():
    if request.method == 'POST':
        if 'filename' in request.form:
            # pegar o nome da apresentação atual
            filename = pegarNomeSlideShow()
            if filename != request.form['filename'] and filename != None:
                sql = 'update OBS set Apresentacao = "' + filename + '"'
                inserirDadosBasico('Roteiro.db', sql)
                return render_template('viewerOBS.jinja', filename=filename, txt1='Imagem de Apresentação', txt2='Legenda', txt3='../calendar')

    filename = executarConsulta('Roteiro.db', 'select * from OBS')[0]
    config = int(executarConsulta('Roteiro.db', 'select config from OBS')[0])
    if config == 0:
        return render_template('viewerOBS.jinja', filename=filename, txt1='Legenda', txt2='Imagem de Apresentação', txt3='../subtitle')
    else:
        return render_template('viewerOBS.jinja', filename=filename, txt1='Imagem de Apresentação', txt2='Legenda', txt3='../calendar')


@app.route('/alterar_config_obs', methods=['GET', 'POST'])
def alterar_config_obs():
    if request.method == 'POST':
        if request.is_json: # application/json
            config = request.json
            sql = 'update OBS set config = ' + str(config)
            inserirDadosBasico('Roteiro.db', sql)
    return ('', 204)

@app.route('/log', methods=['GET', 'POST'])
def log():
    total = executarConsulta(historico, 'select count(*) as total from log')[0]
    pagina = 1

    if request.method == 'POST':
        if 'novaPag' in request.form:
            pagina = int(request.form['novaPag'])

    log = executarConsultaGeral(historico, r"select strftime('%d/%m/%Y - %H:%M:%S', data) as data, nome, Categoria.descricao as categoria, Modo.descricao as modo, obs, Status.descricao as status_descricao, log.status from log, Categoria, Modo, Status where log.categoria = Categoria.id and log.modo = Modo.id and Status.id = log.Status order by log.data desc limit " + str(pagina * 15 - 15) + ", 15")
    return render_template('log.jinja', log=log, pagina=pagina, total=total)

@app.route('/eventos', methods=['GET', 'POST'])
def eventos():

    if 'destino' in request.args:
        destino = request.args['destino']
    else:
        destino = 'novo'

    return render_template('eventos.jinja', destino=destino)

@app.route('/novo_evento', methods=['GET', 'POST'])
def novo_evento():

    lista = None
    data = date.today()

    if request.method == 'POST':
        if request.is_json:
            evento = request.json
            # agora eu tenho todos os dados, preciso inserir no BD, começando com a inserção geral
            if evento['obs'] == '':
                obs = 'null'
            else:
                obs = '"' + evento['obs'] + '"'
            
            if evento['link'] == '':
                link = 'null'
            else:
                link = '"' + evento['link'] + '"'

            try:
                inserirDadosBasico(historico, 'insert into Roteiro values(null, "{}", {}, {}, {})'.format(evento['data'], evento['tema'], obs, link))
                # agora preciso pegar o último id
                id = executarConsulta(historico, 'select seq from sqlite_sequence where name="Roteiro"')[0]
                # inserir dados individualmente agora
                for evt in evento['lst']:
                    if evt['categoria'] == '1':
                        sql = 'insert into evento_roteiro values({}, "{}", {}, {}, null, null)'.format(id, evt['nome'], evt['categoria'], evt['subcategoria'])
                        inserirDadosBasico(historico, sql)
                    elif evt['categoria'] == '2':
                        sql = 'insert into evento_roteiro values({}, "{}", {}, null, null, {})'.format(id, evt['nome'], evt['categoria'], evt['forma'])
                        inserirDadosBasico(historico, sql)
                    else:
                        sql = 'insert into evento_roteiro values({}, "{}", {}, null, {}, {})'.format(id, evt['nome'], evt['categoria'], evt['subcategoria'], evt['forma'])
                        inserirDadosBasico(historico, sql)
                valor = {'sucess':True}
            except:
                valor = {'sucess':False}

            return jsonify(valor)

    msg = None
    if 'msg' in request.args:
        if request.args['msg'] == 'sucess':
            msg = '<span class="text-primary">Dados registrados com sucesso!</span>'
        else:
            msg = '<span class="text-danger">Erro ao cadastrar dados!</span>'

    if 'import' in request.args:
        if request.args['import'] == 'log':
            sql = "select nome, categoria from log where data like '{}%'".format(request.args['data'])
            lista = executarConsultaGeral(historico, sql)
            data = request.args['data']
        elif request.args['import'] == 'files':
            slides = pegarSlidesAbertos()
            if len(slides) > 0:
                lista = []
                for sld in slides:
                    caminho = sld['caminho'].split('\\')
                    if len(caminho) < 2:
                        caminho = sld['caminho'].split('/')
                    if 'Bíblia' in caminho:
                        categoria = 1
                    elif 'HARPA' in caminho:
                        categoria = 2
                    else:
                        categoria = 3
                    
                    lista.append({'nome':caminho[-1], 'categoria':categoria})

    temas = executarConsultaGeral(historico, 'select * from Tema')
    eventos = executarConsultaGeral(historico, 'select * from Evento')
    catBiblia = executarConsultaGeral(historico, 'select * from Subcategoria')
    catMusica = executarConsultaGeral(historico, 'select * from Departamento')
    formaMusical = executarConsultaGeral(historico, 'select * from [Forma Musical]')

    return render_template('cadastroEvento.jinja', temas=temas, data=data, lista=lista, eventos=eventos, catBiblia=catBiblia, catMusica=catMusica, formaMusical=formaMusical, msg=msg)

@app.route('/estatisticas', methods=['GET', 'POST'])
def estatisticas():
    salvarTudo()
    return render_template('estatisticas.jinja')

@app.route('/visualizar_roteiros', methods=['GET', 'POST'])
def visualizar_roteiros():

    pagina = 1
    # listas
    DIAS = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-Feira', 'Sexta-feira', 'Sábado', 'Domingo']
    datas = executarConsulta(historico, r'select max(data) as maior, min(data) as menor from Roteiro')
    temas = executarConsultaGeral(historico, 'select * from Tema')
    atividades = executarConsultaGeral(historico, 'select * from Evento')
    catBiblia = executarConsultaGeral(historico, 'select * from SubCategoria')
    departamentos = executarConsultaGeral(historico, 'select * from Departamento')
    musical = executarConsultaGeral(historico, 'select * from [Forma Musical]')

    if request.method == 'POST':
        if 'novaPag' in request.form:
            pagina = int(request.form['novaPag'])
        
        elif 'nome' in request.form:
            nome = r'%' + request.form['nome'].replace(' ', '%') + r'%'
            dataIni = request.form['datade']
            dataFim = request.form['dataate']
            tema = request.form['evento']
            evento = request.form['atividade']
            subcategoria = request.form['categoria']
            departamento = request.form['departamento']
            forma_musical = request.form['musica']
            pagina = int(request.form['novaPagPesquisa'])

            origem = {'nome':request.form['nome'], 'evento':tema, 'atividade':evento, 'categoria':subcategoria, 'departamento':departamento, 'musica':forma_musical}
            datas = [dataFim, dataIni]

            # primeiro filtrar a lista principal
            sql = r'select Roteiro.id, strftime("%d/%m/%Y", data) as data, Tema.descricao, obs, url from Roteiro, Tema ' + \
            retornarFiltroInner(request.form['nome'], [evento, subcategoria, departamento, forma_musical], 'INNER JOIN evento_roteiro as Rot on Roteiro.id = Rot.id') + \
            retornarFiltro(evento, ' and Rot.Evento = ') + retornarFiltro(subcategoria, ' and Rot.subCategoria = ') + retornarFiltro(departamento, ' and Rot.departamento = ') + retornarFiltro(forma_musical, ' and Rot.formaMusical = ') + retornarFiltroInner(request.form['nome'], [], ' and Nome like "' + nome + '"') + \
            ' where Roteiro.tema = Tema.id and Roteiro.data >= "' + dataIni + '" and Roteiro.data <= "' + dataFim + '"' + retornarFiltro(tema, ' and Tema.id = ') + retornarFiltroInner(request.form['nome'], [], ' and Rot.Nome like "' + nome + '"') + ' group by Roteiro.id order by Roteiro.data desc LIMIT ' + str(pagina * 10 - 10) + ", 10"
            lista = executarConsultaGeral(historico, sql)
            sql = 'select count(DISTINCT Roteiro.id) as total from Roteiro, Tema ' + retornarFiltroInner(request.form['nome'], [evento, subcategoria, departamento, forma_musical], 'INNER JOIN evento_roteiro as Rot on Roteiro.id = Rot.id') + retornarFiltro(evento, ' and Rot.Evento = ') + retornarFiltro(subcategoria, ' and Rot.subCategoria = ') + retornarFiltro(departamento, ' and Rot.departamento = ') + retornarFiltro(forma_musical, ' and Rot.formaMusical = ') + retornarFiltroInner(request.form['nome'], [], ' and Nome like "' + nome + '"') + \
            ' where Roteiro.tema = Tema.id and Roteiro.data >= "' + dataIni + '" and Roteiro.data <= "' + dataFim + '"' + retornarFiltro(tema, ' and Tema.id = ') + retornarFiltroInner(request.form['nome'], [], ' and Rot.Nome like "' + nome + '"')
            
            #print(sql)
            total = executarConsulta(historico, sql)[0]
            for item in lista:
                sql = 'SELECT Nome, Evento.descricao as Categoria, SubCategoria.descricao as Sub, Departamento.descricao as Dep, "Forma Musical".descricao as FM ' + \
                'FROM evento_roteiro as Rot INNER JOIN Evento ON Rot.Evento = Evento.id ' + \
                'LEFT JOIN SubCategoria ON Rot.subCategoria = SubCategoria.id ' + \
                'LEFT JOIN Departamento ON Rot.departamento = Departamento.id ' + \
                'LEFT JOIN [Forma Musical] ON Rot.formaMusical = "Forma Musical".id WHERE Rot.ID = {}'.format(item['id']) + \
                retornarFiltro(evento, ' and Rot.Evento = ') + retornarFiltro(subcategoria, ' and Rot.subCategoria = ') + retornarFiltro(departamento, ' and Rot.departamento = ') + retornarFiltro(forma_musical, ' and Rot.formaMusical = ') + ' and Nome like "' + nome + '"'
                eventos = consultarListaFiltrada(historico, sql)
                data = date(year=int(item['data'][6:]), month=int(item['data'][3:5]), day=int(item['data'][0:2]))
                item['semana'] = DIAS[data.weekday()]
                item['eventos'] = eventos
            
            return render_template('visualizarEvento.jinja', lista=lista, total=total, pagina=pagina, datas=datas, temas=temas, atividades=atividades, catBiblia=catBiblia, departamentos=departamentos, musical=musical, perPage=10, origem=origem)

    lista = executarConsultaGeral(historico, r'select Roteiro.id, strftime("%d/%m/%Y", data) as data, Tema.descricao, obs, url from Roteiro, Tema where Roteiro.tema = Tema.id order by Roteiro.data desc LIMIT ' + str(pagina * 5 - 5) + ", 5")
    total = executarConsulta(historico, 'select count(*) as total from Roteiro')[0]
    for item in lista:
        sql = 'SELECT Nome, Evento.descricao as Categoria, SubCategoria.descricao as Sub, Departamento.descricao as Dep, "Forma Musical".descricao as FM ' + \
        'FROM evento_roteiro as Rot INNER JOIN Evento ON Rot.Evento = Evento.id ' + \
        'LEFT JOIN SubCategoria ON Rot.subCategoria = SubCategoria.id ' + \
        'LEFT JOIN Departamento ON Rot.departamento = Departamento.id ' + \
        'LEFT JOIN [Forma Musical] ON Rot.formaMusical = "Forma Musical".id WHERE Rot.ID = {}'.format(item['id'])
        eventos = consultarListaFiltrada(historico, sql)
        data = date(year=int(item['data'][6:]), month=int(item['data'][3:5]), day=int(item['data'][0:2]))
        item['semana'] = DIAS[data.weekday()]
        item['eventos'] = eventos

    origem = {'nome':'', 'evento':0, 'atividade':0, 'categoria':0, 'departamento':0, 'musica':0}
    return render_template('visualizarEvento.jinja', lista=lista, total=total, pagina=pagina, datas=datas, temas=temas, atividades=atividades, catBiblia=catBiblia, departamentos=departamentos, musical=musical, perPage=5, origem=origem)

@socketio.on('connect')
def on_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
            
    payload = dict(data='User Connected')
    emit('log', payload, broadcast=True)

if __name__ == '__main__':
    #app.run('0.0.0.0',port=80)
    #serve(app, host='0.0.0.0', port=80, threads=8)
    eventlet.wsgi.server(eventlet.listen(('', 80)), app)