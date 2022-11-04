import re
import win32com.client
import pythoncom
import os
from os.path import basename
from consultaAcess import executarConsulta, retornarCategoria
from flask import url_for

#apresentacoes = []

#for obj in app.Presentations:
    #apresentacoes.append(obj.fullName)

class ppt:
    def __init__(self, caminho):
        self.app = win32com.client.Dispatch("PowerPoint.Application", pythoncom.CoInitialize())
        self.apresentacoes = pegarSlidesAbertos()
        self.objCOM = None

        if len(self.apresentacoes) > 0:
            for prs in self.apresentacoes:
                if prs['caminho'][prs['caminho'].find('IGREJA'):] == caminho[caminho.find('IGREJA'):].replace('\\', '/'):
                    self.objCOM = self.app.Presentations(caminho)
                    break

            if self.objCOM == None:
                self.objCOM = self.app.Presentations.Open(FileName=caminho, WithWindow=1)

        else:
            self.objCOM = self.app.Presentations.Open(FileName=caminho, WithWindow=1)

        #print(self.app)

    def iniciarApresentacao(self):

        for i in range(self.app.SlideShowWindows.Count):
            self.app.SlideShowWindows(1).View.Exit()

        self.objCOM.SlideShowSettings.Run()

        #if self.app.SlideShowWindows.Count > 1:
            #self.app.SlideShowWindows(2).View.Exit
        
    def avancarApresentacao(self, slide):
        self.objCOM.SlideShowSettings.Run().View.GotoSlide(slide)

    def quantidadeSlides(self):
        qtd = self.objCOM.Slides.Count
        return qtd

    def pegarSlideVersiculo(self, pesquisa):
        for i in range(1, self.objCOM.Slides.Count + 1):
            texto = self.objCOM.Slides(i).Shapes(2).TextFrame.TextRange.Text
            posicao = texto.find(':')
            fim = texto.find(' ', posicao)
            versiculo = texto[posicao + 1:fim]
            if pesquisa == re.sub('[^0-9]', '', versiculo):
                return i

        return 1


def encerrarTodasApresentacoes():
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application", pythoncom.CoInitialize())

        for i in range(pp.SlideShowWindows.Count):
            pp.SlideShowWindows(1).View.Exit()
    except:
        print('Não existe o que encerrar! Essa mensagem nunca deveria aparecer!')


def pegarSlidesAbertos():
    apresentacoes = []
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application", pythoncom.CoInitialize())

        for obj in pp.Presentations:
            apresentacoes.append({'caminho':obj.fullName, 'nome':obj.Name[:-5], 'check':'False'})
    except:
        return apresentacoes
    return apresentacoes

def pegarSlideShow(export):
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application", pythoncom.CoInitialize())

        if pp.SlideShowWindows.Count > 0:
            dir = os.path.dirname(os.path.realpath(__file__))
            cont = 1
            listaSlides = []
            for sld in pp.SlideShowWindows(1).Presentation.Slides:
                if export:
                    sld.Export(dir + r'\static\images\Output' + r'\Slide' + str(cont) + '.jpg', 'JPG', 234, 122)
                listaSlides.append({'index':cont, 'nome':'Slide' + str(cont) + '.jpg'})
                cont += 1
            return listaSlides
    except:
        return None
    return None

def pegarIndexSlideshow():
    try:
        pp = win32com.client.GetActiveObject('PowerPoint.Application', pythoncom.CoInitialize())
        if pp.SlideShowWindows.Count > 0:
            index = pp.SlideShowWindows(1).View.Slide.SlideIndex
            return index
        else:
            return 0
    except:
        return 0

def pegarNomeSlideShow():
    try:
        pp = win32com.client.GetActiveObject('PowerPoint.Application', pythoncom.CoInitialize())
        if pp.SlideShowWindows.Count > 0:
            filename = pp.SlideShowWindows(1).Presentation.Name
            return filename
        else:
            return None
    except:
        return None

def avancarIndexSlideShow(posicao):
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application", pythoncom.CoInitialize())
        pp.SlideShowWindows(1).View.GotoSlide(posicao, False)
    except:
        pass

def pegarTextoSlideShow():   
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application", pythoncom.CoInitialize())
        if pp.SlideShowWindows.Count > 0:

            #filename = pp.SlideShowWindows(1).Presentation.Name
            fullname = pp.SlideShowWindows(1).Presentation.FullName
            index = pp.SlideShowWindows(1).View.Slide.SlideIndex

            if fullname.find('/Bíblia/') > -1:
                # bíblia... pegar texto da bíblia
                cabecalho = pp.SlideShowWindows(1).View.Slide.Shapes(2).TextFrame.TextRange.Text
                lista = cabecalho.replace('I ', 'I-').replace('II ', 'II-').split(' ')
                versao = lista[-1]

                if len(lista) == 3:
                    livro = lista[0].split(':')[0]
                    cap = '1'
                    ver =  re.sub("[^0-9]", "", lista[0].split(':')[1])
                else:
                    livro = lista[0].replace('-', ' ')
                    cap = re.sub("[^0-9]", "", lista[1].split(':')[0])
                    ver = re.sub("[^0-9]", "", lista[1].split(':')[1])

                texto = executarConsulta("BibliaFormat.db", "select " + versao + " from [" + livro + "] where cap = " + cap + " and ver = " + ver)[0]
                head = livro + ' ' + cap + ':' + ver + ' - '  + versao
                
                conteudo = {"cabecalho":head, "texto":texto, 'index':index}
                return conteudo

            else:

                if pp.SlideShowWindows(1).View.Slide.Shapes(1).HasTextFrame:
                    texto = pp.SlideShowWindows(1).View.Slide.Shapes(1).TextFrame.TextRange.Text

                    if texto == '':
                        if pp.SlideShowWindows(1).View.Slide.Shapes(2).HasTextFrame:
                            texto = pp.SlideShowWindows(1).View.Slide.Shapes(2).TextFrame.TextRange.Text

                elif pp.SlideShowWindows(1).View.Slide.Shapes(2).HasTextFrame:
                    texto = pp.SlideShowWindows(1).View.Slide.Shapes(2).TextFrame.TextRange.Text

                
                texto = texto.replace(chr(11), ' ').replace(chr(13), ' ').replace('  ', ' ')
                conteudo = {'cabecalho':'', 'texto':texto, 'index':index}               

                return conteudo
  
    except:
        conteudo = {'cabecalho':'', 'texto':'', 'index':pegarIndexSlideshow()}
        return conteudo

    conteudo = {'cabecalho':'', 'texto':'', 'index':pegarIndexSlideshow()}
    return conteudo

def verificarCalendario():
    try:
        pp = win32com.client.GetActiveObject("PowerPoint.Application", pythoncom.CoInitialize())

        if pp.SlideShowWindows.Count > 0:
            filename = pp.SlideShowWindows(1).Presentation.Name
            if filename == executarConsulta('Roteiro.db', 'select * from OBS')[0]:
                # salvar arquivo do calendário como imagem
                pp.SlideShowWindows(1).View.Slide.Export(os.path.dirname(os.path.realpath(__file__)) + r'\static\images\Output\Calendario.jpg', 'JPG')
                return {'resultado':True, 'index':pp.SlideShowWindows(1).View.Slide.SlideIndex, 'filename':filename}
            else:
                return {'resultado':False, 'index':0, 'filename':None}
        else:
            return {'resultado':False, 'index':0, 'filename':None}
    except:
        return {'resultado':False, 'index':0, 'filename':None}

#prs = ppt(r'C:\Users\Giuseppe\Desktop\IGREJA\00 - Versões Widescreen\Corinhos, Equipe de Louvor, etc\Avulsos\Casa de oração.pptx')
#prs.iniciarApresentacao()