import c4d

def main():
    
    doc = c4d.documents.GetActiveDocument()
    
    objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_NONE)
         
    TD = doc.GetTakeData()
    main_take = TD.GetMainTake()
    
    # Create Take
    for obj in objs:
        new_take = TD.AddTake(obj.GetName(), main_take, None)
        new_take.FindOrAddOverrideParam(TD, obj, c4d.ID_BASEOBJECT_VISIBILITY_EDITOR, 0, 1)
        new_take.FindOrAddOverrideParam(TD, obj, c4d.ID_BASEOBJECT_VISIBILITY_RENDER, 0, 1)
        
    
    c4d.EventAdd()

if __name__ == '__main__':
    main()
