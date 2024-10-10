import numpy as np
import copy as cp

def x(x_loc):
    return x_loc*2+1 

def y(y_loc):
    return y_loc*2+1 

class map(): # 0墙壁 1黑线 2走过的路线 3宝藏
    def __init__(self):
        self.map = np.array([
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
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
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]])
        
        self.history = []
        self.myloc = [9,0]

    def my_loc(self,loc):
        self.myloc = loc
        self.map[loc[0]*2+1,loc[1]*2+1] = 2

    def set_targets(self,targets):
        for target in targets:
            self.map[target[0]*2+1,target[1]*2+1] = 3

    def map_print(self):
        print("+---0---1---2---3---4---5---6---7---8---9--> y")
        for i in range(21):
            if i%2 == 0:
                print("|",end=' ')
            else:
                print(int((i-1)/2),end=' ')
            for j in range(21):
                if self.map[i,j] == 1:
                    print(' ',end=' ')
                if self.map[i,j] == 0:
                    print('#',end=' ')
                if self.map[i,j] == 2:
                    print('*',end=' ')
                if self.map[i,j] == 3:
                    print('@',end=' ')
            print()
        print('V')
        print('x')

    def possible(self,vim_targets):
        psb = []
        if [self.myloc[0] -1, self.myloc[1]] ==  vim_targets and self.map[x(self.myloc[0]) -1, y(self.myloc[1])] == 1:
            return True, ['w']
        if [self.myloc[0] +1, self.myloc[1]] ==  vim_targets and self.map[x(self.myloc[0]) +1, y(self.myloc[1])] == 1:
            return True, ['s']
        if [self.myloc[0], self.myloc[1]+1 ] ==  vim_targets and self.map[x(self.myloc[0]), y(self.myloc[1]) +1] == 1:
            return True, ['d']
        if [self.myloc[0], self.myloc[1]-1 ] ==  vim_targets and self.map[x(self.myloc[0]), y(self.myloc[1]) -1] == 1:
            return True, ['a']

        if self.map[x(self.myloc[0]) -1, y(self.myloc[1])] == 1 and self.map[x(self.myloc[0]) -2, y(self.myloc[1])] == 1:
            psb.append('w')
        if self.map[x(self.myloc[0]) +1, y(self.myloc[1])] == 1 and self.map[x(self.myloc[0]) +2, y(self.myloc[1])] == 1:
            psb.append('s')
        if self.map[x(self.myloc[0]), y(self.myloc[1]) -1] == 1 and self.map[x(self.myloc[0]), y(self.myloc[1]) -2] == 1:
            psb.append('a')
        if self.map[x(self.myloc[0]), y(self.myloc[1]) +1] == 1 and self.map[x(self.myloc[0]), y(self.myloc[1]) +2] == 1:
            psb.append('d')
    
        return False , psb

    def move(self,dir,apd=True):
        if dir == 'w':
            self.map[self.myloc[0]*2+1 -2, self.myloc[1]*2+1] = 2
            self.map[self.myloc[0]*2+1 -1, self.myloc[1]*2+1] = 2
            self.myloc[0] -= 1
            if apd:
                self.history.append('w')

        if dir == 's':
            self.map[self.myloc[0]*2+1 +2, self.myloc[1]*2+1] = 2
            self.map[self.myloc[0]*2+1 +1, self.myloc[1]*2+1] = 2
            self.myloc[0] += 1
            if apd:
                self.history.append('s')

        if dir == 'a':
            self.map[self.myloc[0]*2+1, self.myloc[1]*2+1 -2] = 2
            self.map[self.myloc[0]*2+1, self.myloc[1]*2+1 -1] = 2
            self.myloc[1] -= 1
            if apd:
                self.history.append('a')

        if dir == 'd':
            self.map[self.myloc[0]*2+1, self.myloc[1]*2+1 +2] = 2
            self.map[self.myloc[0]*2+1, self.myloc[1]*2+1 +1] = 2
            self.myloc[1] += 1
            if apd:
                self.history.append('d')

def shortest_road(begin_loc,end_loc,last_dir,targets,prt = False,len_mode = False):
    first_sam = map()
    first_sam.set_targets(targets)
    group = [first_sam]
    group[0].my_loc(cp.deepcopy(begin_loc))
    flag = -1
    while True:
        for i in range(len(group)):
            if group[i].myloc == begin_loc:
                print(i)
                psb_flag = False
                if last_dir == 'w':
                    psb = ['s']
                if last_dir == 's':
                    psb = ['w']
                if last_dir == 'a':
                    psb = ['d']
                if last_dir == 'd':
                    psb = ['a']
            else:
                psb_flag , psb = group[i].possible(end_loc)

            if psb_flag:
                if psb[0] == 'w':
                    group[i].history.append('w')
                    group[i].map[x(group[i].myloc[0])-1 , y(group[i].myloc[1])] = 2
                if psb[0] == 's':
                    group[i].history.append('s')
                    group[i].map[x(group[i].myloc[0])+1 , y(group[i].myloc[1])] = 2
                if psb[0] == 'a':
                    group[i].history.append('a')
                    group[i].map[x(group[i].myloc[0]) , y(group[i].myloc[1])-1] = 2
                if psb[0] == 'd':
                    group[i].history.append('d')
                    group[i].map[x(group[i].myloc[0]) , y(group[i].myloc[1])+1] = 2
                
                flag = i
                break

            for j in range(len(psb)):
                if len(psb)-j == 1:
                    group[i].move(psb[j],apd=True)
                else:
                    new_map = cp.deepcopy(group[i])
                    new_map.move(psb[j],apd=True)
                    group.append(new_map)

        if flag != -1:
            break

    if prt:
        group[flag].map_print()

    road = []
    road_len = 1
    for i in range(len(group[flag].history)-1):
        if group[flag].history[i] == group[flag].history[i+1]:
            road_len += 1
        if (group[flag].history[i] == 'w' and group[flag].history[i+1] == 'a') or (
            group[flag].history[i] == 'a' and group[flag].history[i+1] == 's') or (
            group[flag].history[i] == 's' and group[flag].history[i+1] == 'd') or (
            group[flag].history[i] == 'd' and group[flag].history[i+1] == 'w'):
            road.append(road_len)
            road_len = 1
            road.append('l')
        if (group[flag].history[i+1] == 'w' and group[flag].history[i] == 'a') or (
            group[flag].history[i+1] == 'a' and group[flag].history[i] == 's') or (
            group[flag].history[i+1] == 's' and group[flag].history[i] == 'd') or (
            group[flag].history[i+1] == 'd' and group[flag].history[i] == 'w'):
            road.append(road_len)
            road_len = 1
            road.append('r')

    road.append(road_len)
    road.append('e')

    if len_mode:
        road_len = 0
        for date in road:
            if isinstance(date,int):
                road_len += date
            else:
                road_len += 1

        return road_len - 1 , group[flag].history[-1]

    return road , group[flag].history[-1]

def target_sort(targets_):
    targets_new = []
    targets = cp.deepcopy(targets_)
    last_dir = 'a'
    last_loc = [9,0]
    stst_i = -1
    stst_len = 9999
    
    while len(targets) > 0:
        for i in range(len(targets)):
            l , dirs = shortest_road(last_loc,targets[i],last_dir,targets,prt = False,len_mode = True)
            if l < stst_len:
                stst_len = l
                ok_dir = dirs
                stst_i = i
        
        print(last_loc)
        targets_new.append(targets.pop(stst_i))
        last_loc = targets_new[-1]
        stst_i = -1
        stst_len = -1
        last_dir = ok_dir
        stst_len = 9999

    return targets_new

if __name__ == '__main__':
    targets = [[9,2],
               [7,4],
               [7,6],
               [5,7],
               [0,7],
               [2,5],
               [4,2],
               [2,3]]
    print(shortest_road([9,0],[2,3],'a',targets,prt = True,len_mode = True))
