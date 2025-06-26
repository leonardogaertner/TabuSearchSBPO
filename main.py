import time
import random
from typing import List, Set, Dict, Tuple
from collections import defaultdict
import numpy as np

TABU_TENURE = 115
MAX_ITERATIONS = 250
NEIGHBORHOOD_SIZE = 20

class Instance:
    def __init__(self, num_orders, num_items, num_aisles, order_items, aisle_items, lb, ub):
        self.num_orders = num_orders
        self.num_items = num_items
        self.num_aisles = num_aisles
        self.order_items = order_items
        self.aisle_items = aisle_items
        self.lb = lb
        self.ub = ub

    @staticmethod
    def read_instance(file_path: str) -> 'Instance':
        with open(file_path, 'r') as f:
            lines = f.readlines()

        o, i, a = map(int, lines[0].strip().split())
        order_items = []
        for line in lines[1:o+1]:
            parts = list(map(int, line.strip().split()))
            k = parts[0]
            items = [(parts[j*2+1], parts[j*2+2]) for j in range(k)]
            order_items.append(items)

        aisle_items = []
        for line in lines[o+1:o+a+1]:
            parts = list(map(int, line.strip().split()))
            l = parts[0]
            items = [(parts[j*2+1], parts[j*2+2]) for j in range(l)]
            aisle_items.append(items)

        lb, ub = map(int, lines[o+a+1].strip().split())

        return Instance(o, i, a, order_items, aisle_items, lb, ub)

class Solution:
    def __init__(self, orders: Set[int], aisles: Set[int]):
        self.orders = orders
        self.aisles = aisles
        self.objective = 0.0
        self.total_units = 0

    def is_feasible(self, instance: Instance) -> bool:
        self.total_units = 0
        item_demand = defaultdict(int)
        for order_idx in self.orders:
            for item_id, qty in instance.order_items[order_idx]:
                self.total_units += qty
                item_demand[item_id] += qty

        if self.total_units < instance.lb or self.total_units > instance.ub:
            return False

        item_supply = defaultdict(int)
        for aisle_idx in self.aisles:
            for item_id, qty in instance.aisle_items[aisle_idx]:
                item_supply[item_id] += qty

        for item_id, demand_qty in item_demand.items():
            if item_supply[item_id] < demand_qty:
                return False

        return True

    def compute_objective(self, instance: Instance) -> float:
        if not self.aisles:
            self.objective = 0.0
        else:
            self.total_units = sum(
                qty for order_idx in self.orders
                for _, qty in instance.order_items[order_idx]
            )
            self.objective = self.total_units / len(self.aisles)
        return self.objective

    def optimize_aisles(self, instance: Instance):
        item_demand = defaultdict(int)
        for order_idx in self.orders:
            for item_id, qty in instance.order_items[order_idx]:
                item_demand[item_id] += qty

        available_aisles = set(range(instance.num_aisles))
        self.aisles = set()
        remaining_demand = item_demand.copy()

        while remaining_demand and available_aisles:
            best_aisle = None
            max_covered = 0
            for aisle_idx in available_aisles:
                covered = sum(
                    min(qty, remaining_demand[item_id])
                    for item_id, qty in instance.aisle_items[aisle_idx]
                    if item_id in remaining_demand
                )
                if covered > max_covered:
                    best_aisle = aisle_idx
                    max_covered = covered

            if best_aisle is None:
                break

            self.aisles.add(best_aisle)
            available_aisles.remove(best_aisle)
            for item_id, qty in instance.aisle_items[best_aisle]:
                if item_id in remaining_demand:
                    remaining_demand[item_id] -= qty
                    if remaining_demand[item_id] <= 0:
                        del remaining_demand[item_id]

        if not self.is_feasible(instance):
            self.aisles = set()
            self.objective = 0.0

def generate_initial_solution(instance: Instance, max_attempts=100) -> Solution:
    print("Gerando solução inicial...")
    for attempt in range(max_attempts):
        orders = set()
        total_units = 0
        order_indices = list(range(instance.num_orders))
        random.shuffle(order_indices)

        for order_idx in order_indices:
            order_units = sum(qty for _, qty in instance.order_items[order_idx])
            if total_units + order_units <= instance.ub:
                orders.add(order_idx)
                total_units += order_units
            if total_units >= instance.lb:
                break

        solution = Solution(orders, set())
        solution.optimize_aisles(instance)
        if solution.is_feasible(instance):
            solution.compute_objective(instance)
            print(f"Solução inicial viável encontrada na tentativa {attempt+1}")
            return solution

    print("Nenhuma solução inicial viável encontrada.")
    return Solution(set(), set())

def generate_neighbor(current: Solution, instance: Instance) -> Solution:
    neighbor_orders = current.orders.copy()
    move_type = random.choice(['add', 'remove', 'swap'])

    if move_type == 'remove' and neighbor_orders:
        neighbor_orders.remove(random.choice(list(neighbor_orders)))
    elif move_type == 'add':
        available_orders = set(range(instance.num_orders)) - neighbor_orders
        if available_orders:
            neighbor_orders.add(random.choice(list(available_orders)))
    elif move_type == 'swap' and neighbor_orders:
        available_orders = set(range(instance.num_orders)) - neighbor_orders
        if available_orders:
            neighbor_orders.remove(random.choice(list(neighbor_orders)))
            neighbor_orders.add(random.choice(list(available_orders)))

    neighbor = Solution(neighbor_orders, set())
    neighbor.optimize_aisles(instance)
    if neighbor.is_feasible(instance):
        neighbor.compute_objective(instance)
        return neighbor
    else:
        return None

def tabu_search(instance: Instance, time_limit: float = 600.0,
                tabu_tenure: int = 10,
                max_iterations: int = 50,
                neighborhood_size: int = 20) -> Solution:
    start_time = time.time()
    current_solution = generate_initial_solution(instance)
    best_solution = current_solution
    best_objective = current_solution.objective

    tabu_list = []
    visited_solutions = set()
    iteration = 0

    while iteration < max_iterations and (time.time() - start_time) < time_limit:
        print(f"\nIteração {iteration + 1}")
        neighbors = []
        for _ in range(neighborhood_size):
            neighbor = generate_neighbor(current_solution, instance)
            if neighbor and neighbor.aisles:
                key = tuple(sorted(neighbor.orders))
                if key not in visited_solutions:
                    visited_solutions.add(key)
                    neighbors.append(neighbor)

        best_neighbor = None
        best_neighbor_obj = -float('inf')
        best_move = None

        for neighbor in neighbors:
            added = neighbor.orders - current_solution.orders
            removed = current_solution.orders - neighbor.orders

            if added:
                move = ('add', next(iter(added)))
            elif removed:
                move = ('remove', next(iter(removed)))
            else:
                continue

            if move not in tabu_list and neighbor.objective > best_neighbor_obj:
                best_neighbor = neighbor
                best_neighbor_obj = neighbor.objective
                best_move = move

        if best_neighbor is None or best_neighbor_obj <= best_objective:
            for neighbor in neighbors:
                if neighbor.objective > best_objective:
                    best_neighbor = neighbor
                    best_neighbor_obj = neighbor.objective
                    break

        if best_neighbor is None:
            print("Sem vizinhos viáveis. Encerrando busca.")
            break

        current_solution = best_neighbor
        tabu_list.append(best_move)
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)

        if best_neighbor_obj > best_objective:
            best_solution = best_neighbor
            best_objective = best_neighbor_obj
            print(f"Melhoria! Novo objetivo: {best_objective:.2f}")

        iteration += 1

    print("\nBusca tabu finalizada.")
    print(f"Melhor objetivo encontrado: {best_solution.objective:.2f}")
    print(f"Pedidos selecionados: {len(best_solution.orders)}")
    print(f"Corredores utilizados: {len(best_solution.aisles)}")
    return best_solution

def write_solution(solution: Solution, output_file: str):
    with open(output_file, 'w') as f:
        f.write(f"{len(solution.orders)}\n")
        for order_idx in sorted(solution.orders):
            f.write(f"{order_idx}\n")
        f.write(f"{len(solution.aisles)}\n")
        for aisle_idx in sorted(solution.aisles):
            f.write(f"{aisle_idx}\n")

def main(input_file: str, output_file: str):
    instance = Instance.read_instance(input_file)
    print(f"Instância carregada: {input_file}")
    print(f"Pedidos: {instance.num_orders}, Itens: {instance.num_items}, Corredores: {instance.num_aisles}")
    print(f"Limites de unidades por wave: {instance.lb} - {instance.ub}")
    solution = tabu_search(instance)
    write_solution(solution, output_file)
    print(f"Solução escrita no arquivo: {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python tabu_search_solver.py <input_file> <output_file>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
