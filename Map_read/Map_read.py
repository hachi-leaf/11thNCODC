import cv2
import numpy as np
import time,os
from hobot_vio import libsrcampy as srcampy
import copy

def map_read(img):
    """
    The principle of this function:

    First, 
    the image is converted into a grayscale map.

    After Gaussian filtering, Canny edge detection and expansion operation processing, 
    the quadrilateral is used to fit the edge.

    And a set of data with the shortest distance 
    between the center of the quadrilateral and the center of the image is found, 
    and then the original image is perspective transformed and corrected, 

    And finally the treasure coordinates are detected in it.


    Secondly, 
    for the obtained coordinates, 
    it is verified according to the rules, 
    ensuring that the points have and only eight and are symmetric with respect to the center.
    """

    img = cv2.resize(img,(720,720))

    Map_0 =[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,0],
            [0,1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,1,0,0,0],
            [0,1,0,1,0,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0],
            [0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0],
            [0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0],
            [0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,1,0,0,0],
            [0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0],
            [0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0],
            [0,1,0,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
            [0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0],
            [0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1,0],
            [0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,1,0],
            [0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,0],
            [0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,1,0,1,0,0,0],
            [0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,0],
            [0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
            [0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,0,1,0,1,0],
            [0,0,0,1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,1,0],
            [0,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

    Map_0 = np.array(Map_0 , dtype = "float32")

    # Grayscale conversion
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gaussian filtering
    img_GaussianBlur = cv2.GaussianBlur(img_gray, (3,3), 0)

    # Canny edge detection
    img_Canny = cv2.Canny(img_GaussianBlur,63,255)

    # Dilat operation
    kernel_3 = np.ones((3,3),np.uint8)
    img_dil = cv2.dilate(img_Canny,kernel_3,iterations = 1)

    # Find the contours
    countours, __ = cv2.findContours(img_dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    con_date = []
    # Traverse the contours
    for __ , cnt in enumerate(countours):
        epsilon = 0.1 * cv2.arcLength(cnt, True)  # Calculates the length of the contours line
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # Append the vertex coordinates and the distance from center
        point_date = []
        point = approx.reshape(-1,2)
        point = point.tolist()
        if len(point) == 4:
            point_date.append(point)
            ly = ( point[0][0] + point[1][0] + point[2][0] + point[3][0] )/4
            lx = ( point[0][1] + point[1][1] + point[2][1] + point[3][1] )/4
            lo = ((lx-359.5)**2 + (ly-359.5)**2)**(1/2)
            point_date.append(lo)
            con_date.append(point_date)
    
    # Output the error1
    if len(con_date) == 0:
        return 1 , None
    
    # Find the point that has the shortest distance from center
    min_len =  1000
    min_i = -1
    for i in range(len(con_date)):
        if con_date[i][1] < min_len:
            min_len = con_date[i][1]
            min_i = i

    true_point = con_date[min_i][0]

    # Calculate the central coordinate again
    ty = ( true_point[0][0] + true_point[1][0] + true_point[2][0] + true_point[3][0] )/4
    tx = ( true_point[0][1] + true_point[1][1] + true_point[2][1] + true_point[3][1] )/4

    # Compute transformation matrix
    point1 = [None,None,None,None]
    for i in range(4):
        if true_point[i][0] - ty < 0 and true_point[i][1] - tx < 0:
            point1[0] = true_point[i]
        elif true_point[i][0] - ty < 0 and true_point[i][1] - tx > 0:
            point1[1] = true_point[i]
        elif true_point[i][0] - ty > 0 and true_point[i][1] - tx > 0:
            point1[2] = true_point[i]
        elif true_point[i][0] - ty > 0 and true_point[i][1] - tx < 0:
            point1[3] = true_point[i]
        else:
            return 2 , None # Output the error2
        
    # Output the error5
    try:
        point1 = np.array(point1,dtype = "float32")
    except:
        return 5 , None
    point2 = np.array([[0,0],[0,512],[512,512],[512,0]],dtype = "float32")
    M = cv2.getPerspectiveTransform(point1,point2)

    # Perspective transformation
    Map_p1 = cv2.warpPerspective(img,M,(512,512))

    # Grayscale conversion
    Map_gray = cv2.cvtColor(Map_p1, cv2.COLOR_BGR2GRAY)

    # Rotation correction
    if Map_gray[16][16] < Map_gray[495][16]:
        Map_gray = cv2.rotate(Map_gray, cv2.ROTATE_90_CLOCKWISE)

    # Rotation correction
    point3 = np.array([[4,4],[466,0],[508,508],[47,511]],dtype = "float32")
    point4 = np.array([[16,16],[656,16],[656,656],[16,656]],dtype = "float32")
    M_t = cv2.getPerspectiveTransform(point3,point4)
    Map_p2 = cv2.warpPerspective(Map_gray,M_t,(672,672))

    # Use Canny profile detection to get directions
    #Map_p3 = cv2.GaussianBlur(Map_p2, (3,3), 0)
    #Map_p3 = cv2.Canny(Map_p3,255,255)

    # Use Binarization to get directions
    __ , Map_p3 = cv2.threshold(Map_p2, 127 , 255, cv2.THRESH_BINARY_INV)

    # Convert maps into matrices
    Map_p4 = []
    for i in range(21):
        mapc = []
        for j in range(21):
            if i == 0 or i == 20 or j == 0 or j==20:
                mapc.append(0)
            elif np.mean(Map_p3[i*32:i*32+32,j*32:j*32+32]) != 0:
                mapc.append(0)
            else:
                mapc.append(1)
        Map_p4.append(mapc)

    Map_p4 = np.array(Map_p4,dtype = "float32")
    
    # The Map_0 minus the Map_p4 to get the points loction
    Aim = Map_0 - Map_p4
    Aim_ran = []
    Aim_loction = []
    for i in range(10):
        Ar = []
        for j in range(10):
            if Aim[2*i+1][2*j+1] == 0:
                Ar.append(0)
            else:
                Ar.append(1)
                Aim_loction.append([i,j])
        Aim_ran.append(Ar)

    Aim_ran = np.array(Aim_ran , dtype = "uint8")

    # Correct is judged by the symmetry of the number of points           
    if len(Aim_loction) != 8:
        return 3 , None #排错
    Aim_ran_A = Aim_ran[:5]
    Aim_ran_B = Aim_ran[5:]
    Aim_ran_B = np.rot90(Aim_ran_B, 2)
    Aim_ran_AB = Aim_ran_A - Aim_ran_B
    if np.max(Aim_ran_AB) != 0 or np.min(Aim_ran_AB) != 0:
        return 4 , None #Output error4
    
    Map_p3 = cv2.cvtColor(Map_p3 , cv2.COLOR_GRAY2RGB)

    for i in range(len(Aim_loction)):
        cv2.circle(Map_p3, ((Aim_loction[i][1])*64+48 , (Aim_loction[i][0])*64+48), 20, (0,0,255), 4)

    return 0 , Aim_loction


def map_read_aux(video,t = map_read):
    """
    This function is to correct the result of 'map_read'.
    The coordinates will be output after the result is the same 60 times
    """
    
    
    cs = 0
    while True:
        _ , frame = video.read()


        ret , Vim = t(frame)
        
        print(ret)
        if ret == 0:
            vim_list = [[],[],[],[]]
            for vim in Vim:
                if vim[0] >= 5 and vim[1] <= 4:
                    vim_list[0].append(vim)
                    
                if vim[0] >= 5 and vim[1] >= 5:
                    vim_list[1].append(vim)
                    
                if vim[0] <= 4 and vim[1] <= 4:
                    vim_list[2].append(vim)
                    
                if vim[0] <= 4 and vim[1] >= 5:
                    vim_list[3].append(vim)
                    
            Vim = []
            for i in range(4):
                for j in range(2):
                    Vim.append(vim_list[i][j])
                    
            print(Vim)
            return Vim

if __name__ == "__main__": #USB Camera test
    video = cv2.VideoCapture(0)
    if video.isOpened() == 1:
        print("open camera succes!")
    else:
        print("camera error!!!")
        sys.exit()
    codec = cv2.VideoWriter_fourcc( 'M', 'J', 'P', 'G' )
    video.set(cv2.CAP_PROP_FOURCC, codec)
    video.set(cv2.CAP_PROP_FPS, 30)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    map_read_aux(map_read)


