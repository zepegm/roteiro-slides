from io import StringIO
from os import listdir
from hashlib import md5
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from consultaAcess import executarConsulta, inserirDadosBasico

def calcularHash(arquivo):
    hash_md5 = md5()
    with open(arquivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def verificarHash():
    # muita calma nessa hora, primeiro eu preciso listar os arquivos, para cada arquivo será tomada uma ação
    arquivos = listdir(r'static\docs')
    for file in arquivos:
        # primeiro vou pegar o Hash do arquivo
        hash = calcularHash('static\docs\\' + file)
        # agora preciso consultar a tabela pra ver se o arquivo está lá
        try:
            hashBD = executarConsulta('Musicas.db', 'select hash from MusicasHash where arquivo = "' + file + '"')[0]
        except:
            hashBD = ''
        # se chegar nessa situação vai ter que gravar tudo
        if hashBD == None or hashBD != hash:
            # primeiro gravamos a informação 
            inserirDadosBasico('Musicas.db', 'insert into MusicasHash values("' + file + '", "' + hash + '")')
            #print('gravei tudo...')
            # bem... se eu notei que o hash está diferente, quer dizer que eu preciso atualizar o arquivo
            pdfToSQLite('Musicas.db', 'static\docs\\', file)
        

def pdfToSQLite(banco, raiz, arquivo):
    output_string = StringIO()
    corte = 0
    cont = 1
    with open(raiz + arquivo, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        inserirDadosBasico('Musicas.db', 'delete from MusicasPDF where arquivo = "' + arquivo + '"')
        for page in PDFPage.create_pages(doc):
            #print(page)
            interpreter.process_page(page)
            texto = output_string.getvalue()[corte:].replace('\n', ' ').replace('  ', ' ')
            inserirDadosBasico(banco, 'insert into MusicasPDF values("' + arquivo + '", ' + str(cont) + ', "' + texto.replace('"', '""').strip() + '")')
            corte = len(output_string.getvalue())
            cont += 1
