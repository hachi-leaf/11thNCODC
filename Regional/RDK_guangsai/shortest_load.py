def shortest_load(loc_go,loc_end,prt=False,vim_8_3=False,vim_7_5=False):
    import numpy as np
    import copy as cp
    class map():
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

        def my_loc(self,loc):
            self.loc = loc
            self.map[loc[0]*2+1,loc[1]*2+1] = -1

        def possible(self):
            psb = []
            if self.map[self.loc[0]*2+1 -1, self.loc[1]*2+1] == 1 and self.map[self.loc[0]*2+1 -2, self.loc[1]*2+1] == 1:
                psb.append('w')
            if self.map[self.loc[0]*2+1 +1, self.loc[1]*2+1] == 1 and self.map[self.loc[0]*2+1 +2, self.loc[1]*2+1] == 1:
                psb.append('s')
            if self.map[self.loc[0]*2+1, self.loc[1]*2+1 -1] == 1 and self.map[self.loc[0]*2+1, self.loc[1]*2+1 -2] == 1:
                psb.append('a')
            if self.map[self.loc[0]*2+1, self.loc[1]*2+1 +1] == 1 and self.map[self.loc[0]*2+1, self.loc[1]*2+1 +2] == 1:
                psb.append('d')
        
            return psb
        
        def node_psb(self):
            psb = []
            if self.map[self.loc[0]*2+1 -1, self.loc[1]*2+1] != 0 and self.map[self.loc[0]*2+1 -2, self.loc[1]*2+1] != 0:
                psb.append('w')
            if self.map[self.loc[0]*2+1 +1, self.loc[1]*2+1] != 0 and self.map[self.loc[0]*2+1 +2, self.loc[1]*2+1] != 0:
                psb.append('s')
            if self.map[self.loc[0]*2+1, self.loc[1]*2+1 -1] != 0 and self.map[self.loc[0]*2+1, self.loc[1]*2+1 -2] != 0:
                psb.append('a')
            if self.map[self.loc[0]*2+1, self.loc[1]*2+1 +1] != 0 and self.map[self.loc[0]*2+1, self.loc[1]*2+1 +2] != 0:
                psb.append('d')
        
            return psb
        
        def move(self,dir,apd=False):
            if dir == 'w':
                self.map[self.loc[0]*2+1 -2, self.loc[1]*2+1] = -1
                self.map[self.loc[0]*2+1 -1, self.loc[1]*2+1] = -1
                self.loc[0] -= 1
                if apd:
                    self.history.append('w')

            if dir == 's':
                self.map[self.loc[0]*2+1 +2, self.loc[1]*2+1] = -1
                self.map[self.loc[0]*2+1 +1, self.loc[1]*2+1] = -1
                self.loc[0] += 1
                if apd:
                    self.history.append('s')

            if dir == 'a':
                self.map[self.loc[0]*2+1, self.loc[1]*2+1 -2] = -1
                self.map[self.loc[0]*2+1, self.loc[1]*2+1 -1] = -1
                self.loc[1] -= 1
                if apd:
                    self.history.append('a')

            if dir == 'd':
                self.map[self.loc[0]*2+1, self.loc[1]*2+1 +2] = -1
                self.map[self.loc[0]*2+1, self.loc[1]*2+1 +1] = -1
                self.loc[1] += 1
                if apd:
                    self.history.append('d')

        def printmap(self):
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
                    if self.map[i,j] == -1:
                        print('*',end=' ')
                print()
            print("|")
            print('^')
            print('x')

    first_sam = map()
    group = [first_sam]
    group[0].my_loc(loc_go)
    flag = -1
    
    if vim_8_3:
        group[0].map[8*2+1 - 1, 3*2+1] = 0
        group[0].map[1*2+1 + 1, 6*2+1] = 0
        
    if vim_7_5:
        group[0].map[7*2+1 + 1, 5*2+1] = 0
        group[0].map[2*2+1 - 1, 4*2+1] = 0
        
    
    while True:
        for i in range(len(group)):
            if group[i].loc == loc_end:
                flag = i
                break
            node_psb = group[i].node_psb()
            if len(node_psb) != 2:
                node = True
            else:
                if 'w' in node_psb and 's' in node_psb:
                    node = False
                elif 'a' in node_psb and 'd' in node_psb:
                    node = False
                else:
                    node = True

            psb = group[i].possible()

            for j in range(len(psb)):
                if len(psb)-j == 1:
                    group[i].move(psb[j],apd=node)
                else:
                    new_map = cp.deepcopy(group[i])
                    new_map.move(psb[j],apd=node)
                    group.append(new_map)

        if flag != -1:
            break

    if prt:
        group[flag].printmap()
    load = []
    for i in range(len(group[flag].history)-1):
        if group[flag].history[i+1] == group[flag].history[i]:
            load.append(1) 
        elif group[flag].history[i+1] == "a" and group[flag].history[i] == "w":
            load.append(2)
        elif group[flag].history[i+1] == "w" and group[flag].history[i] == "d":
            load.append(2)
        elif group[flag].history[i+1] == "d" and group[flag].history[i] == "s":
            load.append(2)
        elif group[flag].history[i+1] == "s" and group[flag].history[i] == "a":
            load.append(2)
        elif group[flag].history[i+1] == "d" and group[flag].history[i] == "w":
            load.append(3)
        elif group[flag].history[i+1] == "s" and group[flag].history[i] == "d":
            load.append(3)
        elif group[flag].history[i+1] == "a" and group[flag].history[i] == "s":
            load.append(3)
        elif group[flag].history[i+1] == "w" and group[flag].history[i] == "a":
            load.append(3)
            
    if loc_end == [0,9]:
        load.append(5)

    return load
    

print(shortest_load([9,0],[0,9],prt=True))
