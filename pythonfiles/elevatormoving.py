def solution(fl):
    elevatormoves = 0
    currentfloor = fl[0]
    for floor in fl:
        elevatormoves += abs(floor - currentfloor)
        currentfloor = floor
    return elevatormoves

print(solution([1,2,5,4,2]))
