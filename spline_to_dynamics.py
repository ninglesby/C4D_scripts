import c4d
from c4d import gui
import math
#Welcome to the world of Python

CONNECTOR_ID = 180000011
DYNAMICS_TAG_ID = 180000102
PYTHON_TAG_ID = 1022749

python_tag_command =     "import c4d\n\n"
python_tag_command +=    "def main():\n    \n    "
python_tag_command +=    "base_obj = op.GetObject()\n    "
python_tag_command +=    "pnt_cnt = base_obj.GetPointCount()\n    "
python_tag_command +=    "doc = c4d.documents.GetActiveDocument()\n    \n    "
python_tag_command +=    "for pnt in range(0, pnt_cnt):\n    \n        "
python_tag_command +=    "obj_name = base_obj[c4d.ID_BASELIST_NAME] + '_ROOT_%d' % pnt\n        "
python_tag_command +=    "obj = doc.SearchObject(obj_name)\n\n        "
python_tag_command +=    "if obj:\n            "
python_tag_command +=    "base_obj.SetPoint(pnt, obj.GetMg().off)\n\n    "
python_tag_command +=    "base_obj.Message (c4d.MSG_UPDATE)"

def vec_to_mat(vec):
    rot_hpb = c4d.utils.VectorToHPB(vec)
    obj_mg = c4d.utils.HPBToMatrix(rot_hpb)
    
    return obj_mg

def distance(pnt_a, pnt_b):
    
    dist = math.sqrt(math.pow(pnt_a.x-pnt_b.x, 2) + math.pow(pnt_a.y-pnt_b.y, 2) + math.pow(pnt_a.z-pnt_b.z, 2))
    
    return dist

def geo_along_points(pnt_list):
    pass
    
def main():
   
   #Get the open document
   doc = c4d.documents.GetActiveDocument()
   
   #Try to select an object, if no object is selected warn user
   try:
       
       obj = doc.GetActiveObject()
       
   except:
       
       gui.MessageDialog("Please Select A Spline")
       
       return False

    #if the object is not a spline warn user
   if not type(obj) == c4d.SplineObject:
       gui.MessageDialog("Selected Object is not a Spline")
       return False
   
   #Get all the points in the spline
   pnt_cnt = obj.GetPointCount()
   
   prev_obj = None
   prev_connector = None
   
   py_tag = c4d.BaseTag(PYTHON_TAG_ID)
   py_tag[c4d.TPYTHON_CODE] = python_tag_command
   obj.InsertTag(py_tag)

   for pnt_index in range(0,pnt_cnt):
       
       
       if pnt_index == 0:
           pnt_a = obj.GetPoint(pnt_index)
           pnt_b = obj.GetPoint(pnt_index+1)
           
           dist = distance(pnt_a, pnt_b)
           
           new_cube = c4d.BaseObject(c4d.Ocube) 
           new_cube.SetAbsPos(pnt_a)
           rot_vec = pnt_a - pnt_b
           rot_hpb = c4d.utils.VectorToHPB(rot_vec)
           new_cube.SetAbsRot(rot_hpb) 
           size = c4d.Vector(dist/10, dist/10, dist/10)
           new_cube[c4d.PRIM_CUBE_LEN] = size
           new_cube[c4d.ID_BASELIST_NAME] = obj[c4d.ID_BASELIST_NAME] + "_ROOT_%d" % pnt_index
           prev_obj = new_cube

           doc.InsertObject(new_cube)
           
           dyn_tag = c4d.BaseTag(DYNAMICS_TAG_ID)
           dyn_tag[c4d.RIGID_BODY_DYNAMIC] = 0
           new_cube.InsertTag(dyn_tag)
           
           
           
       else:
           
           pnt_a = obj.GetPoint(pnt_index - 1)
           pnt_b = obj.GetPoint(pnt_index)
           
           center = (pnt_a + pnt_b)/2
           
           dist = distance(pnt_a, pnt_b)
           
           new_cube = c4d.BaseObject(c4d.Ocube) 

           rot_vec = pnt_a - pnt_b
           obj_mg = vec_to_mat(rot_vec)
           obj_mg.off = center

           locator_size = c4d.Vector(dist/10, dist/10, dist/10)
           locator_cube = c4d.BaseObject(c4d.Ocube) 
           locator_mg = vec_to_mat(rot_vec)
           locator_mg.off = pnt_b
           locator_cube[c4d.ID_BASELIST_NAME] = obj[c4d.ID_BASELIST_NAME] + "_ROOT_%d" % pnt_index
           locator_cube[c4d.PRIM_CUBE_LEN] = locator_size

           

           
           size = c4d.Vector(dist/20, dist/20, dist)
           new_cube[c4d.PRIM_CUBE_LEN] = size
           new_cube[c4d.ID_BASELIST_NAME] = obj[c4d.ID_BASELIST_NAME] + "_%d" % pnt_index
           doc.InsertObject(new_cube, parent=prev_obj)
           doc.InsertObject(locator_cube, parent=new_cube)
           
           
           dyn_tag = c4d.BaseTag(DYNAMICS_TAG_ID)
           dyn_tag[c4d.RIGID_BODY_LINEAR_DAMPING] = .01
           dyn_tag[c4d.RIGID_BODY_ANGULAR_DAMPING] = .01
           dyn_tag[c4d.RIGID_BODY_AERODYNAMICS_DRAG] = .01
           new_cube.InsertTag(dyn_tag)

           connector = c4d.BaseObject(CONNECTOR_ID)
           conn_mg = vec_to_mat(rot_vec)
           conn_mg.off = pnt_a
           connector[c4d.FORCE_TYPE] = 2
           connector[c4d.FORCE_OBJECT_A] = prev_obj
           connector[c4d.FORCE_OBJECT_B] = new_cube
           doc.InsertObject(connector, parent=prev_obj)
           
           prev_obj = new_cube
           
           
           c4d.EventAdd()
           new_cube.SetMg(obj_mg)
           locator_cube.SetMg(locator_mg)
           connector.SetMg(conn_mg)
           
           
 
           

           

   
   
   

if __name__=='__main__':
    main()
