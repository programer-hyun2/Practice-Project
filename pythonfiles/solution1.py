
def solution(s,c):
    result = 0
    for car in c:
        if car/s >= 1.3:
            result += 7
        elif car/s >= 1.2:
            result += 5
        elif car/s >=  1.1:
            result += 3
        print(result)
    return result

speed = 100
cars = [110, 98, 125, 148, 120, 112, 89]
print(solution(speed, cars))