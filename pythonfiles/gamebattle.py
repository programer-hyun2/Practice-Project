def solution(attack,recovery,hp):
    while hp > 0:
        attacktime += 1
        hp -= attack
        if hp <= 0:
            break
        hp += recovery
    return attacktime

print(solution(30,10,70))