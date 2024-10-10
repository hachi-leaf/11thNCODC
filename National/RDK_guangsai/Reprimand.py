import copy as cp
def rep(point,cls,plist):
    def quadrant(p):
        if p[0] <= 4 and p[1] >= 5:
            return 1
        if p[0] <= 4 and p[1] <= 4:
            return 2
        if p[0] >= 5 and p[1] <= 4:
            return 3
        if p[0] >= 5 and p[1] >= 5:
            return 4
        
    list_new = cp.deepcopy(plist)
    if [0,9] in plist:
        list_new.remove([0,9])

    for pnt in list_new:
        if pnt == [0,9]:
            continue
            
        print(pnt,quadrant(pnt), quadrant(point))

        if cls:
            if quadrant(pnt) == quadrant(point):
                list_new.remove(pnt)
            if abs(quadrant(pnt) - quadrant(point)) == 2 and pnt[0]+point[0] == 9 and pnt[1]+point[1] == 9:
                list_new.remove(pnt)

        if not cls:
            if abs(quadrant(pnt) - quadrant(point)) == 2 and not (pnt[0]+point[0] == 9 and pnt[1]+point[1] == 9):
                list_new.remove(pnt)

    list_new.append([0,9])

    return list_new

if __name__ == '__main__':
    targets = [[7,2],
               [7,5],
               [8,8],
               [1,1],
               [2,4],
               [2,7],
               [3,5],
               [0,9]]
    
    print(rep([6,4],True,targets))
    