import pygame
from collections import deque

WIDTH = 600
ROWS = 30
WIN = pygame.display.set_mode((WIDTH, WIDTH + 60))
pygame.display.set_caption("Pathfinder Visualiser")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
GREEN = (0, 200, 0)
RED = (220, 0, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 220, 0)
PURPLE = (160, 0, 220)
DARK_GREY = (40, 40, 40)
LIGHT_BLUE = (173, 216, 230)

class Cell:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.width = width
        self.colour = WHITE
        self.neighbours = []

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def get_neighbours(self, grid):
        self.neighbours = []
        if self.row > 0 and grid[self.row-1][self.col].colour != BLACK:
            self.neighbours.append(grid[self.row-1][self.col])
        if self.row < ROWS-1 and grid[self.row+1][self.col].colour != BLACK:
            self.neighbours.append(grid[self.row+1][self.col])
        if self.col > 0 and grid[self.row][self.col-1].colour != BLACK:
            self.neighbours.append(grid[self.row][self.col-1])
        if self.col < ROWS-1 and grid[self.row][self.col+1].colour != BLACK:
            self.neighbours.append(grid[self.row][self.col+1])

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([Cell(i, j, gap) for j in range(rows)])
    return grid

def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width, message="LEFT click: start → end → walls   |   RIGHT click: erase   |   SPACE: run   |   R: reset"):
    win.fill(DARK_GREY)
    for row in grid:
        for cell in row:
            cell.draw(win)
    draw_grid_lines(win, rows, width)
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 13)
    text = font.render(message, True, (200, 200, 200))
    win.blit(text, (10, width + 18))
    pygame.display.update()

def get_clicked_cell(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = y // gap
    col = x // gap
    return min(row, rows-1), min(col, rows-1)

def reconstruct_path(came_from, current, draw_fn):
    while current in came_from:
        current = came_from[current]
        current.colour = YELLOW
        draw_fn()
        pygame.time.delay(20)

def bfs(draw_fn, grid, start, end):
    queue = deque([start])
    came_from = {}
    visited = {start}

    while queue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        current = queue.popleft()

        if current == end:
            reconstruct_path(came_from, end, draw_fn)
            end.colour = RED
            start.colour = GREEN
            draw_fn()
            return True

        current.get_neighbours(grid)
        for neighbour in current.neighbours:
            if neighbour not in visited:
                visited.add(neighbour)
                came_from[neighbour] = current
                neighbour.colour = LIGHT_BLUE
                queue.append(neighbour)

        if current != start:
            current.colour = BLUE

        draw_fn()
        pygame.time.delay(10)

    return False

def reset_grid(grid, start, end):
    for row in grid:
        for cell in row:
            if cell.colour not in (BLACK, GREEN, RED):
                cell.colour = WHITE
    return start, end

def main():
    pygame.init()
    grid = make_grid(ROWS, WIDTH)
    start = None
    end = None
    running_bfs = False
    run = True

    while run:
        draw(WIN, grid, ROWS, WIDTH)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[1] < WIDTH:
                    row, col = get_clicked_cell(pos, ROWS, WIDTH)
                    cell = grid[row][col]
                    if not start and cell != end:
                        start = cell
                        start.colour = GREEN
                    elif not end and cell != start:
                        end = cell
                        end.colour = RED
                    elif cell != start and cell != end:
                        cell.colour = BLACK

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[1] < WIDTH:
                    row, col = get_clicked_cell(pos, ROWS, WIDTH)
                    cell = grid[row][col]
                    cell.colour = WHITE
                    if cell == start:
                        start = None
                    elif cell == end:
                        end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not running_bfs:
                    running_bfs = True
                    found = bfs(lambda: draw(WIN, grid, ROWS, WIDTH, "Running BFS..."), grid, start, end)
                    msg = "Path found! R to reset." if found else "No path found. R to reset."
                    draw(WIN, grid, ROWS, WIDTH, msg)
                    running_bfs = False

                if event.key == pygame.K_r:
                    grid = make_grid(ROWS, WIDTH)
                    start = None
                    end = None
                    running_bfs = False

    pygame.quit()

main()