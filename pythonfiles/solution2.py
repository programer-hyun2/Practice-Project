def func_a(tl):
    i = 0
    while True:
        if tl[i] == 1:
            return i
        i += 1
          
def func_b(tl):
    i = len(tl)-1
    while True:
        if tl[i] == 1:
            return i
        i -= 1
    
def func_c(tl,st,ed):
    r = 0
    while st <= ed:
        if tl[st] == 0:
            r += 1
        st += 1
    return r

def solution(tt):
    return func_c(tt,func_a(tt),func_b(tt))
    
time_table = [1,1,0,0,1,0,1,0,0,0]
print(solution(time_table))