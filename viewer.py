import cv2
import os
import sqlite3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def exibirFotos(id):
    fig = plt.gcf()
    fig.canvas.manager.set_window_title('Visualizar fotos de registro')

    diretorio = os.path.expanduser('~') + r'\OneDrive - Secretaria da Educação do Estado de São Paulo\log\hook.db'
    con = sqlite3.connect(diretorio)
    cur = con.cursor()

    rs = cur.execute(r"select id, strftime('%d/%m/%Y às %Hh%M', data) as data from registro_evento where id = " + id)
    info = cur.fetchone()
    info_data = info[1].split(' ', 1)

    rs = cur.execute('select * from fotos where id_registro = ' + str(info[0]))
    lista = rs.fetchall()

    cont = 1

    for img in lista:
        nparr = np.fromstring(img[1], np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_np = cv2.cvtColor(img_np , cv2.COLOR_BGR2RGB)        
        
        plt.subplot(2, 2, cont)
        plt.axis('off')
        try:
            plt.title(info_data[cont - 1])
        except:
            pass
        plt.imshow(img_np)
        cont += 1

    plt.show()

    cur.close()
    con.close()

#img = cv2.imread("images\\c1.png")
#img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#plt.axis('off')

#plt.subplot(2, 2, 1)
#plt.imshow(img)

#plt.subplot(2, 2, 2)
#plt.imshow(img)

#plt.subplot(2, 2, 3)
#plt.imshow(img)

#plt.subplot(2, 2, 4)
#plt.imshow(img)

#plt.show()