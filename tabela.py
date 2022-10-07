import tkinter as tk
import os
from tkinter import ttk
from consultaAcess import executarConsultaGeral
from viewer import exibirFotos

def exibirTabela():
    diretorio = os.path.expanduser('~') + r'\OneDrive - Secretaria da Educação do Estado de São Paulo\log\hook.db'

    lista = executarConsultaGeral(diretorio, r"""select id,
        strftime('%d/%m/%Y', data) as dia,
        strftime('%Hh%M', data) as hora,
        CASE strftime('%w', data)
            WHEN '0' THEN 'Domingo'
            WHEN '1' THEN 'Segunda'
            WHEN '2' THEN 'Terça'
            WHEN '3' THEN 'Quarta'
            WHEN '4' THEN 'Quinta'
            WHEN '5' THEN 'Sexta'
            WHEN '6' THEN 'Sábado'
        END semana
        from registro_evento order by data desc""")

    #linhas = len(lista)

    root = tk.Tk() 
    root.geometry('265x350')
    root.title('Lista de Capturas')

    frame = tk.Frame(root)
    frame.pack(pady=20)

    trv = ttk.Treeview(frame, selectmode ='browse')
    trv.pack(side=tk.LEFT)
    #trv.grid(row=1,column=1,padx=20,pady=20)
    trv["columns"] = ("1", "2", "3")
    trv['show'] = 'headings'
    trv['height'] = 10

    # width of columns and alignment 
    trv.column("1", width = 80, anchor ='c')
    trv.column("2", width = 60, anchor ='c')
    trv.column("3", width = 80, anchor ='c')

    # Headings  
    # respective columns
    trv.heading("1", text ="Data")
    trv.heading("2", text ="Hora")
    trv.heading("3", text ="Dia da Semana")

    sb = tk.Scrollbar(frame, orient=tk.VERTICAL)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    trv.config(yscrollcommand=sb.set)
    sb.config(command=trv.yview)

    for l in lista:
        trv.insert("", tk.END, iid=l['id'], text=l['id'], values=(l['dia'], l['hora'], l['semana']))

    def show_photos():
        id = trv.focus()
        if id != '':
            exibirFotos(id)

    tk.Button(
        root, 
        text='Mostrar Fotos', 
        command=show_photos, 
        padx=20, 
        pady=10, 
        bg='#081947', 
        fg='#fff', 
        font=('Times BOLD', 12)
        ).pack(pady=10)

    #style = ttk.Style()
    #style.theme_use("xpnative")
    #style.map("Treeview")

    root.resizable(0,0)
    root.eval('tk::PlaceWindow . center')
    root.mainloop() 

