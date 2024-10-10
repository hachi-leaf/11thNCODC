import numpy as np
import os,time,sys,cv2
import copy as cp

import serial
import serial.tools.list_ports

import Hobot.GPIO as GPIO
from hobot_vio import libsrcampy as srcampy
from hobot_dnn import pyeasy_dnn as dnn

from postprocess import postprocess
from map_read import *
from shortest_load import *

def bgr2nv12_opencv(image): # cv2 to nv12
    height, width = image.shape[0], image.shape[1]
    area = height * width
    yuv420p = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420).reshape((area * 3 // 2,))
    y = yuv420p[:area]
    uv_planar = yuv420p[area:].reshape((2, area // 4))
    uv_packed = uv_planar.transpose((1, 0)).reshape((area // 2,))

    nv12 = np.zeros_like(yuv420p)
    nv12[:height * width] = y
    nv12[height * width:] = uv_packed
    return nv12
    
def road_send(road_list,turn): # send the road
    rol = 'r4'
    for road in road_list:
        rol += str(road)
    rol += 'e'
    
    if turn == 'b':
        rol = rol[0]+rol[2:]
        
    elif turn == 't':
        rol = rol[0]+rol[3:]
    print("send:",rol)
    ser.write(rol.encode('UTF-8'))
        
def infer(): # infer dominoes
    psb = 1
    psb_cls = -1
    time_b = time.time()
    for i in range(50):
        _ , image = video.read()
        
        image = cv2.resize(image,(640,640))
        
        image = cv2.resize(image, (640,640), interpolation=cv2.INTER_AREA)
        nv12_data = bgr2nv12_opencv(image)
        
        outputs = models[0].forward(nv12_data)
        box = postprocess(outputs, model_hw_shape=(640, 640), origin_img_shape=(640,640))
        print(box)
        max_psb = 0
        max_cls = -1
        for thing in box:
            if thing[4] > max_psb:
                max_psb = thing[4]
                max_cls = thing[5]
                
        if max_cls == 2 or max_cls == 3:
            max_cls = 2
        elif max_cls == 4 or max_cls == 5:
            max_cls = 3
                
        if max_cls == -1:
            psb = 1
            psb_cls = -1
        else:
            if max_cls == psb_cls:
                psb += 1
            else:
                psb_cls = max_cls
                psb = 1
                
        print(psb,psb_cls)
        if psb >= 5:
            return int(psb_cls)
    return -1
            
def light(red,green):
    if red == 1:
        GPIO.output(15,GPIO.HIGH)
    else:
        GPIO.output(15,GPIO.LOW)
        
    if green == 1:
        GPIO.output(13,GPIO.HIGH)
    else :
        GPIO.output(13,GPIO.LOW)
        
def botton():
    if GPIO.input(11) == GPIO.HIGH:
        return 1
    else:
        return 0
    
    
try:
    f = open('./log/LEV_log_{}_{}_{}.txt'.format(time.localtime().tm_year,time.localtime().tm_mon,time.localtime().tm_mday),'a+')
    
    f.write('\n'+"="*50+'\n')
    f.write("At {}:{}:{} begin\n".format(time.localtime().tm_hour,time.localtime().tm_min,time.localtime().tm_sec))

    #set the light and botton
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.IN)
    GPIO.setup(13,GPIO.OUT)
    GPIO.setup(15,GPIO.OUT)
    GPIO.output(13,GPIO.LOW)
    GPIO.output(15,GPIO.LOW)
    
    # open srial
    print("open and set the serial...",end = '')
    ser = serial.Serial("/dev/ttyS3", 115200, timeout=0.01)
    print("succes!")
    
    f.write("  Open serial succes\n")

    # open camera
    print("open the camera...",end = '')
    video = cv2.VideoCapture(8)
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
    
    f.write("  Open camera succes\n")
        
    # load models
    print("loading the model...",end = '')
    models = dnn.load('./dominoes_yolov5.bin')
    print("loading done")
    f.write("  Load models succes\n")
    
    #light red
    light(1,0)
    
    #map read
    print("reading map...")
    f.write("  Reading map...\n")
    targets = map_read_aux(video)
    print("read finally!!!")
    print("the vim:",targets)
    f.write("  The vim loc:\n")
    for i in range(8):
        f.write("    [{},{}]\n".format(targets[i][0], targets[i][1]))
    
    #light green
    light(0,1)
    
    while botton() == 0:
        pass
    while botton() == 1:
        pass
    f.write("  Run begin")
    
    # var set
    myloc = [9,0]
    tenor = 0
    turn_flag = 0
    
    # count the first road
    #targets = [[6,0],# target list
    #          [6,4],
    #          [7,5],
    #          [5,8],
    #          [2,4],
    #          [4,1],
    #          [3,9],
    #          [3,5],
    #          [0,9]]

    targets_copy = cp.deepcopy(targets)

    # organize the loc and targets
    first_vim = [target for target in targets if target[0]>=5 and target[1]<=4]
    vim = [shortest_load([9,0],first_vim[0],prt=True, vim_7_5=([7,5] in targets_copy), vim_8_3=([8,3] in targets_copy))]
    vim.append(shortest_load([9,0],first_vim[1],prt=True, vim_7_5=([7,5] in targets_copy), vim_8_3=([8,3] in targets_copy) ) )
    if len(vim[0]) > len(vim[1]):
        del vim[0]
        targets[0] , targets[1] = targets[1] , targets[0]
    else:
        del vim[1]
        
    print(vim)
    
    # send the 'begin'
    ser.write('b'.encode('UTF-8'))
    print("begin")
    
    time_begin = time.time()
    
    # send the first road
    road_send(vim[-1],'b')
    
    f.write("\n  {}:{}:{} From [9,0] to [{},{}]: ".format(time.localtime().tm_hour,time.localtime().tm_min,time.localtime().tm_sec,targets[0][0], targets[0][1]))
    
    time_history = [time.time()-1,time.time()]
    
    True_num = 0
    
    while True:
        # stop
        if botton() == 1:
            while botton()==1 :
                pass
            
            f.write("\n  outage")
                
            light(1,0)
            myloc = [9,0]
            tenor = 1
            jflag = 0
            while True:
                date = ser.read(1).decode('UTF-8')
                if botton() == 1:
                    while True:
                        if botton() == 0:
                            light(0,1)
                            vim.append(shortest_load([9,0],targets[0],prt=True, vim_7_5=([7,5] in targets_copy), vim_8_3=([8,3] in targets_copy) ) )
                            f.write('\n  restart')
                            ser.write('b'.encode('UTF-8'))
                            road_send(vim[-1],'b')
                            f.write("\n  {}:{}:{} From [9,0] to [{},{}]: ".format(time.localtime().tm_hour,time.localtime().tm_min,time.localtime().tm_sec,targets[0][0], targets[0][1]))
                            jflag = 1
                            break
                if jflag == 1:
                    break
                
            
    
        # read serial
        date = ser.read(1).decode('UTF-8')
        
        if date == 'f': # tenor++
            tenor += 1
            print('turn',tenor)
            f.write("+")
            
            
        if tenor == len(vim[-1]): # turn over, vision the dominoes
            # finally
            if len(targets)==1:
                f.write("\n  Finish, time spend "+str(time.time()-time_begin)+'\n')
                break
            print('see...')
            turn_flag += 1;
            f.write("\n    Arrive [{},{}]".format(targets[0][0],targets[0][1]))
            myloc = targets[0]
            del targets[0]
            print("myloc",myloc)
            sym_loc = [9-myloc[0] , 9-myloc[1]]
            cls = infer()
            
            f.write(" class: "+str(cls))

            if cls == 3:
                True_num += 1

            if cls == 3 or cls == 2:
                if sym_loc in targets:
                    targets.remove(sym_loc)
                    f.write("\n    remove [{},{}]".format(sym_loc[0],sym_loc[1]))
                for target in targets:
                    onnaji = 0
                    if (myloc[0]<=4 and target[0]<=4) or (myloc[0]>=5 and target[0]>=5):
                        onnaji += 1
                    if (myloc[1]<=4 and target[1]<=4) or (myloc[1]>=5 and target[1]>=5):
                        onnaji += 1
                    if onnaji == 2:
                        targets.remove(target)
                        print("rm",target)
                        f.write("\n    remove [{},{}]".format(target[0],target[1]))
                        
            if cls == 0 or cls == 1:
                for target in targets:
                    onnaji = 0
                    if (myloc[0]<=4 and target[0]<=4) or (myloc[0]>=5 and target[0]>=5):
                        onnaji += 1
                    if (myloc[1]<=4 and target[1]<=4) or (myloc[1]>=5 and target[1]>=5):
                        onnaji += 1
                    if onnaji == 0 and target != sym_loc:
                        targets.remove(target)
                        f.write("\n    remove [{},{}]".format(target[0],target[1]))

                        print("rm",target)
                        
                if cls == 1:
                    if sym_loc in targets:
                        targets.remove(sym_loc)
                        f.write("\n    remove [{},{}]".format(sym_loc[0],sym_loc[1]))
                        print("rm",target)
                        
            if True_num == 3:
                targets = []
                f.write("\n  Remove all")
                        
            print(targets)
            if len(targets) == 0:
                targets.append([0,9])
            if [0,9] not in targets:
                targets.append([0,9])
            vim.append(shortest_load(cp.deepcopy(myloc),targets[0],prt=True,vim_7_5=([7,5] in targets_copy), vim_8_3=([8,3] in targets_copy)))
            f.write("\n  {}:{}:{} From [{},{}] to [{},{}]: ".format(time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec, myloc[0], myloc[1], targets[0][0], targets[0][1]))
            print(targets_copy)
            print(myloc)
            print(targets)
            
            if cls == 3:
                ser.write('g'.encode('UTF-8'))
                road_send(vim[-1],'f')
                tenor = -1
            else:
                if vim[-1][0] == 2:
                    ser.write('Y'.encode('UTF-8'))
                if vim[-1][0] == 3:
                    ser.write('Z'.encode('UTF-8'))
                if vim[-1][0] == 1:
                    ser.write('U'.encode('UTF-8'))
            
                road_send(vim[-1],'t')
                tenor = 0
            


    

    
finally:
    video.release()
    f.close()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
