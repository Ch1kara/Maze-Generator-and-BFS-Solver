from heapq import heapify, heappop, heappush
import pygame as pg
from pygame.locals import *
import sys
from random import choice

# screen size and title at the top
screen_width = 1302
screen_height = 802
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Maze and Dijkstra's")

pg.init()
clock = pg.time.Clock()
sq_size = 50
cols, rows = screen_width // sq_size, screen_height // sq_size  # making a (col, row) grid out of entire screen


def create_button(x, y, width, height, text):
    """Creates button rectangle that is highlighted when cursor hovers over it"""
    # create base button rectangle
    button = pg.Rect(x, y, width, height)

    # position of the mouse
    cursor_pos = pg.mouse.get_pos()
    cursor_hover = button.collidepoint(cursor_pos)

    # makes outline of box gold if cursor is on it
    if cursor_hover:
        pg.draw.rect(screen, pg.Color('white'), button)
        pg.draw.rect(screen, pg.Color('gold'), button, 3)
    else:
        pg.draw.rect(screen, pg.Color('white'), button)
        pg.draw.rect(screen, pg.Color('white'), button, 3)

    # adds text to the box after everything else
    font = pg.font.SysFont('squaresans', 30)
    text = font.render(f'{text}', True, pg.Color('black'))
    text_rect = text.get_rect(center=button.center)
    screen.blit(text, text_rect)
    pg.display.update()
    return button


def dijkstra_heap(G, s):
    # graph G, start node s
    # uses HEAP to speed up min spanning edge
    # return dictionary of distance to each other node
    heap = []
    for c_node in G[s]:
        item = (c_node[1], s, c_node[0])
        heap.append(item)
    heapify(heap)

    E = {s}
    dist = {s: 0}

    while len(E) < len(G):
        min_element = heappop(heap)
        E.add(min_element[2])
        dist[min_element[2]] = dist[min_element[1]] + min_element[0]

        for c_node in G[min_element[2]]:
            item = (c_node[1], min_element[2], c_node[0])
            if c_node[0] not in E:
                heappush(heap, item)

    return dist


class Maze:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.l_border = True
        self.r_border = True
        self.t_border = True
        self.b_border = True
        self.explored = False  # so that we can make the maze paths

    def draw_sq(self):
        """Used for generating the original graph, modular so that sides can be removed to create maze"""
        # square is defined by top left corner
        x, y = self.x * sq_size, self.y * sq_size  # scaling the locations on screen
        if self.explored:
            pg.draw.rect(screen, pg.Color('violetred1'), (x, y, sq_size, sq_size))

        if self.l_border:
            pg.draw.line(screen, pg.Color('white'), (x, y + sq_size), (x, y), 2)
        if self.r_border:
            pg.draw.line(screen, pg.Color('white'), (x + sq_size, y), (x + sq_size, y + sq_size), 2)
        if self.t_border:
            pg.draw.line(screen, pg.Color('white'), (x, y), (x + sq_size, y), 2)
        if self.b_border:
            pg.draw.line(screen, pg.Color('white'), (x + sq_size, y + sq_size), (x, y + sq_size), 2)

    def current_sq(self):
        """highlights the current square that the algorithm is looking at"""
        x, y = self.x * sq_size, self.y * sq_size  # scaling the locations on screen
        pg.draw.rect(screen, pg.Color('plum2'), (x + 2, y + 2, sq_size - 2, sq_size - 2))

    # next two functions are for choosing the next cells when creating the maze

    def check_sq(self, x, y):
        """Checks to see that the chosen cell isn't out of the grid"""
        # looked up formula for finding index based on x and y
        find_ind = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return graph[find_ind(x, y)]  # returns the chosen cell in the given graph form

    def choose_next(self):
        """Randomly chooses a neighboring node out of the available ones"""
        neighboring_cells = []
        U = self.check_sq(self.x, self.y - 1)
        D = self.check_sq(self.x, self.y + 1)
        L = self.check_sq(self.x - 1, self.y)
        R = self.check_sq(self.x + 1, self.y)

        if U and not U.explored:
            neighboring_cells.append(U)
        if D and not D.explored:
            neighboring_cells.append(D)
        if L and not L.explored:
            neighboring_cells.append(L)
        if R and not R.explored:
            neighboring_cells.append(R)

        if neighboring_cells:
            return choice(neighboring_cells)
        else:
            return False

    @staticmethod
    def remove_border(current_n, next_n):
        """Given the current and next nodes, gets rid of the wall between them"""
        distance_x = current_n.x - next_n.x
        distance_y = current_n.y - next_n.y
        if distance_x == 1:
            current_n.l_border = False
            next_n.r_border = False
        elif distance_x == -1:
            current_n.r_border = False
            next_n.l_border = False
        if distance_y == 1:
            current_n.t_border = False
            next_n.b_border = False
        elif distance_y == -1:
            current_n.b_border = False
            next_n.t_border = False


status = 'norm'
graph = [Maze(j, i) for i in range(rows) for j in range(cols)]
current_n = graph[0]
stack = []

while status != 'quit':
    for event in pg.event.get():
        if event.type == pg.QUIT:
            status = 'quit'

        if event.type == pg.MOUSEBUTTONDOWN:
            click_loc = event.pos
            if status == 'norm':
                if quit_b.collidepoint(click_loc):
                    status = 'quit'
                if gen_b.collidepoint(click_loc):
                    status = 'generate'

        if event.type == pg.key.get_pressed():
            keys = pg.key.get_pressed()
            if keys[K_SPACE]:
                status = 'solve'

    if status == 'norm':
        quit_b = create_button(600, 100, 100, 100, "quit")
        gen_b = create_button(570, 300, 160, 100, "Generate Maze")

    if status == 'generate':
        screen.fill(pg.Color('black'))
        for node in graph:
            node.draw_sq()

        current_n.explored = True
        current_n.current_sq()

        next_node = current_n.choose_next()
        if next_node:
            next_node.explored = True
            stack.append(current_n)
            current_n.remove_border(current_n, next_node)
            current_n = next_node
        elif stack:
            current_n = stack.pop()  # start the "DFS" again once the prior loop reaches a dead end

    if status == 'solve':
        start = choice(graph)
        end = choice(graph)
        if start != end:
            pass

    pg.display.flip()
    clock.tick(30)

pg.quit()
sys.exit()
