import c4d
import redshift

REDSHIFT_SHADER_GRAPH_ID = 1036224

# https://redshift.maxon.net/topic/33950/changing-shader-color-via-python-in-c4d/3?_=1641410596508
def GetAllNodes(gvMaster, gvNode=None, nodes=None):

    removeGvMaster = False

    if nodes == None:
        removeGvMaster = True
        nodes = []
        gvNode = gvMaster.GetRoot()

    while gvNode:
        nodes.append(gvNode)
        GetAllNodes(gvMaster, gvNode.GetDown(), nodes)
        gvNode = gvNode.GetNext()

    # Remove GvMaster and return
    if removeGvMaster:
        return nodes[1:]
    return nodes

def CompareRedshiftMaterial(mata, matb):
    #Get the root node for the redshift node graph
    mata_master = redshift.GetRSMaterialNodeMaster(mata)
    matb_master = redshift.GetRSMaterialNodeMaster(matb)
    
    #Iterate through all the nodes and dump them in a list
    mata_nodes = GetAllNodes(mata_master)
    matb_nodes = GetAllNodes(matb_master)
    
    # if the lists aren't the same length they aren't duplicate
    if len(mata_nodes) == len(matb_nodes):
        # iterate through list a
        for idx, n in enumerate(mata_nodes):
            # compare the data basecontainer on each node, if they aren't equal return false
            if n.GetOperatorContainer()!=matb_nodes[idx].GetOperatorContainer():
                return False
        
        # if we made it through all the nodes with all of them being equal then 
        # I bet the materials are duplicated
        return True
    
    # Return false if the lengths aren't equal
    return False

def ReplaceMaterial(mata, matb, doc=None):
    if not doc:
        doc = c4d.documents.GetActiveDocument()
    
    # grab the object link
    olink = matb[c4d.ID_MATERIALASSIGNMENTS]
    
    obj_count = olink.GetObjectCount()
    
    #iterate through all objects in the assigned mats object link
    for i in range(obj_count):
        tag = olink.ObjectFromIndex(doc, i)
        if tag:
            #enable undo for changing out the material on the tag
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag)
            #swap materials
            tag[c4d.TEXTURETAG_MATERIAL] = mata
    # add undo for deleting the material
    doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, matb)
    # delete the material
    matb.Remove()
    c4d.EventAdd()

def GetAllRedshiftMats(doc=None):
    if not doc:
        doc = c4d.documents.GetActiveDocument()
        
    mats = []
    mat = doc.GetFirstMaterial()
    
    while mat:
        # Only check redshift materials
        if mat.GetType() == REDSHIFT_SHADER_GRAPH_ID:
            mats.append(mat)
        mat = mat.GetNext()
        
    return mats

def CompareAllRedshiftMats(doc=None):
    if not doc:
        doc = c4d.documents.GetActiveDocument()
    doc.StartUndo()
    
    # each time we check a material we add it to the list to 
    # make sure we don't check it twice
    checked_mats = []
    mats = GetAllRedshiftMats(doc=doc)
    
    # we keep trying until the the amount of checked 
    # materials is equal the the total material list
    while len(checked_mats) < len(mats):
        mata = None
        # iterate through the mats to find the first material we
        # haven't checked yet
        for mat in mats:
            if mat not in checked_mats:
                mata=mat
                # as soon as we find one we quit the iteration
                break
        # if we didn't find any we haven't used then we quit the loop
        if not mata:
            break
        
        checked_mats.append(mata)
        
        for matb in mats:
            if matb not in checked_mats:
                if CompareRedshiftMaterial(mata, matb):
                    ReplaceMaterial(mata, matb, doc=doc)
        
        # update the mats list since we have deleted some materials
        mats = GetAllRedshiftMats(doc=doc)
    
    doc.EndUndo()
                
    

# Main function
def main():
    CompareAllRedshiftMats()

# Execute main()
if __name__=='__main__':
    main()