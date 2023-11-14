import pygame as pg
import sys
from random import choice
from collections import deque

# STUFF I WAS GOING TO USE FOR DIJKSTRA's
from heapq import heapify, heappop, heappush
from collections import defaultdict

# screen size and title at the top
screen_width = 1403
screen_height = 803
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Maze and Dijkstra's")

pg.init()
clock = pg.time.Clock()
sq_size = 100  # HOW YOU CHANGE THE MAZE SIZE(MAKE SURE IT'S A MULTIPLE OF BOTH THE SCREEN WIDTH AND HEIGHT)
cols, rows = screen_width // sq_size, screen_height // sq_size  # making a (col, row) grid out of entire screen


def create_button(x, y, width, height, txt_size, text):
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
    font = pg.font.SysFont('squaresans', txt_size)
    text = font.render(f'{text}', True, pg.Color('black'))
    text_rect = text.get_rect(center=button.center)
    screen.blit(text, text_rect)
    pg.display.update()
    return button


# def dijkstra_maze(maze_graph, start, end):
#     """Takes in the maze graph and does all the effects with pygame"""
#     heap = []
#     # dist = {start: 0}
#     E = {start}
#     current = start
#     paths = defaultdict(list)
#     paths[start].append(start)
#
#     while len(E) != len(maze_graph):
#         for c_node in maze_graph[current]:
#             if c_node not in E:
#                 print('about to push')
#                 heappush(heap, (0, 'hello'))
#                 print("heap pushed")
#
#         min_element = heappop(heap)
#         print(min_element)
#
#         if min_element[1] not in E:
#             paths[min_element[1]].append(current)
#             E.add(min_element[1])
#             # dist[min_element] = min_element[0] don't know where to add distances right now
#             current = min_element[1]
#     final_path = [current]
#     path_found = False
#     while not path_found:
#         for vertex in paths:
#             if vertex == paths[current]:
#                 final_path.append(vertex)
#                 current = vertex
#         if current == start:
#             path_found = True
#
#     return final_path


def BFS_maze(maze_graph, start_n, end_n):
    """Takes in a maze graph and returns dictionary with discovered node as key and prev node as value"""
    E = set()  # HAD {START} IN HERE INITIALLY BUT SAID THAT "NODE OBJECT NOT ITERABLE"
    Queue = deque([start_n])
    paths = {}
    while len(Queue) > 0:
        vertex = Queue.popleft()
        for node in maze_graph[vertex]:
            if node not in E:
                E.add(node)
                Queue.append(node)
                paths[node] = vertex

    return paths  # each key(a node) has one value(the node that discovered the key)


def patch_path_together(all_paths, start_n, end_n):
    current_node = end_n
    final_solution = [end_n]
    while current_node != start_n:
        final_solution.append(all_paths[current_node])  # node that discovered end
        current_node = paths[current_node]

    return final_solution[::-1]  # since the value is the node that discovered the key, we need to reverse the solution



class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.node = (x, y)  # USED FOR DEBUGGING
        self.l_border = True
        self.r_border = True
        self.t_border = True
        self.b_border = True
        self.explored = False  # so that we can make the maze paths
        self.neighbors = []

    def draw_sq(self):
        """Used for generating the original graph, modular so that sides can be removed to create maze"""
        # square is defined by top left corner
        x, y = self.x * sq_size, self.y * sq_size  # scaling the locations on screen
        if self.explored:
            pg.draw.rect(screen, pg.Color('violetred1'), (x, y, sq_size, sq_size))

        if self.l_border:
            pg.draw.line(screen, pg.Color('white'), (x, y + sq_size), (x, y), 3)
        if self.r_border:
            pg.draw.line(screen, pg.Color('white'), (x + sq_size, y), (x + sq_size, y + sq_size), 3)
        if self.t_border:
            pg.draw.line(screen, pg.Color('white'), (x, y), (x + sq_size, y), 3)
        if self.b_border:
            pg.draw.line(screen, pg.Color('white'), (x + sq_size, y + sq_size), (x, y + sq_size), 3)

    def draw_current_sq(self):
        """highlights the current square that the algorithm is looking at"""
        x, y = self.x * sq_size, self.y * sq_size  # scaling the locations on screen
        pg.draw.rect(screen, pg.Color('plum2'), (x + 2, y + 2, sq_size - 2, sq_size - 2))

    # next two functions are for choosing the next cells when creating the maze

    def check_sq(self, x, y):
        """Checks to see that the chosen cell isn't out of the grid"""
        # Maze list goes down columns before spanning the rows
        find_ind = lambda x, y: x + y * cols  # math'd
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:  # if cell out of range
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

    # (1, 2) (0, 2)
    # dx = 1, dy = 0

    def find_connected(self):
        """Checks for the connected nodes to a give node at anytime"""
        # Maze list goes down the columns first then goes by the rows next
        if not self.l_border:
            c_node = self.check_sq(self.x - 1, self.y)  # WE SPENT THREE HOURS DEBUGGING FOR A -1 in the Y INSTEAD OF X
            if c_node is not False:  # returns false if none: issues with comparing bool to NODE object with HEAPS
                self.neighbors.append(c_node)

        if not self.r_border:
            c_node = self.check_sq(self.x + 1, self.y)
            if c_node is not False:
                self.neighbors.append(c_node)

        if not self.t_border:
            c_node = self.check_sq(self.x, self.y - 1)
            if c_node is not False:
                self.neighbors.append(c_node)

        if not self.b_border:
            c_node = self.check_sq(self.x, self.y + 1)
            if c_node is not False:
                self.neighbors.append(c_node)

        return self.neighbors

    def change_color(self, color):
        """Used for changing the color of final path, modular given removed sides in maze"""
        # square is defined by top left corner
        x, y = self.x * sq_size, self.y * sq_size  # scaling the locations on screen
        pg.draw.rect(screen, pg.Color(color), (x, y, sq_size, sq_size))

        if self.l_border:
            pg.draw.line(screen, pg.Color('white'), (x, y + sq_size), (x, y), 3)
        if self.r_border:
            pg.draw.line(screen, pg.Color('white'), (x + sq_size, y), (x + sq_size, y + sq_size), 3)
        if self.t_border:
            pg.draw.line(screen, pg.Color('white'), (x, y), (x + sq_size, y), 3)
        if self.b_border:
            pg.draw.line(screen, pg.Color('white'), (x + sq_size, y + sq_size), (x, y + sq_size), 3)


status = 'norm'
graph = [Node(j, i) for i in range(rows) for j in range(cols)]  # columns go before rows for some reason
current_n = graph[0]  # arbitrary start point for drawing the maze
stack = []  # STACK FOR DFS
maze_graph = {}  # USED FOR FINAL PATH AND GENERAL MAZE
start = ''
end = ''
chosen = False  # used for choosing the start and end points for the maze

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
            if status == 'solved':
                if quit_b.collidepoint(click_loc):
                    status = 'quit'

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                status = 'reveal'

            if event.key == pg.K_SPACE:
                status = 'solving'

        if status == 'reveal':
            if type(start) == str or type(end) == str:
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:  # if you press r again then you will generate a new start and end
                    start.change_color('violetred1')  # change the colors back to the maze color
                    end.change_color('violetred1')
                    chosen = False

    if status == 'norm':
        quit_b = create_button(610, 100, 180, 100, 60, "quit")
        gen_b = create_button(400, 300, 600, 150, 100, "Generate Maze")

    if status == 'generate':
        screen.fill(pg.Color('black'))
        for node in graph:
            node.draw_sq()

        current_n.explored = True
        current_n.draw_current_sq()

        next_node = current_n.choose_next()
        if next_node:
            next_node.explored = True
            stack.append(current_n)
            current_n.remove_border(current_n, next_node)
            # TEMP
            current_n = next_node
        elif stack:
            current_n = stack.pop()  # start the "DFS" again once the prior loop reaches a dead end

    if status == 'reveal': # REVEALS A RANDOMLY CHOSEN START AND END FOR THE MAZE
        for node in graph:
            neighbors = node.find_connected()
            # print(f"{node.node}:{neighbors}") # DEBUGGING STUFF
            # print("VERTEX:" + str(node.node))
            #
            # print("NEIGHBORS:" + str(neighbors))
            maze_graph[node] = neighbors
        if not chosen:
            start = choice(list(maze_graph.keys()))
            end = choice(list(maze_graph.keys()))
            start.change_color('purple1')
            end.change_color('purple1')
            if start == end:  # SHOULD PICK A NEW START AND END IF THEY ARE THE SAME
                continue
        chosen = True

    if status == 'solving':

        paths = BFS_maze(maze_graph, start, end)
        final_path = patch_path_together(paths, start, end)
        for node in final_path:
            node.change_color('turquoise')

        final_path[0].change_color('purple1')  # HIGHLIGHT START AND END
        final_path[-1].change_color('purple1')

        status = 'solved'

    if status == 'solved':
        quit_b = create_button(620, 350, 160, 100, 30, "quit?")

    pg.display.flip()
    clock.tick(30)

pg.quit()
sys.exit()
