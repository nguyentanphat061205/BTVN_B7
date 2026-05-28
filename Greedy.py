import tkinter as tk
from tkinter import messagebox
import heapq
import time


class Node:
    def __init__(self, state, parent=None, action=None, depth=0, h_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth
        self.h_cost = h_cost 

    def __lt__(self, other):
        return self.h_cost < other.h_cost


def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def calculate_manhattan_distance(current_state, goal_state):


    goal_pos = {}
    for r in range(3):
        for c in range(3):
            goal_pos[goal_state[r][c]] = (r, c)

    distance = 0
    for r in range(3):
        for c in range(3):
            val = current_state[r][c]
            if val != 0: 
                target_r, target_c = goal_pos[val]
                distance += abs(r - target_r) + abs(c - target_c)
    return distance


def generate_children(node, goal_state):
    children = []
    x, y = find_zero(node.state)
    moves = [(-1, 0, "UP"), (1, 0, "DOWN"), (0, -1, "LEFT"), (0, 1, "RIGHT")]
    for dx, dy, action in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            new_state = [row[:] for row in node.state]
            new_state[x][y], new_state[nx][ny] = (
                new_state[nx][ny],
                new_state[x][y],
            )

            h_cost = calculate_manhattan_distance(new_state, goal_state)

            child = Node(
                state=new_state,
                parent=node,
                action=action,
                depth=node.depth + 1,
                h_cost=h_cost,
            )
            children.append(child)
    return children


def get_solution(goal_node):
    path = []
    current = goal_node
    while current is not None:
        path.append(current)
        current = current.parent
    path.reverse()
    return path


def greedy_generator(initial_state, goal_state):
    initial_h = calculate_manhattan_distance(initial_state, goal_state)
    root = Node(initial_state, h_cost=initial_h)

    frontier = []
    heapq.heappush(frontier, (root.h_cost, root))
    visited = {state_to_tuple(initial_state)}

    while frontier:
        current_h, current_node = heapq.heappop(frontier)

        if current_node.state == goal_state:
            yield current_node, True, get_solution(current_node)
            return
        yield current_node, False, None

        for child in generate_children(current_node, goal_state):
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in visited:
                visited.add(child_tuple)
                heapq.heappush(frontier, (child.h_cost, child))

    yield None, False, None


class PuzzleApp:

    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Greedy")
        self.root.geometry("850x650")
        self.root.configure(bg="#f0f2f5")

        self.TILE_SIZE = 80
        self.GAP = 5
        self.tiles = {}
        self.current_display_state = None
        self.is_running = False

        self.greedy_step_generator = None
        self.nodes_explored = 0
        self.start_time = 0

        self.create_widgets()
        self.set_default_values()

    def create_widgets(self):
        title_lbl = tk.Label(
            self.root,
            text="8-PUZZLE GREEDY SEARCH",
            font=("Helvetica", 16, "bold"),
            bg="#f0f2f5",
            fg="#1e293b",
        )
        title_lbl.pack(pady=15)

        input_frame = tk.Frame(self.root, bg="#f0f2f5")
        input_frame.pack(pady=10)

        init_box = tk.LabelFrame(
            input_frame,
            text=" Trạng thái ban đầu ",
            font=("Arial", 11, "bold"),
            bg="#f0f2f5",
            fg="#475569",
        )
        init_box.grid(row=0, column=0, padx=20)
        self.initial_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(
                    init_box,
                    width=3,
                    font=("Arial", 16),
                    justify="center",
                    bd=2,
                )
                e.grid(row=i, column=j, padx=6, pady=6)
                row_entries.append(e)
            self.initial_entries.append(row_entries)

        goal_box = tk.LabelFrame(
            input_frame,
            text=" Trạng thái đích ",
            font=("Arial", 11, "bold"),
            bg="#f0f2f5",
            fg="#475569",
        )
        goal_box.grid(row=0, column=1, padx=20)
        self.goal_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                e = tk.Entry(
                    goal_box,
                    width=3,
                    font=("Arial", 16),
                    justify="center",
                    bd=2,
                )
                e.grid(row=i, column=j, padx=6, pady=6)
                row_entries.append(e)
            self.goal_entries.append(row_entries)

        main_layout = tk.Frame(self.root, bg="#f0f2f5")
        main_layout.pack(pady=15, fill=tk.BOTH, expand=True)

        canvas_container = tk.Frame(main_layout, bg="#cbd5e1", padx=4, pady=4)
        canvas_container.pack(side=tk.LEFT, padx=40)
        canvas_width_height = 3 * self.TILE_SIZE + 4 * self.GAP
        self.canvas = tk.Canvas(
            canvas_container,
            width=canvas_width_height,
            height=canvas_width_height,
            bg="#e2e8f0",
            highlightthickness=0,
        )
        self.canvas.pack()

        right_frame = tk.Frame(main_layout, bg="#f0f2f5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        self.solve_button = tk.Button(
            right_frame,
            text=" CHẠY THUẬT TOÁN ",
            font=("Arial", 12, "bold"),
            bg="#f97316",
            fg="white",
            activebackground="#ea580c",
            activeforeground="white",
            command=self.start_solving,
            padx=8,
            pady=8,
        )
        self.solve_button.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(
            right_frame,
            text="Trạng thái: Sẵn sàng",
            font=("Arial", 11, "italic"),
            bg="#f0f2f5",
            fg="#64748b",
            anchor="w",
        )
        self.status_label.pack(fill=tk.X, pady=5)

        self.result_text = tk.Text(
            right_frame,
            width=40,
            height=15,
            font=("Consolas", 10),
            bd=2,
            relief=tk.SUNKEN,
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def set_default_values(self):
        start_matrix = [[1, 2, 3], [4, 0, 6], [7, 5, 8]]
        goal_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        for i in range(3):
            for j in range(3):
                self.initial_entries[i][j].insert(
                    0, str(start_matrix[i][j])
                )
                self.goal_entries[i][j].insert(0, str(goal_matrix[i][j]))
        self.draw_puzzle(start_matrix)

    def read_matrix(self, entries):
        matrix = []
        for i in range(3):
            row = []
            for j in range(3):
                val = entries[i][j].get().strip()
                row.append(int(val) if val else 0)
            matrix.append(row)
        return matrix

    def draw_puzzle(self, state, tile_bg="#ffffff", text_fg="#1e293b"):
        self.canvas.delete("all")
        self.tiles = {}
        self.current_display_state = [row[:] for row in state]
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                if val != 0:
                    x1 = j * self.TILE_SIZE + (j + 1) * self.GAP
                    y1 = i * self.TILE_SIZE + (i + 1) * self.GAP
                    x2 = x1 + self.TILE_SIZE
                    y2 = y1 + self.TILE_SIZE
                    rect_id = self.canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill=tile_bg,
                        outline="#94a3b8",
                        width=2,
                        tags=f"tile_{val}",
                    )
                    text_id = self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=str(val),
                        font=("Arial", 22, "bold"),
                        fill=text_fg,
                        tags=f"tile_{val}",
                    )
                    self.tiles[val] = (rect_id, text_id)

    def start_solving(self):
        if self.is_running:
            return

        try:
            initial = self.read_matrix(self.initial_entries)
            goal = self.read_matrix(self.goal_entries)
            all_nums = sorted([num for row in initial for num in row])
            if all_nums != list(range(9)):
                raise ValueError(
                    "Ma trận nhập vào phải chứa đầy đủ các số từ 0 đến 8"
                )

            self.canvas.config(bg="#e2e8f0")
            self.result_text.delete(1.0, tk.END)
            self.solve_button.config(state=tk.DISABLED)
            self.is_running = True
            self.nodes_explored = 0
            self.start_time = time.time()
            self.greedy_step_generator = greedy_generator(initial, goal)
            self.process_next_greedy_step()

        except ValueError as ve:
            messagebox.showerror("Lỗi dữ liệu", str(ve))
            self.solve_button.config(state=tk.NORMAL)
            self.is_running = False

    def process_next_greedy_step(self):
        if not self.is_running:
            return

        try:
            current_node, success, solution = next(
                self.greedy_step_generator
            )
            self.nodes_explored += 1

            if current_node:
                self.draw_puzzle(
                    current_node.state, tile_bg="#fff7ed", text_fg="#c2410c"
                )
                self.status_label.config(
                    text=f"Đang xét Node thứ: {self.nodes_explored} (h(n): {current_node.h_cost})"
                )

            if success and solution:
                end_time = time.time()
                self.status_label.config(text="Giải xong")

                self.result_text.insert(tk.END, f" tìm thấy đg đi \n")
                self.result_text.insert(
                    tk.END,
                    f"Số node đã duyệt qua: {self.nodes_explored}\n",
                )
                self.result_text.insert(
                    tk.END, f"Tổng số bước di chuyển: {len(solution) - 1}\n\n"
                )

                for step, node in enumerate(solution):
                    self.result_text.insert(
                        tk.END, f"Bước {step} (h(n) = {node.h_cost})"
                    )
                    if node.action:
                        self.result_text.insert(
                            tk.END, f" | Trống dịch: {node.action}"
                        )
                    self.result_text.insert(tk.END, "\n")
                    for row in node.state:
                        self.result_text.insert(tk.END, f"  {row}\n")
                    self.result_text.insert(tk.END, "\n")

                self.draw_puzzle(
                    solution[-1].state, tile_bg="#10b981", text_fg="#ffffff"
                )
                self.canvas.config(bg="#d1fae5")

                self.is_running = False
                self.solve_button.config(state=tk.NORMAL)
                return

            self.root.after(50, self.process_next_greedy_step)
        except StopIteration:
            self.status_label.config(text="Thất bại.")
            self.result_text.insert(tk.END, "Ko tìm thấy đg đi.")
            self.is_running = False
            self.solve_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    window = tk.Tk()
    app = PuzzleApp(window)
    window.mainloop()