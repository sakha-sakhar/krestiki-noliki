import pygame
import sys
import random 

GAP = 10
WIDTH = 500
HEIGHT = WIDTH + 10 * GAP
SIZE = 25
CELLSIZE = (WIDTH - 20) / SIZE
WIN = 5

def terminate():
    pygame.quit()
    sys.exit()

def draw_board(board):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), 
         (GAP, GAP, WIDTH - GAP * 2, WIDTH - GAP * 2))
    pygame.draw.rect(screen, (255, 0, 0), 
         (GAP, WIDTH, WIDTH - GAP * 2, HEIGHT - WIDTH - GAP))
    for i in range(SIZE):
        coord = round(GAP + i * CELLSIZE)
        pygame.draw.line(screen, (0, 0, 0), [coord, GAP], [coord, WIDTH - GAP])
        pygame.draw.line(screen, (0, 0, 0), [GAP, coord], [WIDTH - GAP, coord])
    for i in range(SIZE):
        for j in range(SIZE):
            x0 = round(GAP + j * CELLSIZE) + 1
            y0 = round(GAP + i * CELLSIZE) + 1
            x1 = round(GAP + (j + 1) * CELLSIZE) - 1
            y1 = round(GAP + (i + 1) * CELLSIZE) - 1
            if board[i][j] == 2:
                pygame.draw.line(screen, (255, 0, 0), [x0, y0], [x1, y1], 2)
                pygame.draw.line(screen, (255, 0, 0), [x0, y1], [x1, y0], 2)
            elif board[i][j] == 1:
                pygame.draw.ellipse(screen, (0, 0, 255), [x0, y0, round(CELLSIZE - 1), round(CELLSIZE - 1)], 2)

def mouse_coord(mouse):
    if GAP < mouse[0] < WIDTH - GAP	and \
       GAP < mouse[1] < WIDTH - GAP:
        return (int((mouse[1] - GAP) // CELLSIZE), int((mouse[0] - GAP) // CELLSIZE))
    else:
        return None
    
def cell_free(board, coords):
    return board[coords[0]][coords[1]] == 0

def change_cell_state(board, coords, state):
    board[coords[0]][coords[1]] = state
    return board

def get_horz(board, coords):
    return [board[coords[0]][:coords[1]], [board[coords[0]][coords[1]]], board[coords[0]][1 + coords[1]:]]

def get_vert(board, coords):
    return [x[coords[1]] for x in board[:coords[0]]], [board[coords[0]][coords[1]]], [x[coords[1]] for x in board[coords[0] + 1:]]

def new_game_pressed(mouse):
    return WIDTH < mouse[1] < HEIGHT - GAP and GAP < mouse[0] < WIDTH - GAP

def get_diag1(board, coords):
    diag = sum(coords)
    res = [[], [], []]
    n = 0
    for i in range(SIZE):
        for j in range(SIZE):
            if (i, j) == tuple(coords):
                res[1].append(board[i][j])
                n = 2
            elif i + j == diag:
                res[n].append(board[i][j])
    return res

def get_diag2(board, coords):
    diag = coords[0] - coords[1]
    res = [[], [], []]
    n = 0
    for i in range(SIZE):
        for j in range(SIZE):
            if (i, j) == tuple(coords):
                res[1].append(board[i][j])
                n = 2
            elif i - j == diag:
                res[n].append(board[i][j])
    return res

def check_streak_n(seq, n):
    if len(seq) < n:
        return 0
    st = 0
    last = 0
    for i in seq:
        if i == last:
            st += 1
        else:
            last = i
            st = 1
        if last and st >= n:
            return last
    return 0

def check_side_closed(seq, n):
    if not seq:
        return 0
    if seq[0] == 0 or seq[-1] == 0:
        return 2
    return 1
    

def flatten_seq(seq):
    res = []
    for i in seq:
        res = res + i
    return res

def check_victory(board):
    victory = 0
    for i in range(SIZE):
        horz = flatten_seq(get_horz(board, [i, 0]))
        vert = flatten_seq(get_vert(board, [0, i]))
        victory = check_streak_n(horz, WIN)
        if victory:
            return victory
        victory = check_streak_n(vert, WIN)
        if victory:
            return victory
    for i in range(SIZE):
        diag = flatten_seq(get_diag1(board, [i, i]))
        victory = check_streak_n(diag, WIN)
        if victory:
            return victory
        if i < SIZE - 1:
            diag = flatten_seq(get_diag1(board, [i, i + 1]))
            victory = check_streak_n(diag, WIN)
            if victory:
                return victory
    for i in range(SIZE):
        diag = flatten_seq(get_diag2(board, [SIZE - i - 1, i]))
        victory = check_streak_n(diag, WIN)
        if victory:
            return victory
        if i < SIZE - 1:
            diag = flatten_seq(get_diag2(board, [SIZE - i - 1, i + 1]))
            victory = check_streak_n(diag, WIN)
            if victory:
                return victory
    return victory

def computer(board):
    max_priority_cells = [[0, 0]]
    max_priority = 0
    for i in range(SIZE):
        for j in range(SIZE):
            priority = 0
            if board[i][j]:
                continue
            seqs = [get_horz(board, [i, j]), get_vert(board, [i, j]), get_diag1(board, [i, j]), get_diag2(board, [i, j])]
            for x in range(1, WIN):
                for b in seqs:
                    streak1 = check_streak_n(b[0][-x:], x) * check_side_closed(b[0][-x-1:], x)
                    streak2 = check_streak_n(b[2][:x], x) * check_side_closed(b[2][:x+1], x)
                    priority += (x ** 3) * ((streak1 + streak2) ** 2)
                    if (streak1 or streak2) and x == WIN - 1:  # значит, у кого-то есть 4 в ряд рядом с данной клеткой и она свободна
                        if streak1 == 1 or streak2 == 1:
                            return [i, j]
                        priority = float('inf')
            if priority > max_priority:
                max_priority = priority
                max_priority_cells = [[i, j]]
            elif priority == max_priority:
                max_priority_cells.append([i, j])
    if not cell_free(board, max_priority_cells[0]):
        while True:
            max_priority_cells = [[random.randint(0, SIZE - 1), random.randint(0, SIZE - 1)]]
            if cell_free(board, max_priority_cell):
                break
    return random.choice(max_priority_cells)

def main():
    board = []
    for _ in range(SIZE):
        board.append([0] * SIZE)
    running = True
    victory = 0
    while running:
        pygame.display.flip()
        events = pygame.event.get()
        for event in events:
            mouse = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                crds = mouse_coord(mouse)
                if crds and cell_free(board, crds) and not victory:
                    board = change_cell_state(board, crds, 2)
                    victory = check_victory(board)
                    if not victory:
                        print('комп думает...')
                        board = change_cell_state(board, computer(board), 1)
                        print('комп сделал ход')
                        victory = check_victory(board)
                elif new_game_pressed(mouse):
                    running = False
                
        draw_board(board)

if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('Мяу')
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    while True:
        main()
    pygame.quit()