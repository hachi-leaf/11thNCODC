import numpy as np
import os,time,sys,cv2
import copy as cp

from map_read import *
from Road_plan_new import *
from Reprimand import *
from board import *

import serial
import serial.tools.list_ports
import Hobot.GPIO as GPIO
from hobot_vio import libsrcampy as srcampy
from hobot_dnn import pyeasy_dnn as dnn
from postprocess import postprocess

def road_send(mode,road_list_,over): # send the road
    road_list = road_list_
    if over:
        road_list[-1] = 'f'
    if mode == None:
        rol = 'r'
        for road in road_list:
            rol += str(road)
        
        print("send:",rol)
        ser.write(rol.encode('UTF-8'))
    if mode == 'b':
        rol = 'r1b'
        for road in road_list:
            rol += str(road)
        
        print("send:",rol)
        ser.write(rol.encode('UTF-8'))
    if mode == 'z':
        if road_list[0] != 1:
            rol = 'b'
            road_list[0] -= 1
        elif road_list[1] == 'r':
            rol = 'z'
            road_list = road_list[2:]
        elif road_list[1] == 'l':
            rol = 'y'
            road_list = road_list[2:]
            
        for road in road_list:
            rol += str(road)
        
        print("send:",rol)
        ser.write(rol.encode('UTF-8'))
        
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
    
def infer_red(): # infer dominoes
    psb = 1
    psb_cls = -1
    time_b = time.time()
    for i in range(20):
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
    
def infer_blue(): # infer dominoes
    psb = 1
    psb_cls = -1
    time_b = time.time()
    for i in range(20):
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
        if psb >= 3:
            return 3-int(psb_cls)
    return -1

 

 
fourcc = cv2.VideoWriter_fourcc(*'XVID')
 
out = cv2.VideoWriter('out.avi', fourcc, 20.0, (1080, 720))
 
fi =0
 

if __name__ == "__main__":
    bot = BOT()
    bot.open_all(1)
    my_loc = [9,0]
    last_dir = 'a'
    last_target = [-1,-1]
    True_num = 0
    try:
        # load models
        print("loading the model...",end = '')
        models = dnn.load('./dominoes_new_yolov5.bin')
        print("loading done")
    
        # open srial
        print("open and set the serial...")
        ser = serial.Serial("/dev/ttyS3", 115200, timeout=0.01)
        print("succes!")
        
        # open camera    
        print("open the camera...",end = '')
        for i in range(20):
            video = cv2.VideoCapture(8)
            if video.isOpened() == 1:
                print("open camera",i,"succes!")
                break
        if video.isOpened() != 1:
            print("camera error")
            sys.exit()
        codec = cv2.VideoWriter_fourcc( 'M', 'J', 'P', 'G' )
        video.set(cv2.CAP_PROP_FOURCC, codec)
        video.set(cv2.CAP_PROP_FPS, 30)
        video.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        bot.open_all(0)
        bot.open_stop(1)
        #input("open read")
        
        while bot.flush() != 'read':
            pass
            
        bot.open_stop(0)
            
        while bot.flush() != 0:
            pass
        
        print("reading map...")
        targets = target_sort(map_read_aux(video))
        targets.append([0,9])
        last_targets = cp.deepcopy(targets)
        print("read finally!!!")
        print("the vim:",targets)
        
        bot.open_all(1)
        
        targets_copy = cp.deepcopy(targets)
        
        vim_loc = targets.pop(0)
        
        for i in range(10):
            date_test = ser.read(1).decode('UTF-8')
        while date_test != '':
            date_test = ser.read(1).decode('UTF-8')
        
        while True:
            if bot.flush() == 'red':
                bot.open_all(0)
                bot.open_red(1)
                infer = infer_red
                break
            if bot.flush() == 'blue':
                bot.open_all(0)
                bot.open_blue(1)
                infer = infer_blue
                break

        
        while bot.flush() != 0:
            pass
        
        ser.write('g'.encode('UTF-8'))
        
        #input('go')
        
        rd , last_dir = shortest_road(my_loc,vim_loc,last_dir,targets_copy,prt = True,len_mode = False)
        
        last_turn = rd[-3]
        
        road_send(None,rd,False)
        #road_send(None,shortest_road([6,0],[7,2],targets_copy,prt = True,len_mode = False))
        
        while True:
            if bot.flush() == 'stop':
                if last_target != [-1,-1]:
                    targets.insert(0,vim_loc)
                    vim_loc = last_target
                bot.open_stop(1)
                my_loc = [9,0]
                #targets.insert(0,)
                while bot.flush() == 'stop':
                    pass
                
                while bot.flush() != 'red' and bot.flush() != 'blue':
                    pass
                    
                bot.open_stop(0)
                    
                ser.write('g'.encode('UTF-8'))
                
                last_dir = 'a'
                rd , last_dir = shortest_road(my_loc,vim_loc,last_dir,targets_copy,prt = True,len_mode = False)
                last_turn = rd[-3]
                road_send(None,rd,vim_loc == [0,9])
                
            if bot.flush() == 'over':
                bot.open_stop(1)
                my_loc = [9,0]
                #targets.insert(0,)
                while bot.flush() == 'stop':
                    pass
                
                while bot.flush() != 'red' and bot.flush() != 'blue':
                    pass
                    
                bot.open_stop(0)
                    
                ser.write('g'.encode('UTF-8'))
                
                last_dir = 'a'
                rd , last_dir = shortest_road(my_loc,vim_loc,last_dir,targets_copy,prt = True,len_mode = False)
                last_turn = rd[-3]
                road_send(None,rd,vim_loc == [0,9])

            
        
            ret, frame = video.read()
            date = ser.read(1).decode('UTF-8')
            if date == 'e':
                my_loc = vim_loc
                last_target = cp.deepcopy(vim_loc)
                # order = input('end')
                # order = 'b'
                #order = 'z'
                #for i in range(15):
                #    print(i)
                #    ret, frame = video.read()
                #    cv2.imwrite('dmn/'+str(fi)+'.jpg',frame)
                #    fi += 1
                
            
            if date == 'd':
                
                cls = infer()   
                if cls == 0 or cls == 1:
                    targets = rep(my_loc,True,targets)
                elif cls == 2 or cls == 3:
                    targets = rep(my_loc,False,targets)
                    
                
                vim_loc = targets.pop(0)
                 
                if cls == 0:
                    True_num += 1
                    order = 'b'
                else:
                    order = 'z'
                    
                if True_num >= 3:
                    vim_loc = [0,9]
                    targets = []
                    
                if order == 'b':
                    rd , last_dir = shortest_road(my_loc,vim_loc,last_dir,targets_copy,prt = True,len_mode = False)
                    road_send('b',rd,vim_loc == [0,9])
                    continue
                elif order == 'z':
                    rd , last_dir = shortest_road(my_loc,vim_loc,last_dir,targets_copy,prt = True,len_mode = False)
                    road_send('z',rd,vim_loc == [0,9])
                elif order == 'y':
                    rd , last_dir = shortest_road(my_loc,vim_loc,last_dir,targets_copy,prt = True,len_mode = False)
                    road_send('y',rd,vim_loc == [0,9])
                    
                last_turn = rd[-3]
                
                
                    

      
    finally:
        video.release()