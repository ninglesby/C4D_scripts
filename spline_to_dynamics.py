import c4d
from c4d import gui
import math
#Welcome to the world of Python


#C4D uses integers to identify different objects. These integers are probably listed somewhere in the document and have an associated variable,
#however I find it much faster to drag and drop them onto the console and print their ID
CONNECTOR_ID = 180000011
DYNAMICS_TAG_ID = 180000102
PYTHON_TAG_ID = 1022749

#I wanted the script to be self containted so this prints out another python script needed for a python tag on the spline
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


#converts a vector to a rotation matrix
def vec_to_mat(vec):
    rot_hpb = c4d.utils.VectorToHPB(vec)
    obj_mg = c4d.utils.HPBToMatrix(rot_hpb)
    
    return obj_mg

#measure teh distance between two points
def distance(pnt_a, pnt_b):
    
    dist = math.sqrt(math.pow(pnt_a.x-pnt_b.x, 2) + math.pow(pnt_a.y-pnt_b.y, 2) + math.pow(pnt_a.z-pnt_b.z, 2))
    
    return dist
    
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
   
   #We'll need to now the previous object and connector later, I am just setting up the variable now
   prev_obj = None
   prev_connector = None
   
   #create a python tag object
   py_tag = c4d.BaseTag(PYTHON_TAG_ID)
   
   #insert our python code from above into the tag
   py_tag[c4d.TPYTHON_CODE] = python_tag_command

   #apply the tag to our object
   obj.InsertTag(py_tag)

   #iterate through all the vertices on the spline
   for pnt_index in range(0,pnt_cnt):
       
       #The first point gets treated a little differently than the other points
       if pnt_index == 0:

           #get the first point on the spline
           pnt_a = obj.GetPoint(pnt_index)
           #get the second point on the spline
           pnt_b = obj.GetPoint(pnt_index+1)
           
           #find the distance between the two points
           dist = distance(pnt_a, pnt_b)
           
           #create a cube object that can be dynamic
           new_cube = c4d.BaseObject(c4d.Ocube) 
           
           #Set absolute position, it is important to note, that SetAbsPos is relative to a parent
           new_cube.SetAbsPos(pnt_a)

           #For our vector to hpb to work our vector has to be relative to the origin, so we subtract the second point
           rot_vec = pnt_a - pnt_b

           #This is a built in function, we are using it to align the cube with spline
           rot_hpb = c4d.utils.VectorToHPB(rot_vec)
           #Setting the rotation
           new_cube.SetAbsRot(rot_hpb) 
           #create a c4d vector relative to the distance between points
           size = c4d.Vector(dist/10, dist/10, dist/10)
           #apply the size vector to the size parameter of the cube
           new_cube[c4d.PRIM_CUBE_LEN] = size
           #Give the cube a name, this is important because we will be using the name later to identify different points
           new_cube[c4d.ID_BASELIST_NAME] = obj[c4d.ID_BASELIST_NAME] + "_ROOT_%d" % pnt_index
           #setting the prev_obj variable as the cube we are making
           prev_obj = new_cube

           #insert our cube into the document
           doc.InsertObject(new_cube)
           
           #create a dynamics tag
           dyn_tag = c4d.BaseTag(DYNAMICS_TAG_ID)
           #turn dynamics off on the tag
           dyn_tag[c4d.RIGID_BODY_DYNAMIC] = 0
           #apply the tag to the object
           new_cube.InsertTag(dyn_tag)
           
           
           
       else:
           
           #get the point previous to the current point in the iteration
           pnt_a = obj.GetPoint(pnt_index - 1)
           #get the current point in the iteration
           pnt_b = obj.GetPoint(pnt_index)
           
           #average the points to find the midpoint
           center = (pnt_a + pnt_b)/2
           
           #find the distance between the two points
           dist = distance(pnt_a, pnt_b)
           
           #create a new cube object
           new_cube = c4d.BaseObject(c4d.Ocube) 

           #find the vector starting at the origin
           rot_vec = pnt_a - pnt_b

           #return a rotation matrix based off the orientation of the vector
           obj_mg = vec_to_mat(rot_vec)

           #the fourth dimension of the matrix is "offset" which is also the global position, set that to the midpoint
           obj_mg.off = center

           #create a locator box, the position of this box controls the vertices of the spline, it is also useful to be the parent 
           #of objects you want to move with rope

           #size is relative to the distance between vertices on the spline
           locator_size = c4d.Vector(dist/10, dist/10, dist/10)
           #create a new cube object
           locator_cube = c4d.BaseObject(c4d.Ocube) 
           #get the matrix with the proper orientation
           locator_mg = vec_to_mat(rot_vec)
           #set the position to the current point in the iteration
           locator_mg.off = pnt_b
           #set the name, this is import because we will use this name later to find the object
           locator_cube[c4d.ID_BASELIST_NAME] = obj[c4d.ID_BASELIST_NAME] + "_ROOT_%d" % pnt_index
           #set the size of the cube
           locator_cube[c4d.PRIM_CUBE_LEN] = locator_size

           

           #length is equal to the distance between the two points, width is relative to length
           size = c4d.Vector(dist/20, dist/20, dist)
           #set the size of the new cube
           new_cube[c4d.PRIM_CUBE_LEN] = size
           #give it a name
           new_cube[c4d.ID_BASELIST_NAME] = obj[c4d.ID_BASELIST_NAME] + "_%d" % pnt_index
           #insert the two objects just created
           doc.InsertObject(new_cube, parent=prev_obj)
           doc.InsertObject(locator_cube, parent=new_cube)
           
           #create a dynamcis tag object
           dyn_tag = c4d.BaseTag(DYNAMICS_TAG_ID)
           #by default I give the tag a little dampening and drag
           dyn_tag[c4d.RIGID_BODY_LINEAR_DAMPING] = .01
           dyn_tag[c4d.RIGID_BODY_ANGULAR_DAMPING] = .01
           dyn_tag[c4d.RIGID_BODY_AERODYNAMICS_DRAG] = .01
           #apply the tag to the cube
           new_cube.InsertTag(dyn_tag)

           #create a connector object
           connector = c4d.BaseObject(CONNECTOR_ID)
           #create a matrix for the alignment of the connector
           conn_mg = vec_to_mat(rot_vec)
           #set the position in the matrix to the previous vertex
           conn_mg.off = pnt_a
           #change the connector type to ball and socket
           connector[c4d.FORCE_TYPE] = 2
           #put the previous object in the first force object field
           connector[c4d.FORCE_OBJECT_A] = prev_obj
           #and put the current object in the second force object field
           connector[c4d.FORCE_OBJECT_B] = new_cube
           #insert the connecter
           doc.InsertObject(connector, parent=prev_obj)
           
           #make the current object the previous object
           prev_obj = new_cube
           
           #update the c4d scene
           c4d.EventAdd()

           #apply the matrices to all the objects
           new_cube.SetMg(obj_mg)
           locator_cube.SetMg(locator_mg)
           connector.SetMg(conn_mg)
           
           
 
           

           

   
   
   

if __name__=='__main__':
    main()
