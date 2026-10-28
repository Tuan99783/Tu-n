"""Vẽ các hình minh hoạ cho 5 đề (xuất PNG)."""
import math
import sys
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

plt.rcParams["font.family"] = "DejaVu Serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"

OUT = "."


def new(w=4.2, h=2.6):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=220, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def line(ax, p, q, **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], color="black", lw=1.2, **kw)


def pt(ax, p, name, dx=0.0, dy=0.0, dot=True, size=12):
    if dot:
        ax.plot(*p, "o", color="black", ms=3)
    ax.text(p[0] + dx, p[1] + dy, name, fontsize=size, style="italic", ha="center", va="center")


def angle(ax, p, t1, t2, r=0.35, label=None, lr=None, size=10, n=1):
    """Cung đánh dấu góc từ t1 đến t2 (độ, ngược chiều kim đồng hồ)."""
    for k in range(n):
        rr = r + 0.06 * k
        ax.add_patch(Arc(p, 2 * rr, 2 * rr, theta1=t1, theta2=t2, lw=0.9))
    if label:
        m = math.radians((t1 + t2) / 2)
        lr = lr or r + 0.2
        ax.text(p[0] + lr * math.cos(m), p[1] + lr * math.sin(m), label, fontsize=size,
                ha="center", va="center")


def right_angle(ax, p, d1, d2, s=0.18):
    a1, a2 = math.radians(d1), math.radians(d2)
    u = (s * math.cos(a1), s * math.sin(a1))
    v = (s * math.cos(a2), s * math.sin(a2))
    pts = [(p[0] + u[0], p[1] + u[1]), (p[0] + u[0] + v[0], p[1] + u[1] + v[1]), (p[0] + v[0], p[1] + v[1])]
    ax.plot([q[0] for q in pts], [q[1] for q in pts], color="black", lw=0.9)


def tick(ax, p, q, n=1, s=0.1):
    """Đánh dấu đoạn bằng nhau bằng n vạch ở giữa đoạn pq."""
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    for k in range(n):
        off = (k - (n - 1) / 2) * 0.07
        cx, cy = mx + ux * off, my + uy * off
        ax.plot([cx - nx * s, cx + nx * s], [cy - ny * s, cy + ny * s], color="black", lw=1)


def along(p, deg, t):
    return (p[0] + t * math.cos(math.radians(deg)), p[1] + t * math.sin(math.radians(deg)))


# ---------------- Đề 1 – Bài 4 ----------------
def de1_bai4():
    fig, ax = new()
    A = (3, 2)
    B = along(A, -115, 2 / math.sin(math.radians(115)))
    line(ax, (-0.3, 2), (5, 2)); line(ax, (-0.3, 0), (5, 0))
    line(ax, along(A, 65, 0.8), along(B, -115, 0.8))
    ax.text(5.15, 2, "a", fontsize=12, style="italic", va="center")
    ax.text(5.15, 0, "b", fontsize=12, style="italic", va="center")
    c_end = along(A, 65, 0.8)
    ax.text(c_end[0] + 0.12, c_end[1], "c", fontsize=12, style="italic", va="center")
    pt(ax, A, "A", -0.12, 0.25); pt(ax, B, "B", -0.25, -0.22)
    angle(ax, A, -115, 0, r=0.3, label="1", lr=0.5)
    angle(ax, A, -180, -115, r=0.3, label="2", lr=0.5)
    angle(ax, B, 0, 65, r=0.3, label="1", lr=0.5)
    angle(ax, B, -115, 0, r=0.22, label="2", lr=0.42)
    save(fig, "de1_bai4.png")


# ---------------- Đề 2 – Bài 4 ----------------
def de2_bai4():
    fig, ax = new(4.0, 2.5)
    A, B = (0, 2), (0, 0)
    s = 2 / (math.sin(math.radians(40)) + math.cos(math.radians(40)) * math.tan(math.radians(30)))
    O = along(A, -40, s)
    line(ax, A, (3.2, 2)); line(ax, B, (3.2, 0)); line(ax, A, O); line(ax, B, O)
    ax.text(3.3, 2, "x", fontsize=12, style="italic", va="center")
    ax.text(3.3, 0, "y", fontsize=12, style="italic", va="center")
    pt(ax, A, "A", -0.2, 0.15); pt(ax, B, "B", -0.2, -0.15); pt(ax, O, "O", 0.22, 0)
    angle(ax, A, -40, 0, r=0.45, label=r"$40^\circ$", lr=0.8, size=9)
    angle(ax, B, 0, 30, r=0.45, label=r"$30^\circ$", lr=0.8, size=9)
    t1 = math.degrees(math.atan2(A[1] - O[1], A[0] - O[0]))
    t2 = math.degrees(math.atan2(B[1] - O[1], B[0] - O[0])) + 360
    angle(ax, O, t1, t2, r=0.25, label="?", lr=0.45, size=10)
    save(fig, "de2_bai4.png")


# ---------------- Đề 3 – Bài 4 ----------------
def de3_bai4():
    fig, ax = new()
    line(ax, (0, -0.6), (0, 2.6))
    line(ax, (-0.4, 2), (5, 2)); line(ax, (-0.4, 0), (5, 0))
    ax.text(0.12, 2.6, "c", fontsize=12, style="italic", va="center")
    ax.text(5.15, 2, "a", fontsize=12, style="italic", va="center")
    ax.text(5.15, 0, "b", fontsize=12, style="italic", va="center")
    right_angle(ax, (0, 2), 0, -90); right_angle(ax, (0, 0), 0, 90)
    M = (2.5, 2)
    N = along(M, -60, 2 / math.sin(math.radians(60)))
    line(ax, along(M, 120, 0.7), along(N, -60, 0.7))
    e = along(M, 120, 0.7)
    ax.text(e[0] - 0.15, e[1], "d", fontsize=12, style="italic", va="center")
    pt(ax, M, "M", -0.3, -0.22); pt(ax, N, "N", -0.3, -0.22)
    angle(ax, M, 0, 120, r=0.3, label="1", lr=0.5)
    angle(ax, N, 0, 120, r=0.3, label="1", lr=0.5)
    angle(ax, N, 120, 180, r=0.3, label="2", lr=0.5)
    save(fig, "de3_bai4.png")


# ---------------- Đề 4 – Bài 4 ----------------
def de4_bai4():
    fig, ax = new(4.2, 2.6)
    B, C = (0, 0), (4, 0)
    t = 4 / (math.cos(math.radians(60)) + math.sin(math.radians(60)))
    A = along(B, 60, t)
    line(ax, A, B); line(ax, B, C); line(ax, C, A)
    line(ax, (-0.8, A[1]), (4.8, A[1]))
    ax.text(4.95, A[1], "a", fontsize=12, style="italic", va="center")
    pt(ax, A, "A", 0, 0.25); pt(ax, B, "B", -0.2, -0.18); pt(ax, C, "C", 0.2, -0.18)
    angle(ax, B, 0, 60, r=0.4, label=r"$60^\circ$", lr=0.75, size=9)
    angle(ax, C, 135, 180, r=0.45, label=r"$45^\circ$", lr=0.85, size=9)
    angle(ax, A, 180, 240, r=0.3, label="1", lr=0.52)
    angle(ax, A, 315, 360, r=0.3, label="2", lr=0.52)
    save(fig, "de4_bai4.png")


# ---------------- Đề 5 – Bài 4 ----------------
def de5_bai4():
    fig, ax = new()
    A = (2, 2)
    B = along(A, -70, 2 / math.sin(math.radians(70)))
    line(ax, (-0.3, 2), (5, 2)); line(ax, (-0.3, 0), (5, 0))
    line(ax, along(A, 110, 0.8), along(B, -70, 0.8))
    ax.text(5.15, 2, "a", fontsize=12, style="italic", va="center")
    ax.text(5.15, 0, "b", fontsize=12, style="italic", va="center")
    e = along(A, 110, 0.8)
    ax.text(e[0] - 0.15, e[1], "c", fontsize=12, style="italic", va="center")
    pt(ax, A, "A", -0.3, -0.22); pt(ax, B, "B", 0.3, -0.22)
    angle(ax, A, 0, 110, r=0.3, label="1", lr=0.5)
    angle(ax, A, -70, 0, r=0.3, label="2", lr=0.5)
    angle(ax, B, 0, 110, r=0.3, label="1", lr=0.5)
    angle(ax, B, 110, 180, r=0.3, label="2", lr=0.5)
    save(fig, "de5_bai4.png")


# ---------------- Hình cho đáp án Bài 5 ----------------
def de1_bai5():
    fig, ax = new(2.8, 2.4)
    A, B, C, M = (2, 3), (0, 0), (4, 0), (2, 0)
    for p, q in ((A, B), (A, C), (B, C), (A, M)):
        line(ax, p, q)
    tick(ax, A, B); tick(ax, A, C); tick(ax, B, M, 2); tick(ax, M, C, 2)
    pt(ax, A, "A", 0, 0.25); pt(ax, B, "B", -0.22, -0.15); pt(ax, C, "C", 0.22, -0.15); pt(ax, M, "M", 0, -0.25)
    save(fig, "de1_bai5.png")


def de2_bai5():
    fig, ax = new(3.0, 2.5)
    O = (0, 0)
    A, B = along(O, 0, 2.5), along(O, 70, 2.5)
    C = along(O, 35, 3.6)
    line(ax, O, along(O, 0, 4.2)); line(ax, O, along(O, 70, 3.6))
    line(ax, O, C); line(ax, A, C); line(ax, B, C)
    tick(ax, O, A); tick(ax, O, B); tick(ax, A, C, 2); tick(ax, B, C, 2)
    ax.text(4.3, 0, "x", fontsize=12, style="italic", va="center")
    e = along(O, 70, 3.6); ax.text(e[0], e[1] + 0.15, "y", fontsize=12, style="italic", ha="center")
    pt(ax, O, "O", -0.2, -0.1); pt(ax, A, "A", 0, -0.22); pt(ax, B, "B", -0.22, 0.05); pt(ax, C, "C", 0.22, 0.1)
    save(fig, "de2_bai5.png")


def de3_bai5():
    fig, ax = new(3.0, 2.6)
    A, B = (0, 0), (4, 0)
    C, D = (1.5, 1.8), (1.5, -1.8)
    for p, q in ((A, B), (A, C), (C, B), (A, D), (D, B)):
        line(ax, p, q)
    tick(ax, A, C); tick(ax, A, D); tick(ax, C, B, 2); tick(ax, D, B, 2)
    pt(ax, A, "A", -0.22, 0); pt(ax, B, "B", 0.22, 0); pt(ax, C, "C", 0, 0.22); pt(ax, D, "D", 0, -0.22)
    save(fig, "de3_bai5.png")


def de4_bai5():
    fig, ax = new(3.2, 1.8)
    A, B, C, D = (1, 2), (4.5, 2), (3.5, 0), (0, 0)
    for p, q in ((A, B), (B, C), (C, D), (D, A), (B, D)):
        line(ax, p, q)
    tick(ax, A, B); tick(ax, D, C); tick(ax, A, D, 2); tick(ax, B, C, 2)
    pt(ax, A, "A", -0.15, 0.2); pt(ax, B, "B", 0.15, 0.2); pt(ax, C, "C", 0.15, -0.2); pt(ax, D, "D", -0.15, -0.2)
    save(fig, "de4_bai5.png")


def de5_bai5():
    fig, ax = new(3.0, 1.8)
    B, C, A, D = (0, 0), (4, 0), (1, 2), (3, 2)
    O = (2, 4 / 3)
    for p, q in ((A, B), (B, C), (C, D), (A, C), (B, D), (A, D)):
        line(ax, p, q)
    tick(ax, A, B); tick(ax, D, C)
    pt(ax, A, "A", -0.12, 0.22); pt(ax, D, "D", 0.12, 0.22); pt(ax, B, "B", -0.2, -0.15)
    pt(ax, C, "C", 0.2, -0.15); pt(ax, O, "O", 0, -0.25)
    save(fig, "de5_bai5.png")


ALL = (de1_bai4, de2_bai4, de3_bai4, de4_bai4, de5_bai4, de1_bai5, de2_bai5, de3_bai5, de4_bai5, de5_bai5)

if __name__ == "__main__":
    OUT = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(OUT, exist_ok=True)
    for f in ALL:
        f()
    print("done")
