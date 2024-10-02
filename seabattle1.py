class BoardOutException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class AlreadyShot(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Dot():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Ship:
    def __init__(self, length, nose_dot, direction, lives):
        self.length = length
        self.nose_dot = nose_dot
        self.direction = direction
        self.lives = lives

    def dots(self):
        dots = []
        if self.direction == "горизонтальное":
            for i in range(self.length):
                dots.append(Dot(self.nose_dot.x + i, self.nose_dot.y))
        elif self.direction == "вертикальное":
            for i in range(self.length):
                dots.append(Dot(self.nose_dot.x, self.nose_dot.y + i))
        return dots


class Board:
    def __init__(self, hid=False, size = 6):
        self.hid = hid
        self.ships = []
        self.board = [['O' for _ in range(size)] for _ in range(size)]
        self.busy = []
        self.size = size
        self.alive_ships = 0

    def __str__(self):
        result = []

        x = "   | " + " | ".join(map(str, range(1, self.size + 1))) + " |"
        result.append(x)
        result.append("-" * len(x))

        for i in range(self.size):
            y = f"{i + 1} | " + " | ".join("O" if self.hid and cell== "■" else cell for cell in self.board[i]) + " |"
            result.append(y)

        return "\n".join(result)
    def add_ship(self, ship):
        for dot in ship.dots():
            if self.out(dot) or dot in self.busy:
                raise BoardOutException("Место занято или за пределами поля!")

        for dot in ship.dots():
            self.board[dot.y][dot.x] = '■'
            self.busy.append(dot)

        self.contour(ship)
        self.ships.append(ship)
        self.alive_ships += 1

    def contour(self, ship, show=False):
        around = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for dot in ship.dots():
            for dx, dy in around:
                cur = Dot(dot.x + dx, dot.y + dy)
                if not self.out(cur) and cur not in self.busy:
                    self.busy.append(cur)
                    if show:
                        if self.board[cur.y][cur.x] != 'X':
                            self.board[cur.y][cur.x] = '.'

    def out(self, dot):
        result = not (0 <= dot.x < self.size and 0 <= dot.y < self.size)
        return result

    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException("Выстрел за пределами игрового поля!")
        if self.board[dot.y][dot.x] in ['.', 'T', 'X']:
            raise AlreadyShot ("Вы уже стреляли сюда!")
            pass

        for ship in self.ships:
            if dot in ship.dots():
                ship.lives -= 1
                self.board[dot.y][dot.x] = 'X'
                if ship.lives == 0:
                    self.alive_ships -= 1
                    print("Корабль уничтожен!")
                    self.contour(ship, show=True)
                    return True
                else:
                    print("Корабль подбит!")
                    return True

        self.board[dot.y][dot.x] = 'T'
        print("Промах!")
        return False


class Player:
    def __init__(self,my_board, enemy_board):
        self.my_board = my_board
        self.enemy_board = enemy_board
    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardOutException as e:
                print(e)
            except AlreadyShot as e:
                print(e)


import random

class AI(Player):
    def ask(self):
        dot = Dot(random.randint(0,self.enemy_board.size - 1), random.randint(0,self.enemy_board.size - 1))
        print(f'AI shot at {dot.x + 1}, {dot.y + 1}')
        return dot

class User (Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()
            if len(cords) != 2:
                print("Нужно ввести 2 координаты!")
                continue

            x,y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                    print ("Введите числа!")
                    continue

            x, y = int(x) - 1 , int(y) - 1

            return Dot(x,y)

class Game:
    def __init__(self):
        player = self.random_board()
        comp = self.random_board()
        comp.hid = False

        self.ai = AI (comp, player)
        self.user = User (player, comp)

    def random_board(self):
        attempts = 0
        board = Board ( )
        lengths = [3, 2, 2, 1, 1, 1, 1]
        for length in lengths:
            while True:
                attempts += 1
                if attempts > 1000:
                    return self.random_board()
                x = random.randint(0, board.size - 1)
                y = random.randint(0, board.size - 1)
                direction = random.choice(["горизонтальное", "вертикальное"])
                ship = Ship(length, Dot(x, y), direction, length)

                try:
                    board.add_ship(ship)
                    break
                except BoardOutException:
                    continue
        board.busy = []
        return board


    def greet(self):
        print("Добро пожаловать в игру 'Морской бой в консоли!!!'")
        print("----------------------------------------------------")
        print("Формат ввода: 'x y' ")
        print(', где "x" - номер строки')
        print(', а "y" - номер столбца')
        print("----------------------------------------------------")
        print("Желаем приятной игры!")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.user.my_board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.user.enemy_board)
            if num % 2 == 0:
                print("Ход пользователя!")
                repeat = self.user.move()
            else:
                print("Ход компьютера!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.user.enemy_board.alive_ships == 0:
                # self.user.enemy_board == 0:
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.user.my_board.alive_ships == 0:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start (self):
        self.greet()
        self.loop()
g = Game()
g.start()
