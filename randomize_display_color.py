import c4d
from c4d import gui
import random
# Welcome to the world of Python


def iter_hierarchy(root, callback=None):
    while root:
        
        for x in iter_hierarchy(root.GetDown(), callback):
            yield x
        
        if callback:
            yield callback(root)
        else:
            yield root
            
        root = root.GetNext()

def set_color(obj):
    objects = [c4d.Opolygon,
    c4d.Ocube,
    c4d.Oplane,
    c4d.Osphere,
    c4d.Otorus,
    c4d.Ocylinder,
    c4d.Odisc,
    c4d.Ocone,
    c4d.Ocapsule,
    c4d.Ooiltank,
    c4d.Otube,
    c4d.Opyramid,
    c4d.Oplatonic,
    c4d.Ofigure,
    5169]
    if obj.GetType() in objects:
    
        obj[c4d.ID_BASEOBJECT_USECOLOR] = 2
        obj[c4d.ID_BASEOBJECT_COLOR] = random_vector()

def random_vector():

    return c4d.Vector(random.random(), random.random(), random.random())

# Main function
def main():
    doc = c4d.documents.GetActiveDocument()
    obj = doc.GetFirstObject()
    
    for x in iter_hierarchy(obj, set_color):
        pass
    c4d.EventAdd()
# Execute main()
if __name__=='__main__':
    main()
