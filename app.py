import os
import csv
from io import StringIO
from powerpoint import ppt
from consultaAcess import retornarCategoria, executarConsulta
from flask import Flask, render_template, request, redirect, url_for, session

# vou ver se consigo abrir certinho
app=Flask(__name__)

diretorio = open('diretorio.ini', 'r', encoding='utf8').read()

def estaVazio(valor):
    if valor == '':
        return 0
    else:
        return 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/abrirbiblia', methods=['GET', 'POST'])
def abrirbiblia():
    if request.method == 'POST':
        livro = request.form['livro']
        capitulo = request.form['capitulo']
        versao = request.form['versao']
        versiculo =  request.form['versiculo']

        if 'noturno' in request.form:
            noturno = r'\Modo Escuro'
        else:
            noturno = ''

        if 'rapido' in request.form:
            rapido = '1'
        else:
            rapido = ''

        caminho = diretorio + noturno + r'\Bíblia' + '\\' + versao + '\\' + livro + '\\' + livro + ' - ' + '{0:03}'.format(int(capitulo)) + '.pptx'

        if os.path.isfile(caminho):
            prs = ppt(caminho)
            if 'rapido' in request.form:
                prs.iniciarApresentacao()
                prs.avancarSlideVersiculo(prs.quantidadeSlides(), versiculo)
                
            consultaBD = executarConsulta('Bíblia', retornarCategoria(livro), livro, capitulo, 'ver', 'livro', 'cap')
            return render_template('biblia.html', status='Arquivo aberto com sucesso!', corstatus='text-primary', livro=livro, capitulo=capitulo, versao=versao, noturno=estaVazio(noturno), rapido=estaVazio(rapido), versiculo=versiculo, sucesso='ok', consultaBD=consultaBD)

        else:
            return render_template('biblia.html', status='Esse capítulo não existe!', corstatus='text-danger', livro=livro, capitulo=capitulo, versao=versao, noturno=estaVazio(noturno), rapido=estaVazio(rapido), versiculo=versiculo, sucesso='', consultaBD='')

    return render_template('biblia.html', status='', corstatus='', livro='', capitulo='', versao='', noturno='', rapido='', versiculo='', sucesso='', consultaBD='')
    

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
        else:
            noturno = ''

        for hino in hinos:
            if hino.isdigit:
                print(hino)
                if int(hino) > 0 and int(hino) < 641:
                    print(diretorio + noturno + '\\HARPA\\HINO ' + hino.zfill(3) + '.pptx')
                    prs = ppt(diretorio + noturno + '\\HARPA\\HINO ' + hino.zfill(3) + '.pptx')
                    sucesso += 1
                    resultado += hino.zfill(3) + ', '

        if sucesso == 1:
            status = 'Hino ' + resultado[0:-2] + ' aberto com sucesso!'
            corstatus = 'text-primary'
        elif sucesso > 1:
            status = 'Hinos ' + resultado[0:-2] + ' abertos com sucesso!'
            corstatus = 'text-primary' 
        return render_template('harpa.html', listahinos=listahinos, status=status, corstatus=corstatus, noturno=estaVazio(noturno))


    return render_template('harpa.html', listahinos=listahinos, status='', corstatus='', noturno='')

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
        pasta = next(os.walk(diretorio + r'\Corinhos, Equipe de Louvor, etc' + '\\' + p['nome']))[2]
        listaEL.append(pasta)

    pastas = os.listdir(diretorio + r'\DEPARTAMENTOS (LETRAS)')
    pastasDP = []

    for pasta in pastas:
        total = len(next(os.walk(diretorio + r'\DEPARTAMENTOS (LETRAS)' + '\\' + pasta))[2])
        #print(raiz + r'\Corinhos, Equipe de Louvor, etc' + '\\' + pasta)
        pastasDP.append({'nome':pasta, 'total':total, 'dir':'DEPARTAMENTOS (LETRAS)'})

    listaDP = []
    for p in pastasDP:
        pasta = next(os.walk(diretorio + r'\DEPARTAMENTOS (LETRAS)' + '\\' + p['nome']))[2]
        listaDP.append(pasta)        

    if request.method == 'POST' and 'checkEL' in request.form or 'checkDP' in request.form:

        if 'noturno' in request.form:
            noturno = r'\Modo Escuro'
        else:
            noturno = ''

        msg = '"'
        musicas_corinhos = request.form.getlist('checkEL')
        musicas_dep = request.form.getlist('checkDP')

        musicasAbertas = ''

        for m in musicas_corinhos:
            prs = ppt(diretorio + noturno + '\\' + m)
            sucesso += 1
            musicasAbertas += '"' + m[m.rfind('\\') + 1:-5] + '", '

        for m in musicas_dep:
            prs = ppt(diretorio + noturno + '\\' + m)
            sucesso += 1
            musicasAbertas += '"' + m[m.rfind('\\') + 1:-5] + '", '

        if sucesso > 1:
            status = 'Arquivos ' + musicasAbertas[:-2] + ' abertos com sucesso!'
            corstatus = 'text-primary'
        elif sucesso == 1:
            status = 'Arquivo ' + musicasAbertas[:-2] + ' aberto com sucesso!'
            corstatus = 'text-primary'
        else:
            status = 'Erro gravíssimo na hora de abrir arquivo'
            corstatus = 'text-danger'

        return render_template('corinhos.html', listaEL=listaEL, pastasEL=pastasEl, listaDP=listaDP, pastasDP=pastasDP, corstatus=corstatus, status=status, noturno=estaVazio(noturno))
        

    return render_template('corinhos.html', listaEL=listaEL, pastasEL=pastasEl, listaDP=listaDP, pastasDP=pastasDP, corstatus='', status='', noturno='')

if __name__ == '__main__':
   app.run()