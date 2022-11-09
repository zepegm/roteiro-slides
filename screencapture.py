import numpy as np
import cv2
from mss import mss
import screeninfo

def get_resolution():
    monitores = screeninfo.get_monitors()

    if (len(monitores) > 1):
        return {'top': 0, 'left': monitores[0].width, 'width': monitores[1].width, 'height': monitores[1].height}
    else:
        return {'top': 0, 'left': 0, 'width': monitores[0].width, 'height': monitores[0].height}

#@staticmethod
def screen():

    #print('cheguei aqui pelo menos?')
    bounding_box = get_resolution()

    sct = mss()
    sct_img = sct.grab(bounding_box)
    #print(cv2.imencode('.jpg', np.array(sct_img)).tobytes())
    return cv2.imencode('.jpg', np.array(sct_img))[1].tobytes()