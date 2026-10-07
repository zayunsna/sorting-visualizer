import math
import random
import os
import sys
from dataclasses import dataclass
from typing import Callable, Generator, Optional

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import pygame
except ImportError:
    print("pygame is not installed.")
    print("Install it with: python3 -m pip install -r requirements.txt")
    sys.exit(1)


WIDTH = 1100
HEIGHT = 720
SIDEBAR_WIDTH = 190
PANEL_HEIGHT = 168
BAR_AREA_TOP = PANEL_HEIGHT
BAR_AREA_BOTTOM = HEIGHT - 36
BACKGROUND = (5, 13, 24)
SIDEBAR = (7, 19, 34)
PANEL = (10, 26, 43)
PANEL_ALT = (14, 35, 55)
BORDER = (31, 76, 91)
GRID = (18, 51, 67)
TEXT = (220, 246, 244)
MUTED = (114, 154, 164)
BAR = (0, 229, 216)
BAR_SORTED = (94, 255, 189)
COMPARE = (0, 245, 255)
SWAP = (255, 61, 129)
ACCENT = (0, 245, 255)
LOW_VALUE_COLOR = (0, 204, 255)
HIGH_VALUE_COLOR = (255, 43, 214)
VISUAL_MODES = (
    "Histogram",
    "Circle",
    "Dot Plot",
    "Particle",
    "Spiral",
    "Radial Bars",
    "Heatmap",
    "Waveform",
    "Grid",
    "Arc Swap",
    "Race Track",
    "Equalizer",
)


@dataclass
class SortEvent:
    action: str
    left: Optional[int] = None
    right: Optional[int] = None
    message: str = ""


def make_array(size: int = 42, low: int = 20, high: int = 100) -> list[int]:
    return [random.randint(low, high) for _ in range(size)]


def finish_sweep(arr: list[int]) -> Generator[SortEvent, None, None]:
    for index, value in enumerate(arr):
        yield SortEvent("sweep", index, None, f"final sweep {index + 1}/{len(arr)}: {value}")


def periodic_insertion_sort(
    arr: list[int], pass_interval: int = 4
) -> Generator[SortEvent, None, None]:
    """Sort arr in place, yielding comparisons and swaps for animation.

    compare(a, b) means arr[a] > arr[b], so equal values retain their order.
    This is insertion sort with an extra pass, rather than true library sort.
    Each inserted prefix is already sorted, so the extra pass is redundant
    for correctness but is retained to reproduce the requested algorithm.
    """
    if pass_interval < 1:
        raise ValueError("pass_interval must be at least 1")

    for i in range(1, len(arr)):
        j = i
        yield SortEvent("insert", j, None, f"insert index {i}")
        while j > 0:
            yield SortEvent("compare", j - 1, j, f"insertion: compare {arr[j - 1]} and {arr[j]}")
            if arr[j - 1] <= arr[j]:
                break
            yield SortEvent("swap", j - 1, j, f"swap {arr[j - 1]} and {arr[j]}")
            arr[j - 1], arr[j] = arr[j], arr[j - 1]
            yield SortEvent("after_swap", j - 1, j, "insertion: after swap")
            j -= 1

        if i % pass_interval == 0:
            yield SortEvent("pass", 0, i - 1, f"extra pass at i={i}: k < {i - 1}")
            for k in range(i - 1):
                yield SortEvent("compare", k, k + 1, f"extra pass: compare {arr[k]} and {arr[k + 1]}")
                if arr[k] > arr[k + 1]:
                    yield SortEvent("swap", k, k + 1, f"extra pass: swap {arr[k]} and {arr[k + 1]}")
                    arr[k], arr[k + 1] = arr[k + 1], arr[k]
                    yield SortEvent("after_swap", k, k + 1, "extra pass: after swap")

    yield from finish_sweep(arr)
    yield SortEvent("done", None, None, "sorted")


def insertion_sort(arr: list[int]) -> Generator[SortEvent, None, None]:
    for i in range(1, len(arr)):
        j = i
        yield SortEvent("insert", j, None, f"insert index {i}")

        while j > 0:
            yield SortEvent("compare", j - 1, j, f"compare {arr[j - 1]} and {arr[j]}")
            if arr[j - 1] <= arr[j]:
                break

            yield SortEvent("swap", j - 1, j, f"swap {arr[j - 1]} and {arr[j]}")
            arr[j - 1], arr[j] = arr[j], arr[j - 1]
            yield SortEvent("after_swap", j - 1, j, "after swap")
            j -= 1

    yield from finish_sweep(arr)
    yield SortEvent("done", None, None, "sorted")


def bubble_sort(arr: list[int]) -> Generator[SortEvent, None, None]:
    n = len(arr)

    for end in range(n - 1, 0, -1):
        swapped = False
        yield SortEvent("pass", 0, end, f"bubble pass up to index {end}")

        for i in range(end):
            yield SortEvent("compare", i, i + 1, f"compare {arr[i]} and {arr[i + 1]}")
            if arr[i] > arr[i + 1]:
                yield SortEvent("swap", i, i + 1, f"swap {arr[i]} and {arr[i + 1]}")
                arr[i], arr[i + 1] = arr[i + 1], arr[i]
                swapped = True
                yield SortEvent("after_swap", i, i + 1, "after swap")

        if not swapped:
            break

    yield from finish_sweep(arr)
    yield SortEvent("done", None, None, "sorted")


def selection_sort(arr: list[int]) -> Generator[SortEvent, None, None]:
    n = len(arr)

    for i in range(n - 1):
        min_index = i
        yield SortEvent("select", i, min_index, f"select minimum for index {i}")

        for j in range(i + 1, n):
            yield SortEvent("compare", min_index, j, f"compare {arr[min_index]} and {arr[j]}")
            if arr[j] < arr[min_index]:
                min_index = j
                yield SortEvent("select", i, min_index, f"new minimum {arr[min_index]}")

        if min_index != i:
            yield SortEvent("swap", i, min_index, f"swap {arr[i]} and {arr[min_index]}")
            arr[i], arr[min_index] = arr[min_index], arr[i]
            yield SortEvent("after_swap", i, min_index, "after swap")

    yield from finish_sweep(arr)
    yield SortEvent("done", None, None, "sorted")


def quick_sort(arr: list[int]) -> Generator[SortEvent, None, None]:
    def partition(low: int, high: int) -> Generator[SortEvent, None, int]:
        pivot = arr[high]
        i = low
        yield SortEvent("pivot", high, None, f"pivot {pivot}")

        for j in range(low, high):
            yield SortEvent("compare", j, high, f"compare {arr[j]} and pivot {pivot}")
            if arr[j] <= pivot:
                if i != j:
                    yield SortEvent("swap", i, j, f"move {arr[j]} before pivot")
                    arr[i], arr[j] = arr[j], arr[i]
                    yield SortEvent("after_swap", i, j, "after swap")
                i += 1

        if i != high:
            yield SortEvent("swap", i, high, f"place pivot {pivot}")
            arr[i], arr[high] = arr[high], arr[i]
            yield SortEvent("after_swap", i, high, "after swap")

        return i

    def sort_range(low: int, high: int) -> Generator[SortEvent, None, None]:
        if low >= high:
            return

        yield SortEvent("pass", low, high, f"quick sort range {low}..{high}")
        pivot_index = yield from partition(low, high)
        yield from sort_range(low, pivot_index - 1)
        yield from sort_range(pivot_index + 1, high)

    yield from sort_range(0, len(arr) - 1)
    yield from finish_sweep(arr)
    yield SortEvent("done", None, None, "sorted")


Algorithm = tuple[str, Callable[[list[int]], Generator[SortEvent, None, None]]]
ALGORITHMS: list[Algorithm] = [
    ("Periodic Insertion", periodic_insertion_sort),
    ("Insertion Sort", insertion_sort),
    ("Bubble Sort", bubble_sort),
    ("Selection Sort", selection_sort),
    ("Quick Sort", quick_sort),
]


def mix_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    ratio: float,
) -> tuple[int, int, int]:
    ratio = max(0.0, min(1.0, ratio))
    return tuple(int(start[i] + (end[i] - start[i]) * ratio) for i in range(3))


def brighten(color: tuple[int, int, int], amount: float = 0.26) -> tuple[int, int, int]:
    return mix_color(color, (255, 255, 255), amount)


class VisualizationViews:
    def visual_mode_name(self) -> str:
        return VISUAL_MODES[self.visual_mode_index]

    def select_visual_mode(self, index: int) -> None:
        self.visual_mode_index = index % len(VISUAL_MODES)

    def cycle_visual_mode(self) -> None:
        self.select_visual_mode(self.visual_mode_index + 1)

    def step_sort(self) -> None:
        if self.event.action == "done":
            return

        try:
            self.event = next(self.sorter)
        except StopIteration:
            self.event = SortEvent("done", None, None, "sorted")

        self.steps += 1
        if self.event.action == "compare":
            self.comparisons += 1
        elif self.event.action == "swap":
            self.swaps += 1


    def draw_text(self, text: str, x: int, y: int, font: pygame.font.Font, color=TEXT) -> None:
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

    def bar_color(self, index: int) -> tuple[int, int, int]:
        base_color = self.value_color(self.arr[index])

        if index == self.event.left or index == self.event.right:
            if self.event.action in ("swap", "after_swap"):
                return SWAP
            if self.event.action in ("pivot", "select"):
                return ACCENT
            if self.event.action == "sweep":
                return brighten(base_color, 0.35)
            return brighten(base_color, 0.28)

        return base_color

    def value_color(self, value: int) -> tuple[int, int, int]:
        low = min(self.arr)
        high = max(self.arr)
        ratio = 0.0 if high == low else (value - low) / (high - low)
        return mix_color(LOW_VALUE_COLOR, HIGH_VALUE_COLOR, ratio)

    def content_rect(self) -> pygame.Rect:
        return pygame.Rect(SIDEBAR_WIDTH + 28, BAR_AREA_TOP + 28, WIDTH - SIDEBAR_WIDTH - 56, BAR_AREA_BOTTOM - BAR_AREA_TOP - 28)

    def value_ratio(self, value: int) -> float:
        low = min(self.arr)
        high = max(self.arr)
        return 0.0 if high == low else (value - low) / (high - low)

    def x_for_index(self, index: int, rect: pygame.Rect) -> int:
        if len(self.arr) <= 1:
            return rect.centerx
        return rect.left + int(index * rect.width / (len(self.arr) - 1))

    def y_for_value(self, value: int, rect: pygame.Rect) -> int:
        return rect.bottom - int(self.value_ratio(value) * rect.height)

    def is_highlighted(self, index: int) -> bool:
        return index == self.event.left or index == self.event.right

    def highlight_width(self, index: int, normal: int = 4, highlighted: int = 7) -> int:
        return highlighted if self.is_highlighted(index) else normal

    def draw_bars(self) -> None:
        max_value = max(self.arr)
        rect = self.content_rect()
        usable_height = rect.height
        gap = 3
        bar_width = (rect.width - gap * (len(self.arr) - 1)) / len(self.arr)

        for i, value in enumerate(self.arr):
            bar_height = int((value / max_value) * (usable_height - 40))
            x = rect.left + int(i * (bar_width + gap))
            y = rect.bottom - bar_height
            bar_rect = pygame.Rect(x, y, int(bar_width), bar_height)
            pygame.draw.rect(self.screen, self.bar_color(i), bar_rect, border_radius=4)

            if len(self.arr) <= 48:
                label = self.small_font.render(str(value), True, TEXT)
                label_x = x + bar_rect.width // 2 - label.get_width() // 2
                self.screen.blit(label, (label_x, y - 22))

    def draw_circle(self) -> None:
        max_value = max(self.arr)
        min_value = min(self.arr)
        rect = self.content_rect()
        center_x = rect.centerx
        center_y = rect.centery + 8
        inner_radius = 92
        max_length = min(rect.width, rect.height) // 2 - inner_radius - 26

        pygame.draw.circle(self.screen, GRID, (center_x, center_y), inner_radius, width=2)

        for i, value in enumerate(self.arr):
            angle = -math.pi / 2 + (2 * math.pi * i / len(self.arr))
            ratio = 0.0 if max_value == min_value else (value - min_value) / (max_value - min_value)
            length = 28 + int(ratio * max_length)
            start_x = center_x + math.cos(angle) * inner_radius
            start_y = center_y + math.sin(angle) * inner_radius
            end_x = center_x + math.cos(angle) * (inner_radius + length)
            end_y = center_y + math.sin(angle) * (inner_radius + length)
            color = self.bar_color(i)
            width = 6 if i == self.event.left or i == self.event.right else 4

            pygame.draw.line(self.screen, color, (start_x, start_y), (end_x, end_y), width)
            pygame.draw.circle(self.screen, color, (int(end_x), int(end_y)), width + 2)

            if i == self.event.left or i == self.event.right:
                label = self.small_font.render(str(value), True, TEXT)
                label_x = int(end_x - label.get_width() / 2)
                label_y = int(end_y - label.get_height() / 2)
                self.screen.blit(label, (label_x, label_y))

    def draw_dot_plot(self) -> None:
        rect = self.content_rect()
        pygame.draw.line(self.screen, GRID, (rect.left, rect.bottom), (rect.right, rect.bottom), 1)
        pygame.draw.line(self.screen, GRID, (rect.left, rect.top), (rect.left, rect.bottom), 1)

        for i, value in enumerate(self.arr):
            x = self.x_for_index(i, rect)
            y = self.y_for_value(value, rect)
            radius = 9 if self.is_highlighted(i) else 6
            pygame.draw.circle(self.screen, self.bar_color(i), (x, y), radius)

    def draw_particle(self) -> None:
        rect = self.content_rect()
        for i, value in enumerate(self.arr):
            x = self.x_for_index(i, rect)
            y = self.y_for_value(value, rect)
            radius = 11 if self.is_highlighted(i) else 6
            color = self.bar_color(i)
            for trail in range(3):
                offset_x = int(math.sin((self.steps + i * 7 + trail * 11) * 0.08) * (trail + 1) * 3)
                offset_y = int(math.cos((self.steps + i * 5 + trail * 13) * 0.08) * (trail + 1) * 3)
                trail_color = brighten(color, 0.18 + trail * 0.12)
                pygame.draw.circle(self.screen, trail_color, (x + offset_x, y + offset_y), max(2, radius - trail * 2))
            pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_spiral(self) -> None:
        rect = self.content_rect()
        center_x = rect.centerx
        center_y = rect.centery
        max_radius = min(rect.width, rect.height) // 2 - 24
        turns = 2.7

        for i, value in enumerate(self.arr):
            progress = i / max(1, len(self.arr) - 1)
            angle = -math.pi / 2 + progress * turns * 2 * math.pi
            radius = 22 + progress * max_radius
            size = 5 + int(self.value_ratio(value) * 13)
            x = int(center_x + math.cos(angle) * radius)
            y = int(center_y + math.sin(angle) * radius)
            pygame.draw.circle(self.screen, self.bar_color(i), (x, y), size + (4 if self.is_highlighted(i) else 0))

    def draw_radial_bars(self) -> None:
        rect = self.content_rect()
        center_x = rect.centerx
        center_y = rect.centery + 4
        inner_radius = 58
        max_length = min(rect.width, rect.height) // 2 - inner_radius - 18

        for i, value in enumerate(self.arr):
            angle = -math.pi / 2 + 2 * math.pi * i / len(self.arr)
            length = 20 + int(self.value_ratio(value) * max_length)
            width = self.highlight_width(i, 5, 9)
            start = (
                center_x + math.cos(angle) * inner_radius,
                center_y + math.sin(angle) * inner_radius,
            )
            end = (
                center_x + math.cos(angle) * (inner_radius + length),
                center_y + math.sin(angle) * (inner_radius + length),
            )
            pygame.draw.line(self.screen, self.bar_color(i), start, end, width)

    def draw_heatmap(self) -> None:
        rect = self.content_rect()
        cols = math.ceil(math.sqrt(len(self.arr) * rect.width / max(1, rect.height)))
        rows = math.ceil(len(self.arr) / cols)
        gap = 4
        cell_w = (rect.width - gap * (cols - 1)) / cols
        cell_h = (rect.height - gap * (rows - 1)) / rows

        for i, value in enumerate(self.arr):
            col = i % cols
            row = i // cols
            cell = pygame.Rect(
                rect.left + int(col * (cell_w + gap)),
                rect.top + int(row * (cell_h + gap)),
                max(4, int(cell_w)),
                max(4, int(cell_h)),
            )
            pygame.draw.rect(self.screen, self.bar_color(i), cell, border_radius=5)
            if self.is_highlighted(i):
                pygame.draw.rect(self.screen, TEXT, cell, width=2, border_radius=5)

    def draw_waveform(self) -> None:
        rect = self.content_rect()
        points = [(self.x_for_index(i, rect), self.y_for_value(value, rect)) for i, value in enumerate(self.arr)]
        if len(points) >= 2:
            pygame.draw.lines(self.screen, GRID, False, points, 8)
            pygame.draw.lines(self.screen, ACCENT, False, points, 2)

        for i, point in enumerate(points):
            pygame.draw.circle(self.screen, self.bar_color(i), point, 8 if self.is_highlighted(i) else 4)

    def draw_grid(self) -> None:
        rect = self.content_rect()
        cols = 7
        rows = math.ceil(len(self.arr) / cols)
        gap = 8
        tile_w = (rect.width - gap * (cols - 1)) / cols
        tile_h = (rect.height - gap * (rows - 1)) / rows

        for i, value in enumerate(self.arr):
            col = i % cols
            row = i // cols
            ratio = self.value_ratio(value)
            tile = pygame.Rect(
                rect.left + int(col * (tile_w + gap)),
                rect.top + int(row * (tile_h + gap)),
                int(tile_w),
                int(tile_h),
            )
            color = self.bar_color(i)
            pygame.draw.rect(self.screen, color, tile, border_radius=8)
            inset = int((1.0 - ratio) * min(tile.width, tile.height) * 0.35)
            inner = tile.inflate(-inset, -inset)
            pygame.draw.rect(self.screen, brighten(color, 0.22), inner, border_radius=7)

    def draw_arc_swap(self) -> None:
        self.draw_bars()
        if self.event.left is None or self.event.right is None:
            return

        rect = self.content_rect()
        left = min(self.event.left, self.event.right)
        right = max(self.event.left, self.event.right)
        x1 = self.x_for_index(left, rect)
        x2 = self.x_for_index(right, rect)
        span = max(28, x2 - x1)
        arc_height = min(170, max(46, span // 2))
        arc_rect = pygame.Rect(x1, rect.top + 24, span, arc_height)
        pygame.draw.arc(self.screen, ACCENT, arc_rect, 0, math.pi, 3)

    def draw_race_track(self) -> None:
        rect = self.content_rect()
        lane_h = rect.height / len(self.arr)
        track_left = rect.left + 16
        track_width = rect.width - 32

        for i, value in enumerate(self.arr):
            y = rect.top + int(i * lane_h + lane_h / 2)
            x = track_left + int(self.value_ratio(value) * track_width)
            pygame.draw.line(self.screen, GRID, (track_left, y), (track_left + track_width, y), 1)
            pygame.draw.circle(self.screen, self.bar_color(i), (x, y), 9 if self.is_highlighted(i) else 6)

    def draw_equalizer(self) -> None:
        rect = self.content_rect()
        max_value = max(self.arr)
        cols = len(self.arr)
        gap = 5
        bar_width = (rect.width - gap * (cols - 1)) / cols

        for i, value in enumerate(self.arr):
            phase = math.sin((self.steps * 0.25) + i * 0.7)
            pulse = 1.0 + (0.18 * phase if self.is_highlighted(i) else 0.05 * phase)
            height = int((value / max_value) * rect.height * 0.88 * pulse)
            x = rect.left + int(i * (bar_width + gap))
            y = rect.centery - height // 2
            bar_rect = pygame.Rect(x, y, max(3, int(bar_width)), height)
            pygame.draw.rect(self.screen, self.bar_color(i), bar_rect, border_radius=6)

    def draw_visualization(self) -> None:
        mode = self.visual_mode_name()
        if mode == "Circle":
            self.draw_circle()
        elif mode == "Dot Plot":
            self.draw_dot_plot()
        elif mode == "Particle":
            self.draw_particle()
        elif mode == "Spiral":
            self.draw_spiral()
        elif mode == "Radial Bars":
            self.draw_radial_bars()
        elif mode == "Heatmap":
            self.draw_heatmap()
        elif mode == "Waveform":
            self.draw_waveform()
        elif mode == "Grid":
            self.draw_grid()
        elif mode == "Arc Swap":
            self.draw_arc_swap()
        elif mode == "Race Track":
            self.draw_race_track()
        elif mode == "Equalizer":
            self.draw_equalizer()
        else:
            self.draw_bars()

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.draw_sidebar()
        self.draw_panel()
        self.draw_visualization()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


class Visualizer(VisualizationViews):
    PATTERNS = ("Random", "Reversed", "Sorted", "Few unique")

    def __init__(self) -> None:
        self.algorithm_index = 0
        self.algorithm_buttons = []
        self.pass_interval = 4
        self.pattern_index = 0
        self.initial_arr: list[int] = []
        self.sliders: dict[str, pygame.Rect] = {}
        self.buttons: dict[str, pygame.Rect] = {}
        self.dragging: str | None = None
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 36)
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 19)
        self.sidebar_font = pygame.font.Font(None, 20)
        self.speed_ms = 80
        self.array_size = 42
        self.running = True
        self.visual_mode_index = 0
        self.visual_buttons = []
        self.reset()
        pygame.display.set_caption("Sorting Visualizer")

    def algorithm_name(self) -> str:
        return ALGORITHMS[self.algorithm_index][0] + " Sort" if self.algorithm_index == 0 else ALGORITHMS[self.algorithm_index][0]

    def reset(self, regenerate: bool = True) -> None:
        if regenerate:
            self.initial_arr = make_array(self.array_size)
            pattern = self.PATTERNS[self.pattern_index]
            if pattern == "Reversed":
                self.initial_arr.sort(reverse=True)
            elif pattern == "Sorted":
                self.initial_arr.sort()
            elif pattern == "Few unique":
                self.initial_arr = [random.choice((20, 40, 60, 80, 100)) for _ in range(self.array_size)]
        self.arr = self.initial_arr.copy()
        algorithm = ALGORITHMS[self.algorithm_index][1]
        self.sorter = (algorithm(self.arr, self.pass_interval) if self.algorithm_index == 0 else algorithm(self.arr))
        self.comparisons = self.swaps = self.steps = 0
        self.event = SortEvent("ready", message="ready - press Start or Space")
        self.paused = True
        self.last_step_at = pygame.time.get_ticks()

    def toggle_pause(self) -> None:
        if self.event.action == "done":
            self.reset(regenerate=False)
        self.paused = not self.paused
        self.last_step_at = pygame.time.get_ticks()

    def activate(self, name: str) -> None:
        if name == "start":
            self.toggle_pause()
        elif name == "step":
            self.paused = True
            self.step_sort()
        elif name == "shuffle":
            self.reset()
        elif name == "restart":
            self.reset(regenerate=False)
        elif name == "pattern":
            self.pattern_index = (self.pattern_index + 1) % len(self.PATTERNS)
            self.reset()

    def set_slider(self, name: str, x: int) -> None:
        if name == "interval" and self.algorithm_index != 0:
            return
        rect = self.sliders[name]
        low, high = {"count": (8, 120), "delay": (1, 700), "interval": (1, 12)}[name]
        value = low + round(max(0.0, min(1.0, (x - rect.x) / rect.width)) * (high - low))
        attribute = {"count": "array_size", "delay": "speed_ms", "interval": "pass_interval"}[name]
        if value == getattr(self, attribute):
            return
        setattr(self, attribute, value)
        if name != "delay":
            self.reset(regenerate=name == "count")
        else:
            self.last_step_at = pygame.time.get_ticks()

    def handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in self.sliders.items():
                    if rect.inflate(16, 24).collidepoint(event.pos):
                        self.dragging = name
                        self.set_slider(name, event.pos[0])
                        break
                else:
                    for name, rect in self.buttons.items():
                        if rect.collidepoint(event.pos):
                            self.activate(name)
                            break
                    for rect, index in self.algorithm_buttons:
                        if rect.collidepoint(event.pos):
                            self.select_algorithm(index)
                            break
                    for rect, index in self.visual_buttons:
                        if rect.collidepoint(event.pos):
                            self.select_visual_mode(index)
                            break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = None
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                self.set_slider(self.dragging, event.pos[0])
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    self.select_algorithm(event.key - pygame.K_1)
                elif event.key == pygame.K_SPACE:
                    self.toggle_pause()
                elif event.key == pygame.K_RIGHT:
                    self.activate("step")
                elif event.key == pygame.K_r:
                    self.activate("restart")
                elif event.key == pygame.K_n:
                    self.activate("shuffle")
                elif event.key == pygame.K_v:
                    self.cycle_visual_mode()
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.speed_ms = max(1, min(700, self.speed_ms + (-10 if event.key == pygame.K_UP else 10)))
                    self.last_step_at = pygame.time.get_ticks()

    def update(self) -> None:
        if self.paused or self.event.action == "done":
            return
        now = pygame.time.get_ticks()
        # Multiple events per frame keep small delays useful on a 60 Hz display.
        due = min(250, (now - self.last_step_at) // self.speed_ms)
        for _ in range(due):
            self.step_sort()
            self.last_step_at += self.speed_ms
            if self.event.action == "done":
                break

    def select_algorithm(self, index: int) -> None:
        self.algorithm_index = index % len(ALGORITHMS)
        self.reset(regenerate=False)
        pygame.display.set_caption(f"Sorting Visualizer - {self.algorithm_name()}")

    def draw_sidebar(self) -> None:
        pygame.draw.rect(self.screen, SIDEBAR, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, BORDER, (SIDEBAR_WIDTH - 1, 0), (SIDEBAR_WIDTH - 1, HEIGHT))
        self.draw_text("Algorithms", 18, 20, self.font)
        self.draw_text("click or keys 1-5", 18, 46, self.small_font, MUTED)
        self.algorithm_buttons = []
        self.visual_buttons = []
        for index, (name, _) in enumerate(ALGORITHMS):
            rect = pygame.Rect(14, 72 + index * 35, SIDEBAR_WIDTH - 28, 29)
            selected = index == self.algorithm_index
            pygame.draw.rect(self.screen, PANEL_ALT if selected else PANEL, rect, border_radius=6)
            pygame.draw.rect(self.screen, ACCENT if selected else BORDER, rect, width=1, border_radius=6)
            self.draw_text(name, rect.x + 10, rect.y + 8, self.small_font, TEXT if selected else MUTED)
            self.algorithm_buttons.append((rect, index))
        self.draw_text("Views", 18, 255, self.font)
        for index, name in enumerate(VISUAL_MODES):
            rect = pygame.Rect(14, 286 + index * 33, SIDEBAR_WIDTH - 28, 27)
            selected = index == self.visual_mode_index
            pygame.draw.rect(self.screen, PANEL_ALT if selected else PANEL, rect, border_radius=6)
            pygame.draw.rect(self.screen, ACCENT if selected else BORDER, rect, width=1, border_radius=6)
            self.draw_text(name, rect.x + 10, rect.y + 7, self.small_font, TEXT if selected else MUTED)
            self.visual_buttons.append((rect, index))
        self.draw_text("Space: start / pause", 14, 692, self.small_font, MUTED)

    def draw_panel(self) -> None:
        x0 = SIDEBAR_WIDTH + 28
        pygame.draw.rect(self.screen, PANEL, (SIDEBAR_WIDTH, 0, WIDTH - SIDEBAR_WIDTH, PANEL_HEIGHT))
        self.draw_text(self.algorithm_name(), x0, 12, self.title_font)
        status = "complete" if self.event.action == "done" else "paused" if self.paused else "running"
        self.draw_text(f"{status} | comparisons {self.comparisons} | swaps {self.swaps} | events {self.steps}", x0 + 355, 20, self.small_font)
        self.sliders = {}
        for offset, name, label, value, low, high in (
            (0, "count", "Count", self.array_size, 8, 120),
            (295, "delay", "Delay ms/event (lower = faster)", self.speed_ms, 1, 700),
            (590, "interval", "Extra pass every N insertions", self.pass_interval, 1, 12),
        ):
            x, y, width = x0 + offset, 77, 245
            active = name != "interval" or self.algorithm_index == 0
            caption = f"{label}: {value}" if active else "Extra pass: periodic insertion only"
            self.draw_text(caption, x, 52, self.small_font, TEXT if active else MUTED)
            rect = pygame.Rect(x, y, width, 8)
            self.sliders[name] = rect
            pygame.draw.rect(self.screen, GRID, rect, border_radius=4)
            ratio = (value - low) / (high - low)
            pygame.draw.rect(self.screen, ACCENT if active else MUTED, (x, y, int(width * ratio), 8), border_radius=4)
            pygame.draw.circle(self.screen, TEXT, (x + int(width * ratio), y + 4), 7)
        self.buttons = {}
        start_label = "Replay" if self.event.action == "done" else "Start" if self.paused else "Pause"
        for index, (name, label) in enumerate((
            ("start", start_label), ("step", "Step"), ("shuffle", "New numbers"),
            ("restart", "Restart"), ("pattern", f"Input: {self.PATTERNS[self.pattern_index]}"),
        )):
            rect = pygame.Rect(x0 + index * 169, 101, 158, 30)
            self.buttons[name] = rect
            pygame.draw.rect(self.screen, PANEL_ALT, rect, border_radius=6)
            pygame.draw.rect(self.screen, BORDER, rect, width=1, border_radius=6)
            self.draw_text(label, rect.x + 12, rect.y + 8, self.small_font)
        self.draw_text(self.event.message, x0, 143, self.small_font, ACCENT)


def main() -> None:
    Visualizer().run()


if __name__ == "__main__":
    main()
