# 제품 재고를 저장할 딕셔너리
inventory = {}

def add_product(name, quantity):
    inventory[name] = quantity

def print_products():
    for name, quantity in inventory.items():
        print(f"제품명 : {name}, 수량 : {quantity}")

def print_products_by_quantity(threshold):
    for name, quantity in inventory.items():
        if quantity <= threshold:
            print(f"제품명 : {name}, 수량 : {quantity}")

def save_products_to_file(filename):
    with open(filename, 'w') as file:
        for name, quantity in inventory.items():
            file.write(f"{name},{quantity}\n")

def load_products_from_file(filename):
    global inventory
    inventory = {}
    with open(filename, 'r') as file:
        for line in file:
            name, quantity = line.strip().split(',')
            inventory[name] = int(quantity)

# 예제 사용
add_product("사과", 10)
add_product("바나나", 5)
print("<모든 제품 출력>")
print_products()
print("\n<수량이 5 이하인 제품>")
print_products_by_quantity(5)
save_products_to_file("inventory.txt")
inventory = {}  # 초기화
load_products_from_file("inventory.txt")
print("\n<파일에서 로드한 제품 출력>")
print_products()