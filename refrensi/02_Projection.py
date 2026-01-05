# This work was done by Mohammad Nasucha, Ph.D.
# Ensure you retain this comment in any derivative works.

print("\033c")       #To close all
import numpy as np
from matplotlib import pyplot as plt

#####                                       USER ENTRIES                                    #####
dir = "C:\\Users\\MN\\OneDrive - Universitas Pembangunan Jaya\\Py Project All\\MK KompGraf_IFA308\\M11_Model 3D Astronaut\\Hasil\\"
nama_file = "astronaut"
nama_file_latar = "earth & stars 200"
frame_nbr_start = 0
frame_nbr_stop = 4
nbr_of_frame = frame_nbr_stop-frame_nbr_start
noise_threshold = 40                         #To anticipate noise color within the 3D space.
object_thickness = 0.2                                              #Relative to the 3D size

#####                                     PREPARATION I                                   ######
voxel = np.load(dir + nama_file + "_0.npy")
#voxel = voxel.astype(int)
print("pic.shape =", voxel.shape)
maks = max(voxel.shape)
col, row, depth = maks, maks, maks   #We ensure making a cubic 3D space and a square 2D screen.
# NOTES
# In the following, the programer or user decides the cam position where
# At 3D room border Z = 0 and at the leftmost of the room voxel Z = depth.
# e.g. cam_z = -5 * depth means that the cam resides far ahead the 3D room border.
cam_z = -round(depth/1)                                        #The cam is located at this point.
cam_focal = round(-cam_z)         #The distance between the cam's lense and the 2D screen.
print("cam_z =", cam_z)

print("TO UNDERSTAND THE FOLLOWING MATH OPERATIONS YOU SHALL REFER TO NASUCHA!S GEOMETRIC NOTES")
print('col, row, depth =', col, ',', row, ',', depth)
cx = round(0.5*col); cy = round(0.5*row)            #The center of 3D room, cam and the 2D screen
print('cx, cy =', cx, ',', cy)

#THE 2D SCREEN POSITION IS FIXED, THAT IS, ANALOGOUS TO REAL SENSORS RESIDING AT THE CAM'S FOCAL
room_border_z = 0                                    #The z position of the 3D room's border is 0.
print('room_border_z =', room_border_z)

#DECIDING THE SIZE OF THE 2D SCREEN
col = col; row = row

#####                   DEFINING THE FUNCTION FOR BACKWARD PROJECTION                     #####
# FUNCTION TO CORELATE A PIXEL AT THE 2D SCREEN (px,py) TO A VOXEL IN THE 3D ROOM (vx,vy,vz).
def projection (cx, cy, cam_z, screen_z, px, py, vz):
    #You shall refer to Nasucha!s projection geometric notes
    pz = screen_z
    vx = round (cx + (cx-px) * ((vz-cam_z)/(cam_z-pz)) )
    vy = round (cy + (cy-py) * ((vz-cam_z)/(cam_z-pz)) )
    return vx, vy

#============================================================================================
#======================================    MAIN PROGRAM     =================================
#=========================================  ===================================================
#Preparing gambar latar, exactly just at 2D screen
latar_hitam = np.zeros(shape=(row, col, 3), dtype=np.uint8)          #latar hitam
latar_gambar = plt.imread(nama_file_latar + ".jpg")                  #latar gambar
#latar[:,:,:] = gambar_latar[:,:,:]

for i in range(frame_nbr_start, frame_nbr_stop+1):
    pixel = latar_gambar.copy()              # Put the background picture onto the 2D Screen.
    voxel = np.load(dir + nama_file + "_" + str(i) + ".npy")
    screen_z = cam_z - cam_focal
    print('cam_z =', cam_z); print('screen_z =', screen_z)
    print('NOW BACK PROJECTING: FROM 2D SCREEN TO CAM TO 3D OBJECT')
    print('Finding vx and vy of the 3D object that corelates with every pixel of 2D sceen.')
    for px in range(0, col):               #x of a pixel of the 2D screen
        print('Projecting frame number', str(i), ': projecting voxels to the screen at x =', px, '.')
        for py in range(0, row):           #y of that pixel
            for vz in range(0, depth):    #z of the voxel of the corelating 3D object
                                           #starting from 3D room's border (ringht to left)
                vx, vy = projection (cx, cy, cam_z, screen_z, px, py, vz)        #Projection
                if (vy >= 0 and vy < row and vx >= 0 and vx < col) and \
                    (int(voxel[vy,vx,vz,0]) + int(voxel[vy,vx,vz,1]) + int(voxel[vy,vx,vz,2]) > \
                     noise_threshold):
                    pixel[row-py-1,col-px-1,:] = voxel[vy,vx,vz,:]
                    #print('Projecting a voxel and skipping the vz loop')
                    break
    plt.imsave(dir + nama_file + "_" + str(i) + "_" + str(cam_z) + ".jpg", pixel)
plt.figure
plt.imshow(pixel)
plt.show()
