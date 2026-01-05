# This work was done by Mohammad Nasucha, Ph.D.
# Ensure you retain this comment in any derivative work.
print("\033c")       #It tells the terminal to clear itself.
import numpy as np
from matplotlib import pyplot as plt

####                               USER ENTRIES                                  ####

#Resolution and Threshold
col, row, depth, ch = 200, 200, 200, 3
nama_file = "astronaut"
output_dir = "C:\\Users\\MN\\OneDrive - Universitas Pembangunan Jaya\\Py Project All\\MK KompGraf_IFA308\\M11_Model 3D Astronaut\\Hasil\\"
noise_threshold = 10                    #To anticipate noise color within the 3D space.
object_thickness = 0.2                                        #Relative to the 3D size

#Animation Paremeters
zc = round(0.15*depth)                         #Initial position of the model at the Z-axis.
cx = round(col/2); cy = round(row/2); cz = zc  #Ini adalah titik pusat model, bukan ruangan.
alfa_start = 0; beta_start = 0
delta_alfa, delta_beta = 3, 10          #Rotation about the z-axis (alfa) and y-axis (beta).
frame_nbr_start = 0
frame_nbr_stop = 38
nbr_of_frame = frame_nbr_stop-frame_nbr_start
dz = round(0.8*depth/nbr_of_frame); dy = round(dz/10); dx = dy

# CREATING THE MODEL
#The astronaut sketch was done using 1000 pixel resolution.
# Thus, for other resolution you shall make adjustment / nomination
# using the following function.

#Creating the Model: Colors
body_white = (240, 240, 240)
head_arm_leg_white = (200,200, 200)
foot_grey = (100, 100, 100)
eye_black = (11, 11, 11)
eye_blue = (30, 30, 133)
gold = (255, 182, 0)
joint_black = (18, 18, 18)
sleeve_red = (255, 100, 100)
leg_red = (255, 0, 0)
arm_red = leg_red
back_pack_gray = (120, 110, 105)
antenna_gray = (61, 61, 61)

# A  function to calculate nominal coordinate values in such a way
# so that the model appearance does not change with resolution
def nom(value):
    return round(row*value/1000)

#Creating the Model: Z Coordinates
body_z = (zc-nom(48), zc+nom(48+1))
head_z = body_z
arm_z = body_z
backpack_z = (zc+nom(48), zc+nom(144+1))
antenna_z = (zc+nom(130), zc+nom(140+1))
sleeve_red_z = arm_z
fingers_z = (zc-nom(8), zc+nom(8+1))
#gold_z = (body_z[0]-nom(4), zc+nom(4))
gold_z = (body_z[0]-nom(4), body_z[0]+nom(10))
eye_z = gold_z
chest_blue_strip_z = (zc-nom(47), zc-nom(44+1))
leg_z = (zc-nom(50), zc+nom(50+1))
leg_red_z = leg_z
foot_z = (zc-nom(73), zc+nom(60+1))

#Creating the Model: Y and X Coordinates
head_y = (nom(99), nom(250+1))
head_x = (nom(409), nom(583+1))
body_y = (nom(258), nom(607+1))               #koordinat rujukan
body_x = (nom(383), nom(609+1))               #koordinat rujukan
backpack_y = (nom(172), nom(474+1))
backpack_x = (nom(366), nom(621+1))
antenna_y = (nom(110), nom(600))              #110 s.d. 172
antenna_x = (nom(376), nom(386+1))
arm_y = (nom(258), nom(563+1))
arm_right_x = (nom(303), nom(379+1))
arm_left_x = (nom(614), nom(689+1))
arm_red_y = (nom(530), nom(553))
arm_red_right_x = arm_right_x
arm_red_left_x = arm_left_x
leg_y = (nom(610), nom(887+1))
leg_right_x = (nom(383), nom(490+1))
leg_left_x = (nom(503), nom(609+1))
leg_red_y = (nom(670), nom(693+1))
leg_red_right_x = leg_right_x
leg_red_left_x =  leg_left_x
foot_y = (nom(890), nom(938))
foot_right_x = (nom(362), nom(490+1))
foot_left_x = (nom(503), nom(630+1))
finger_y = (nom(582), nom(652))
finger_right_1_x = (nom(279), nom(295+1))
# finger_right_2_x = (423, 429+1)
# finger_right_3_x = (431, 437+1)
# finger_right_4_x = (439, 444+1)
# finger_left_1_x = (546, 551+1)
# finger_left_2_x = (553, 559+1)
# finger_left_3_x = (561, 567+1)
# finger_left_4_x = (569, 575+1)
eyes_black_y = (nom(120), nom(162+1))
eyes_blue_y = (nom(131), nom(152+1))
eye_black_right_x = (nom(430), nom(479+1))
eye_blue_right_x = (nom(443), nom(466+1))
eye_black_left_x = (nom(518), nom(568+1))
eye_blue_left_x = (nom(531), nom(555+1))
gold_y = (nom(336), nom(456+1))
gold_x = (nom(438), nom(562+1))
chest_blue_strip_ad_y = (nom(313), nom(321+1))
chest_blue_strip_be_y = (nom(417), nom(425))
chest_blue_strip_cf_y = (nom(24), nom(552))
chest_blue_strip_ab_x = (nom(360), nom(412+1))
chest_blue_strip_de_x = (nom(588), nom(640+1))
chest_blue_strip_c_x = (nom(360), nom(490+1))
chest_blue_strip_f_x = (nom(510), nom(640+1))

##                 FUNCTION FOR DEGREE TO RAD CONVERSION                  ##
# Converting degree unit of alfa and beta to radiant unit
def degree_to_rad (alfa, beta):
    alfa_rad = (alfa / 180) * np.pi  # Converting degree to rad
    beta_rad = (beta / 180) * np.pi  # Converting dgreee to rad
    return alfa_rad, beta_rad

##        FUNCTION TO ROTATE A VOXEL (yi, xi, zi) ABOUT A CENTER         ##
##                  AS MUCH AS ALFA RAD THEN BETA RAD                    ##
# Pusat rotasi: y_pusat, x_pusat, koordinat asal: xi, yi;
# Koordinat hasil rotasi: xr2, yr2, zr2.
#def rotate(vx,vy,vz,cx,cy,cz,alfa_rad,beta_rad):
def putar_titik(y_pusat, x_pusat, z_pusat, yi, xi, zi, alfa_rad, beta_rad):
    #Putar titik dengan as berupa sumbu z, sejauh alfa_rad
    xr1 = round(np.cos(alfa_rad)*(xi-x_pusat) - np.sin(alfa_rad)*(yi-y_pusat)) + x_pusat
    yr1 = round(np.sin(alfa_rad)*(xi-x_pusat) + np.cos(alfa_rad)*(yi-y_pusat)) + y_pusat
    zr1 = zi                                                                  #zi tetap.
    #Putar titik dengan as berupa sumbu y, sejauh beta_rad
    xr2 = round(np.cos(beta_rad)*(xr1-x_pusat) - np.sin(beta_rad)*(zr1-z_pusat)) + x_pusat
    zr2 = round(np.sin(beta_rad)*(xr1-x_pusat) + np.cos(beta_rad)*(zr1-z_pusat)) + z_pusat
    yr2 = yr1                                                                  #yi tetap.
    return yr2, xr2, zr2

####                                   MAIN PROGRAM                                   ####

###                               CREATING THE 3D MODEL                               ###
print("Creating the Template of the 3D Space ...")
voxel  = np.zeros(shape=(row, col, depth, ch), dtype=np.uint8)    #Template for the 3D model
buffer = np.zeros(shape=(row, col, depth, ch), dtype=np.uint8)    #Template for the 3D buffer
slice = np.zeros(shape=(row, col, ch), dtype=np.uint8)             #Template for the slice cut

print ("Creating Body Parts")
print ("Creating arms...")
voxel[arm_y[0]:arm_y[1], arm_right_x[0]:arm_right_x[1], arm_z[0]:arm_z[1]] = head_arm_leg_white #right arm
voxel[arm_y[0]:arm_y[1], arm_left_x[0]:arm_left_x[1], arm_z[0]:arm_z[1]] = head_arm_leg_white #left arm

print ("Creating right arm red strips...")
voxel[arm_red_y[0]:arm_red_y[1], arm_red_right_x[0]:arm_red_right_x[1], arm_z[0]:arm_z[1]] = arm_red #right arm
voxel[arm_red_y[0]:arm_red_y[1], arm_red_left_x[0]:arm_red_left_x[1], arm_z[0]:arm_z[1]] = arm_red #right arm

print ("Creating head...")
voxel[head_y[0]:head_y[1], head_x[0]:head_x[1], head_z[0]:head_z[1]] = head_arm_leg_white #head
print ("Creating two eyes...")
voxel[eyes_black_y[0]:eyes_black_y[1], eye_black_right_x[0]:eye_black_right_x[1], eye_z[0]:eye_z[1]] = eye_black #right eye
voxel[eyes_black_y[0]:eyes_black_y[1], eye_black_left_x[0]:eye_black_left_x[1], eye_z[0]:eye_z[1]] = eye_black #right eye
voxel[eyes_blue_y[0]:eyes_blue_y[1], eye_blue_right_x[0]:eye_blue_right_x[1], eye_z[0]:eye_z[1]] = eye_blue #right eye
voxel[eyes_blue_y[0]:eyes_blue_y[1], eye_blue_left_x[0]:eye_blue_left_x[1], eye_z[0]:eye_z[1]] = eye_blue #right
print ("Creating the body...")
voxel[body_y[0]:body_y[1], body_x[0]:body_x[1], body_z[0]:body_z[1]] = body_white
print ("Creating two legs...")
voxel[leg_y[0]:leg_y[1], leg_right_x[0]:leg_red_right_x[1], leg_z[0]:leg_z[1]] = head_arm_leg_white
voxel[leg_y[0]:leg_y[1], leg_left_x[0]:leg_red_left_x[1], leg_z[0]:leg_z[1]] = head_arm_leg_white
print ("Creating two feet...")
voxel[foot_y[0]:foot_y[1], foot_right_x[0]:foot_right_x[1], foot_z[0]:foot_z[1]] = foot_grey
voxel[foot_y[0]:foot_y[1], foot_left_x[0]:foot_left_x[1], foot_z[0]:foot_z[1]] = foot_grey
print ("Creating red strips...")
voxel[leg_red_y[0]:leg_red_y[1], leg_right_x[0]:leg_right_x[1], leg_z[0]:leg_z[1]] = leg_red
voxel[leg_red_y[0]:leg_red_y[1], leg_left_x[0]:leg_left_x[1], leg_z[0]:leg_z[1]] = leg_red
print ("Creating golden chest square...")
voxel[gold_y[0]:gold_y[1], gold_x[0]:gold_x[1], gold_z[0]:gold_z[1]] = gold
print ("Creating the backpack...")
voxel[backpack_y[0]:backpack_y[1], backpack_x[0]:backpack_x[1], backpack_z[0]:backpack_z[1]] = back_pack_gray
print ("Creating the antenna...")
voxel[antenna_y[0]:antenna_y[1], antenna_x[0]:antenna_x[1], antenna_z[0]:antenna_z[1]] = antenna_gray

#NEXT blue strips, fingers

###            TEMPORARY VISUALIZATION OF THE 3D MODEL(S) USING SLICING              ###
half_row, half_col, half_depth = round(row/2), round(col/2), round(depth/2)
#Visualizing the cross slice at the Y-axis
slice[:, :, :] = voxel[nom(400), :, :, :]
plt.figure("A CROSS SLICE AT Y-AXIS"); plt.imshow(slice)
#Visualizing the cross slice at the X-axis
slice[:, :, :] = voxel[:, nom(454), :, :]
plt.figure("A CROSS SLICE AT X-AXIS"); plt.imshow(slice)
#Visualizing the cross slice at the Z-axis
slice[:, :, :] = voxel[:, :, body_z[0], :]
plt.figure("A CROSS SLICE AT Z-AXIS"); plt.imshow(slice)
#plt.ion()
#plt.pause(10)
np.save(output_dir + nama_file + "_0.npy", voxel)

###                ANIMATING THE MODEL: Rotate and translate the model               ###
#rotation
alfa = 0+delta_alfa*frame_nbr_start; beta = 0+delta_beta*frame_nbr_start
#translation
ty = 0+dy*frame_nbr_start; tx = 0+dx*frame_nbr_start; tz = 0+dy*frame_nbr_start

for m in range (frame_nbr_start, frame_nbr_stop+1):
    alfa_rad, beta_rad = degree_to_rad(alfa, beta)                    #Convert degree to rad.
    voxel = np.load(output_dir + nama_file + "_0.npy")           #Always reads original model.
    for i in range (0, row):                                  #Rotating te whole voxel[:,:,:]
        print('ANIMATING: frame number', str(m), ', alfa beta =', alfa, beta, ', ty tx tz =',ty, tx, tz, 'now processing voxels in row', i, '.')
        for j in range (0, col):
            for k in range (0, depth):
                cek1 = int(voxel[i,j,k,0])
                cek2 = int(voxel[i,j,k,1])
                cek3 = int(voxel[i,j,k,2])
                if (cek1 + cek2 + cek3) > noise_threshold:
                    yr, xr, zr = putar_titik(cy,cx,cz,i,j,k,alfa_rad,beta_rad) #Rotate the voxel
                    i, j, k, yr, xr, zr = int(i), int(j), int(k), int(yr), int(xr), int(zr)
                    buffer[yr+ty, xr+tx, zr+tz,:] = voxel[i,j,k,:]          #rotate and translate
                    voxel[i,j,k,:] = 0 #The voxel that has been rotated must be put back to black.
                    #voxel[i,j,k] = (0,0,0) #The voxel that has been rotated must be put back to black.

    print('Saving the result as a .npy file.')
    np.save(output_dir + nama_file + "_" + str(m) + ".npy", buffer)
    voxel[:, :, :] = 0        #The 3D model must be reset so it's ready for the next job.
    buffer[:, :, :] = 0                                        #the same with the buffer
    alfa = alfa + delta_alfa; beta = beta + delta_beta            #angle for the next job
    ty = ty+dy; tx = tx+dx; tz = tz+dz                      #translation for the next job

#CATATAN
#Putar robot pada sumbu z (alfa) dan sumbu y (beta) sambil translasi maju seearah sumbu z.

plt.show()
