"""
American Option Pricing — Binomial Tree & LSMC with SpaceX/SPCX Case Study
Computer Based Investment Analysis · Frankfurt UAS · Summer 2026
Authors: Ilyos Umurzakov, Leon Ye
Run: streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="American Option Pricing · FRA UAS",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── COLOUR PALETTE ─────────────────────────────────────────────────────────────
BG   = "#0d1117"
BG2  = "#161b22"
BD   = "#30363d"
TXT  = "#e6edf3"
MUT  = "#8b949e"
BLUE = "#58a6ff"
LBLU = "#79c0ff"
GRN  = "#3fb950"
RED  = "#f85149"
ORG  = "#f0883e"
PRP  = "#d2a8ff"

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  section[data-testid="stSidebar"]       { display:none !important; }
  button[data-testid="collapsedControl"] { display:none !important; }
  html,body,[class*="css"]               { font-size:17px !important; }
  h1  { font-size:2.6rem !important; color:#79c0ff !important; font-weight:800 !important; }
  h2  { font-size:1.8rem !important; color:#a5d6ff !important; font-weight:700 !important;
        margin-top:2rem !important; }
  h3  { font-size:1.3rem !important; color:#e6edf3 !important; font-weight:600 !important; }
  p,li{ font-size:1.05rem !important; line-height:1.75 !important; }

  .kpi { background:linear-gradient(135deg,#1a2744 0%,#0d1117 100%);
         border:1px solid #1f6feb; border-radius:12px;
         padding:22px 16px; text-align:center; margin-bottom:8px; }
  .kpi-val { font-size:2.2rem; font-weight:800; color:#58a6ff; }
  .kpi-lbl { font-size:0.85rem; color:#8b949e; margin-top:6px; }

  .card { background:#161b22; border:1px solid #30363d; border-radius:12px;
          padding:20px 24px; margin:8px 0; }
  .card-h { font-size:1.1rem; font-weight:700; color:#79c0ff; margin-bottom:10px; }
  .card-b { font-size:1.0rem; color:#c9d1d9; line-height:1.7; }

  .find { background:#0d2a1a; border-left:5px solid #3fb950; border-radius:0 8px 8px 0;
          padding:14px 18px; margin:12px 0; color:#aff1b6; font-size:1.05rem; }
  .warn { background:#2a1a0d; border-left:5px solid #f0883e; border-radius:0 8px 8px 0;
          padding:14px 18px; margin:12px 0; color:#ffa657; font-size:1.05rem; }
  .info { background:#0d1f3a; border-left:5px solid #58a6ff; border-radius:0 8px 8px 0;
          padding:14px 18px; margin:12px 0; color:#bfdbfe; font-size:1.05rem; }
  .ans  { background:#1a0d2a; border-left:5px solid #d2a8ff; border-radius:0 8px 8px 0;
          padding:16px 20px; margin:18px 0; color:#e2c8ff; font-size:1.05rem; }

  .step { background:#161b22; border:1px solid #30363d; border-radius:10px;
          padding:16px 20px; margin:6px 0; }
  .step-num { font-size:0.75rem; color:#58a6ff; text-transform:uppercase;
              letter-spacing:3px; font-weight:700; margin-bottom:6px; }
  .step-head { font-size:1.1rem; font-weight:700; color:#e6edf3; margin-bottom:8px; }
  .step-body { font-size:0.97rem; color:#c9d1d9; line-height:1.65; }
</style>
""", unsafe_allow_html=True)

# ── NAVIGATION ─────────────────────────────────────────────────────────────────
SLIDES = [
    "📖  Introduction",
    "🌳  Binomial Tree",
    "🎲  LSMC",
    "✅  Base Case",
    "🚀  SpaceX/SPCX",
    "📌  Conclusion",
]

if "slide" not in st.session_state:
    st.session_state.slide = 0

nav_cols = st.columns(len(SLIDES))
for i, (col, label) in enumerate(zip(nav_cols, SLIDES)):
    with col:
        if st.button(label, use_container_width=True, key=f"nav_{i}",
                     type="primary" if st.session_state.slide == i else "secondary"):
            st.session_state.slide = i
            st.rerun()

st.markdown("<hr style='border:1px solid #30363d;margin:0.4rem 0 1.5rem 0;'>",
            unsafe_allow_html=True)

slide = st.session_state.slide

# ── PLOTLY LAYOUT HELPER ───────────────────────────────────────────────────────
def lo(h=460, title="", xlab="", ylab=""):
    d = dict(
        paper_bgcolor=BG, plot_bgcolor=BG2,
        font=dict(color=TXT, size=13),
        xaxis=dict(gridcolor=BD, linecolor="#484f58", linewidth=1, color=TXT,
                   title=xlab, title_font=dict(size=13)),
        yaxis=dict(gridcolor=BD, linecolor="#484f58", linewidth=1, color=TXT,
                   title=ylab, title_font=dict(size=13)),
        legend=dict(bgcolor="rgba(22,27,34,0.92)", bordercolor=BD,
                    borderwidth=1, font=dict(size=12, color=TXT)),
        margin=dict(l=65, r=25, t=55 if title else 30, b=60),
        height=h, hovermode="x unified",
    )
    if title:
        d["title"] = dict(text=title, font=dict(size=15, color=LBLU))
    return d

# ── PRICING FUNCTIONS ──────────────────────────────────────────────────────────
@st.cache_data
def binomial_price(S0, K, r, sigma, T, N, american=True):
    dt   = T / N
    u    = np.exp(sigma * np.sqrt(dt))
    d    = 1 / u
    p    = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    vals = [max(K - S0 * u**j * d**(N - j), 0) for j in range(N + 1)]
    for step in range(N - 1, -1, -1):
        nv = []
        for j in range(step + 1):
            stk  = S0 * u**j * d**(step - j)
            cont = disc * (p * vals[j + 1] + (1 - p) * vals[j])
            ex   = max(K - stk, 0)
            nv.append(max(cont, ex) if american else cont)
        vals = nv
    return vals[0]

@st.cache_data
def black_scholes_put(S, K, r, sigma, T):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

@st.cache_data
def simulate_paths(S0, r, sigma, T, N, num_paths, seed=42):
    rng   = np.random.default_rng(seed)
    dt    = T / N
    paths = np.zeros((num_paths, N + 1))
    paths[:, 0] = S0
    for t in range(1, N + 1):
        z = rng.standard_normal(num_paths)
        paths[:, t] = paths[:, t - 1] * np.exp(
            (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z)
    return paths

@st.cache_data
def lsmc_put(S0, K, r, sigma, T, N, num_paths, seed=42):
    paths     = simulate_paths(S0, r, sigma, T, N, num_paths, seed)
    dt        = T / N
    disc      = np.exp(-r * dt)
    cashflows = np.maximum(K - paths[:, -1], 0)
    for t in range(N - 1, 0, -1):
        cashflows *= disc
        stock    = paths[:, t]
        exercise = np.maximum(K - stock, 0)
        itm      = exercise > 0
        if itm.sum() < 3:
            continue
        x    = stock[itm]
        X    = np.column_stack([np.ones_like(x), x, x**2])
        beta = np.linalg.lstsq(X, cashflows[itm], rcond=None)[0]
        cont = X @ beta
        idx  = np.where(itm)[0][exercise[itm] > cont]
        cashflows[idx] = exercise[idx]
    return np.mean(cashflows * disc)

@st.cache_data
def implied_vol(market_price, S0, K, r, T, N):
    lo, hi = 0.01, 3.00
    for _ in range(80):
        mid = (lo + hi) / 2
        if binomial_price(S0, K, r, mid, T, N) < market_price:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

@st.cache_data
def small_tree(S0, K, r, sigma, T, N_vis=4):
    dt   = T / N_vis
    u    = np.exp(sigma * np.sqrt(dt))
    d    = 1 / u
    p    = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    stock    = [[S0 * u**j * d**(t - j) for j in range(t + 1)] for t in range(N_vis + 1)]
    values   = [None] * (N_vis + 1)
    exercise = [None] * (N_vis + 1)
    values[-1]   = [max(K - s, 0) for s in stock[-1]]
    exercise[-1] = [False] * (N_vis + 1)
    current = values[-1]
    for t in range(N_vis - 1, -1, -1):
        values[t], exercise[t] = [], []
        for j in range(t + 1):
            cont = disc * (p * current[j + 1] + (1 - p) * current[j])
            ex   = max(K - stock[t][j], 0)
            values[t].append(max(cont, ex))
            exercise[t].append(ex > cont and ex > 0)
        current = values[t]
    return stock, values, exercise

# ── PLOTLY CHART BUILDERS ──────────────────────────────────────────────────────
def chart_binom_convergence(S0, K, r, sigma, T):
    steps  = [5, 10, 20, 50, 100, 200, 500]
    prices = [binomial_price(S0, K, r, sigma, T, n, american=False) for n in steps]
    bs     = black_scholes_put(S0, K, r, sigma, T)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=steps, y=prices, mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=8, color=BLUE, line=dict(color=BG2, width=1.5)),
        name="European binomial put",
        hovertemplate="N=%{x}<br>Price=%{y:.4f} USD<extra></extra>",
    ))
    fig.add_hline(y=bs, line_color=RED, line_dash="dash", line_width=2,
                  annotation_text=f"Black–Scholes: {bs:.4f} USD",
                  annotation_font_color=RED, annotation_position="top left")
    fig.update_layout(**lo(460,
        title="Binomial European Put → Black–Scholes Convergence",
        xlab="Number of steps N", ylab="Put price (USD)"))
    return fig

def chart_lsmc_convergence(S0, K, r, sigma, T, N_ref=200):
    path_counts = [500, 1_000, 2_000, 5_000, 10_000, 20_000, 50_000]
    lsmc_prices = [lsmc_put(S0, K, r, sigma, T, 50, n) for n in path_counts]
    ref         = binomial_price(S0, K, r, sigma, T, N_ref, american=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=path_counts, y=lsmc_prices, mode="lines+markers",
        line=dict(color=GRN, width=2.5),
        marker=dict(size=8, color=GRN, line=dict(color=BG2, width=1.5)),
        name="LSMC American put",
        hovertemplate="Paths=%{x:,}<br>Price=%{y:.4f} USD<extra></extra>",
    ))
    fig.add_hline(y=ref, line_color=RED, line_dash="dash", line_width=2,
                  annotation_text=f"Binomial reference (N=200): {ref:.4f} USD",
                  annotation_font_color=RED, annotation_position="top left")
    fig.update_layout(**lo(460,
        title="LSMC American Put — Stability vs. Number of Paths",
        xlab="Number of simulated paths", ylab="American put price (USD)"))
    return fig

def chart_tree(stock, values, exercise):
    N_vis = 4
    fig   = go.Figure()

    # edges
    edge_x, edge_y = [], []
    for t in range(N_vis):
        for j in range(t + 1):
            x0, y0 = t, j - t / 2
            for dj in [0, 1]:
                x1 = t + 1
                y1 = (j + dj) - (t + 1) / 2
                edge_x += [x0, x1, None]
                edge_y += [y0, y1, None]
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(color=BD, width=2), showlegend=False, hoverinfo="skip"))

    # node circles (two layers: normal and early-exercise)
    for ex_flag, col_fill, col_border, leg_name in [
        (False, "#1a2744", BLUE, "Normal node"),
        (True,  "#2a0d0d", RED,  "Early exercise"),
    ]:
        xs, ys = [], []
        for t in range(N_vis + 1):
            for j in range(t + 1):
                if exercise[t][j] == ex_flag:
                    xs.append(t)
                    ys.append(j - t / 2)
        if xs:
            fig.add_trace(go.Scatter(
                x=xs, y=ys, mode="markers",
                marker=dict(size=52, color=col_fill,
                            line=dict(color=col_border, width=2.5)),
                name=leg_name, hoverinfo="skip"))

    # text annotations inside nodes
    for t in range(N_vis + 1):
        for j in range(t + 1):
            fig.add_annotation(
                x=t, y=j - t / 2,
                text=f"<b>S={stock[t][j]:.0f}</b><br>V={values[t][j]:.2f}",
                showarrow=False, align="center",
                font=dict(size=10.5,
                          color="#ffa6a6" if exercise[t][j] else "#c9d1d9"),
            )

    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=TXT, size=13),
        xaxis=dict(showgrid=False, zeroline=False, tickvals=list(range(5)),
                   ticktext=["t = 0", "t = 1", "t = 2", "t = 3", "t = 4"],
                   linecolor="#484f58"),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(bgcolor="rgba(22,27,34,0.9)", bordercolor=BD,
                    borderwidth=1, font=dict(size=12, color=TXT),
                    orientation="h", x=0, y=-0.08),
        margin=dict(l=20, r=20, t=55, b=60),
        height=520,
        title=dict(text="SpaceX/SPCX American Put — Binomial Tree "
                        "(4-step visual, N = 200 for pricing)",
                   font=dict(size=15, color=LBLU)),
    )
    return fig

def chart_mc(paths, strike, S0):
    time_grid        = np.linspace(0, 93 / 365, paths.shape[1])
    terminal_prices  = paths[:, -1]
    terminal_payoffs = np.maximum(strike - terminal_prices, 0)

    fig = go.Figure()
    for i in range(100):
        fig.add_trace(go.Scatter(
            x=time_grid, y=paths[i],
            mode="lines", line=dict(color=f"rgba(88,166,255,0.12)", width=0.9),
            showlegend=False, hoverinfo="skip",
        ))
    fig.add_hline(y=strike, line_color=RED, line_dash="dash", line_width=2,
                  annotation_text=f"Strike: {strike} USD",
                  annotation_font_color=RED)
    fig.update_layout(**lo(480,
        title="Simulated SpaceX/SPCX Stock Paths (100 of 50,000)",
        xlab="Time to maturity (years)", ylab="Stock price (USD)"))
    return fig, terminal_prices, terminal_payoffs

def chart_terminal_dist(terminal_prices, strike, S0):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=terminal_prices, nbinsx=60,
        marker=dict(color=ORG, opacity=0.8, line=dict(color=BG2, width=0.4)),
        name="Terminal price",
        hovertemplate="Price bin=%{x:.0f} USD<br>Count=%{y}<extra></extra>",
    ))
    fig.add_vline(x=strike, line_color=RED, line_dash="dash", line_width=2,
                  annotation_text=f"Strike: {strike} USD",
                  annotation_font_color=RED)
    fig.add_vline(x=S0, line_color=GRN, line_dash="dot", line_width=2,
                  annotation_text=f"S₀: {S0} USD",
                  annotation_font_color=GRN)
    fig.update_layout(**lo(480,
        title="Terminal Stock Price Distribution",
        xlab="Terminal price (USD)", ylab="Number of paths"))
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 0 — INTRODUCTION
# ══════════════════════════════════════════════════════════════════════════════
if slide == 0:
    st.markdown("# Pricing of American Options")
    st.markdown(
        "#### Binomial Tree & Least-Squares Monte Carlo with a SpaceX/SPCX Case Study")
    st.markdown(
        "*Computer Based Investment Analysis · Frankfurt UAS · Summer 2026*  \n"
        "**Authors:** Ilyos Umurzakov · Leon Ye &nbsp;|&nbsp; "
        "**Lecturers:** Ferdinand Wöhrle · Lukas Müller")

    st.markdown("<hr class='sec-rule' style='border-top:2px solid #1f6feb;margin:1.5rem 0;'>",
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown("""<div class='kpi'>
        <div class='kpi-val'>2</div>
        <div class='kpi-lbl'>Numerical methods compared</div></div>""",
        unsafe_allow_html=True)
    c2.markdown("""<div class='kpi'>
        <div class='kpi-val'>107.4%</div>
        <div class='kpi-lbl'>Implied volatility — SpaceX/SPCX</div></div>""",
        unsafe_allow_html=True)
    c3.markdown("""<div class='kpi'>
        <div class='kpi-val'>$1,130</div>
        <div class='kpi-lbl'>Market premium per contract</div></div>""",
        unsafe_allow_html=True)

    st.markdown("## What is an American Option?")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""<div class='card'>
        <div class='card-h'>European vs. American</div>
        <div class='card-b'>
        A <b>European option</b> can only be exercised at expiry.<br><br>
        An <b>American option</b> can be exercised at <em>any point</em> before expiry.
        This flexibility makes it at least as valuable — and much harder to price.
        </div></div>""", unsafe_allow_html=True)

        st.markdown("""<div class='card'>
        <div class='card-h'>Early Exercise Premium</div>
        <div class='card-b'>
        The extra value of the American right is the <em>early exercise premium</em>:<br><br>
        <b>V<sub>American</sub> ≥ V<sub>European</sub></b><br><br>
        For a <b>put</b> on a non-dividend stock, early exercise can be optimal when
        the stock price is very low — the holder may prefer to receive the strike price
        immediately rather than waiting.
        </div></div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("""<div class='card'>
        <div class='card-h'>Why No Closed Form?</div>
        <div class='card-b'>
        Black–Scholes gives a closed-form price for <em>European</em> options.
        For American options, early exercise creates a free-boundary problem:
        the holder must decide at <em>every moment</em> whether to exercise.
        This makes a simple formula impossible. We need numerical methods.
        </div></div>""", unsafe_allow_html=True)

        st.markdown("""<div class='card'>
        <div class='card-h'>This Paper</div>
        <div class='card-b'>
        <b>Method 1 — CRR Binomial Tree:</b> builds a discrete price lattice and prices
        the option by backward induction. Transparent and explainable.<br><br>
        <b>Method 2 — LSMC:</b> simulates thousands of stock paths and estimates the
        continuation value at each step with regression. Flexible and scalable.<br><br>
        <b>Case study:</b> September 2026 SpaceX/SPCX put, strike 135 USD.
        </div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class='info'>
    <b>Key question:</b> How large is the early exercise premium for the SpaceX put?
    And what does the market's 107% implied volatility tell us about future expectations?
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 1 — BINOMIAL TREE
# ══════════════════════════════════════════════════════════════════════════════
elif slide == 1:
    st.markdown("## 🌳 Method 1: CRR Binomial Tree")
    st.markdown("*Cox, Ross & Rubinstein (1979)*")

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("### Model Setup")
        st.markdown("The stock price moves **up** or **down** at each discrete time step:")
        st.latex(r"\Delta t = \frac{T}{N}")
        st.latex(r"u = e^{\sigma\sqrt{\Delta t}}, \quad d = \frac{1}{u}")
        st.markdown("The **risk-neutral probability** of an up move:")
        st.latex(r"p = \frac{e^{r\,\Delta t} - d}{u - d}")
        st.markdown(
            "This is not a real-world forecast — it is a pricing tool that lets us "
            "discount expected payoffs at the risk-free rate.")

        st.markdown("### Backward Induction")
        st.markdown("At maturity, the put payoff at each node is max(K − S, 0).  \n"
                    "Working backwards, the **continuation value** at each node is:")
        st.latex(r"C = e^{-r\,\Delta t}\,(p\,V_{\text{up}} + (1-p)\,V_{\text{down}})")
        st.markdown("For an American option:")
        st.latex(r"V = \max\!\bigl(C,\; K - S\bigr)")
        st.markdown(
            "The **max** is the core of American option pricing. "
            "It compares waiting (C) with exercising immediately (K − S).")

    with col_r:
        st.markdown("### Strengths & Limitations")
        for num, head, body in [
            ("01", "Transparency",
             "Every single node is interpretable. You can trace exactly why the "
             "option is exercised at a specific stock price and time step."),
            ("02", "Accuracy with N",
             "More steps → finer tree → European price converges to Black–Scholes. "
             "N = 200 is more than sufficient for 4-decimal accuracy."),
            ("03", "Limitation: Computation",
             "The tree has (N+1)(N+2)/2 nodes. At N = 200 that is ~20,000 nodes, "
             "but it remains fast for a single underlying asset."),
            ("04", "Limitation: Simplicity",
             "Constant volatility and interest rate. No dividends in our case study. "
             "Extensions exist but complicate the model."),
        ]:
            st.markdown(f"""<div class='step'>
            <div class='step-num'>Point {num}</div>
            <div class='step-head'>{head}</div>
            <div class='step-body'>{body}</div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class='find'>
    <b>Key insight:</b> The binomial tree turns a continuous-time decision problem
    into a finite sequence of binary choices. The American put price is the value
    at the root node (t = 0) after backward induction.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 2 — LSMC
# ══════════════════════════════════════════════════════════════════════════════
elif slide == 2:
    st.markdown("## 🎲 Method 2: Least-Squares Monte Carlo")
    st.markdown("*Longstaff & Schwartz (2001)*")

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("### Why Plain Monte Carlo Fails")
        st.markdown("""<div class='warn'>
        Standard Monte Carlo only uses the <b>terminal payoff</b>. This works for
        European options, but American holders can exercise <em>before</em> maturity.
        At each step, the holder must compare:<br><br>
        <b>Immediate exercise value</b> vs. <b>Expected value of waiting</b><br><br>
        The future value depends on unknown future paths — we cannot calculate it directly.
        </div>""", unsafe_allow_html=True)

        st.markdown("### The LSMC Solution")
        st.markdown("Simulate many paths with **risk-neutral GBM**:")
        st.latex(
            r"S_{t+\Delta t} = S_t \cdot \exp\!\left[\left(r - \tfrac12\sigma^2\right)"
            r"\Delta t + \sigma\sqrt{\Delta t}\,Z\right]")
        st.markdown(
            "Then **work backward** from maturity. At each step, estimate the "
            "continuation value by regressing discounted future cashflows on:")
        st.latex(r"\text{Basis functions: } 1,\; S,\; S^2")
        st.markdown(
            "Only **in-the-money** paths are included in the regression — "
            "out-of-the-money options would never be exercised, so they are irrelevant.")

    with col_r:
        st.markdown("### Algorithm Step by Step")
        for num, head, body in [
            ("01", "Simulate paths",
             "Generate num_paths stock price trajectories using GBM under the "
             "risk-neutral measure, from t = 0 to t = T."),
            ("02", "Terminal payoffs",
             "At maturity T, calculate max(K − S_T, 0) for each path. "
             "These are the starting cashflows for the backward pass."),
            ("03", "Backward regression",
             "At each time step t (moving backward), discount cashflows one step. "
             "For ITM paths, regress cashflows on [1, S_t, S_t²] to estimate "
             "the continuation value."),
            ("04", "Exercise decision",
             "If exercise value > fitted continuation value, update cashflow "
             "to the exercise value for that path."),
            ("05", "Final price",
             "Average all cashflows and apply one final discounting step "
             "to get the American put price at t = 0."),
        ]:
            st.markdown(f"""<div class='step'>
            <div class='step-num'>Step {num}</div>
            <div class='step-head'>{head}</div>
            <div class='step-body'>{body}</div></div>""", unsafe_allow_html=True)

    st.markdown("""<div class='info'>
    <b>Key difference vs. binomial tree:</b> The binomial tree calculates the
    continuation value exactly from two branches. LSMC <em>estimates</em> it
    statistically from many paths. Both should give similar answers — differences
    are expected simulation noise, not errors.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 3 — BASE CASE
# ══════════════════════════════════════════════════════════════════════════════
elif slide == 3:
    st.markdown("## ✅ Base Case Validation")
    st.markdown(
        "Standard at-the-money inputs from the options pricing literature.  \n"
        "Goal: confirm that both methods agree and that the binomial tree "
        "converges to Black–Scholes for European options.")

    # ── inputs
    col_in, col_res = st.columns([1, 1.4])
    with col_in:
        st.markdown("### Inputs")
        inp = pd.DataFrame({
            "Parameter": ["Stock price S₀", "Strike K", "Risk-free rate r",
                          "Volatility σ", "Maturity T"],
            "Value":     ["100 USD", "100 USD (ATM)", "5% p.a.", "20% p.a.", "1 year"],
        })
        st.dataframe(inp, hide_index=True, use_container_width=True)

    # ── compute
    S0_bc, K_bc, r_bc, sig_bc, T_bc = 100, 100, 0.05, 0.20, 1.0
    bs    = black_scholes_put(S0_bc, K_bc, r_bc, sig_bc, T_bc)
    b_eur = binomial_price(S0_bc, K_bc, r_bc, sig_bc, T_bc, 200, american=False)
    b_am  = binomial_price(S0_bc, K_bc, r_bc, sig_bc, T_bc, 200, american=True)
    l_am  = lsmc_put(S0_bc, K_bc, r_bc, sig_bc, T_bc, 200, 50_000)
    ee    = b_am - b_eur

    with col_res:
        st.markdown("### Results")
        res = pd.DataFrame({
            "Measure": [
                "Black–Scholes European put",
                "Binomial European put (N=200)",
                "Binomial American put (N=200)",
                "LSMC American put (50,000 paths)",
                "Early exercise premium",
            ],
            "Value (USD)": [f"{bs:.4f}", f"{b_eur:.4f}", f"{b_am:.4f}",
                            f"{l_am:.4f}", f"{ee:.4f}"],
        })
        st.dataframe(res, hide_index=True, use_container_width=True)

    st.markdown("---")

    # ── highlight boxes
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"""<div class='kpi'>
        <div class='kpi-val'>{bs:.2f} USD</div>
        <div class='kpi-lbl'>Black–Scholes European put</div></div>""",
        unsafe_allow_html=True)
    c2.markdown(f"""<div class='kpi'>
        <div class='kpi-val'>{b_am:.2f} USD</div>
        <div class='kpi-lbl'>Binomial American put</div></div>""",
        unsafe_allow_html=True)
    c3.markdown(f"""<div class='kpi'>
        <div class='kpi-val'>{ee:.4f} USD</div>
        <div class='kpi-lbl'>Early exercise premium</div></div>""",
        unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Convergence Plots")

    tab1, tab2 = st.tabs(["📉 Binomial → Black–Scholes", "🎲 LSMC stability"])
    with tab1:
        st.plotly_chart(chart_binom_convergence(S0_bc, K_bc, r_bc, sig_bc, T_bc),
                        use_container_width=True)
        st.markdown("""<div class='find'>
        The European binomial put converges rapidly to the Black–Scholes benchmark.
        Already at N = 50 the difference is less than 1 cent. At N = 200 it is
        virtually indistinguishable — confirming the implementation is correct.
        </div>""", unsafe_allow_html=True)

    with tab2:
        st.plotly_chart(chart_lsmc_convergence(S0_bc, K_bc, r_bc, sig_bc, T_bc),
                        use_container_width=True)
        st.markdown("""<div class='find'>
        With only 500 paths, LSMC is noisy. By 10,000 paths it stabilises near the
        binomial reference. At 50,000 paths the estimate is reliable. Remaining
        differences from the binomial are normal simulation and regression error.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 4 — SPACEX / SPCX CASE STUDY
# ══════════════════════════════════════════════════════════════════════════════
elif slide == 4:
    st.markdown("## 🚀 SpaceX/SPCX Case Study")

    # ── context KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown("""<div class='kpi'>
        <div class='kpi-val'>$135</div>
        <div class='kpi-lbl'>IPO price · 12 Jun 2026</div></div>""",
        unsafe_allow_html=True)
    c2.markdown("""<div class='kpi'>
        <div class='kpi-val'>$201.80</div>
        <div class='kpi-lbl'>Stock price · 16 Jun 2026</div></div>""",
        unsafe_allow_html=True)
    c3.markdown("""<div class='kpi'>
        <div class='kpi-val'>$1,130</div>
        <div class='kpi-lbl'>Market premium per contract</div></div>""",
        unsafe_allow_html=True)
    c4.markdown("""<div class='kpi'>
        <div class='kpi-val'>93 days</div>
        <div class='kpi-lbl'>Time to Sep 18, 2026 expiry</div></div>""",
        unsafe_allow_html=True)

    st.markdown("""<div class='info'>
    SpaceX (ticker: SPCX) listed at 135 USD on 12 June 2026 and rose sharply to
    201.80 USD by 16 June. On that day, exchange options were launched. A September
    2026 put at the IPO strike of 135 USD traded at <b>11.30 USD per share
    (1,130 USD per contract)</b>. This is our case study.
    </div>""", unsafe_allow_html=True)

    # ── compute
    S0, K, r, T = 201.80, 135, 0.037, 93 / 365
    mkt = 11.30
    N   = 200

    with st.spinner("Computing implied volatility and model prices…"):
        sigma_iv  = implied_vol(mkt, S0, K, r, T, N)
        b_am_sx   = binomial_price(S0, K, r, sigma_iv, T, N, american=True)
        b_eu_sx   = binomial_price(S0, K, r, sigma_iv, T, N, american=False)
        l_am_sx   = lsmc_put(S0, K, r, sigma_iv, T, N, 50_000)
        ee_sx     = b_am_sx - b_eu_sx

    st.markdown("---")

    col_l, col_r = st.columns([1, 1])

    with col_l:
        st.markdown("### Implied Volatility")
        st.markdown("""<div class='ans'>
        We <em>reverse</em> the pricing model: instead of asking "what price does a
        given volatility produce?", we ask<br><br>
        <b>"Which volatility makes the model match the 11.30 USD market price?"</b><br><br>
        The answer is found by bisection search over σ.
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class='kpi' style='margin-top:16px;'>
            <div class='kpi-val'>{sigma_iv*100:.1f}%</div>
            <div class='kpi-lbl'>Implied volatility σ<sub>IV</sub></div></div>""",
            unsafe_allow_html=True)

        st.markdown("""<div class='warn' style='margin-top:12px;'>
        A typical stock has σ ≈ 20–30%. SpaceX/SPCX shows ~107% because the option
        is <b>deeply out of the money</b> (stock at 201.80 vs. strike at 135) and
        the market expects <b>extreme price swings</b> from a newly-listed stock.
        </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("### Model Results")
        res_sx = pd.DataFrame({
            "Measure": [
                "Market price per share",
                "Market price per contract (×100)",
                "Implied volatility σ_IV",
                "Binomial American put",
                "Binomial European put",
                "LSMC American put",
                "Early exercise premium",
            ],
            "Value": [
                f"{mkt:.2f} USD",
                f"{mkt*100:.2f} USD",
                f"{sigma_iv*100:.2f}%",
                f"{b_am_sx:.4f} USD",
                f"{b_eu_sx:.4f} USD",
                f"{l_am_sx:.4f} USD",
                f"{ee_sx:.4f} USD",
            ],
        })
        st.dataframe(res_sx, hide_index=True, use_container_width=True)

        st.markdown(f"""<div class='find' style='margin-top:12px;'>
        <b>Key finding:</b> The early exercise premium is only
        <b>{ee_sx:.4f} USD</b> out of a total price of {mkt:.2f} USD.
        That is less than 0.3% of the contract value. The price is almost
        entirely driven by <em>high implied volatility</em>, not early exercise.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Visualisations")
    tab_tree, tab_mc = st.tabs(["🌳 Binomial Tree", "🎲 Monte Carlo Simulation"])

    with tab_tree:
        stk, vals, ex = small_tree(S0, K, r, sigma_iv, T, N_vis=4)
        st.plotly_chart(chart_tree(stk, vals, ex), use_container_width=True)
        st.markdown("""<div class='info'>
        Each node shows the stock price S and the American put value V.
        <span style='color:#f85149;'><b>Red nodes</b></span> indicate where immediate
        exercise is optimal in this 4-step visual tree. The actual pricing uses 200 steps.
        Because the stock starts far above the strike, most upper nodes have zero put value
        and exercise only appears in the lower-left region of the tree.
        </div>""", unsafe_allow_html=True)

    with tab_mc:
        with st.spinner("Simulating 50,000 paths…"):
            paths = simulate_paths(S0, r, sigma_iv, T, N, 50_000, seed=42)
        fig_mc, term_prices, term_payoffs = chart_mc(paths, K, S0)
        fig_dist = chart_terminal_dist(term_prices, K, S0)

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            st.plotly_chart(fig_mc, use_container_width=True)
        with col_mc2:
            st.plotly_chart(fig_dist, use_container_width=True)

        st.markdown(f"""<div class='find'>
        Average undiscounted terminal put payoff across all 50,000 paths:
        <b>{np.mean(term_payoffs):.2f} USD</b>.
        Only paths ending below 135 USD generate a payoff. The LSMC method
        applies regression backward through time to decide whether early exercise
        on any individual path is preferable to waiting until expiry.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SLIDE 5 — CONCLUSION
# ══════════════════════════════════════════════════════════════════════════════
elif slide == 5:
    st.markdown("## 📌 Conclusion")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Method Comparison")
        comp = pd.DataFrame({
            "Criterion":     ["Transparency", "Speed", "Accuracy",
                              "Flexibility", "Best for"],
            "Binomial Tree": ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐",
                              "⭐⭐", "Teaching & single underlying"],
            "LSMC":          ["⭐⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐",
                              "⭐⭐⭐⭐⭐", "Complex/multi-factor options"],
        })
        st.dataframe(comp, hide_index=True, use_container_width=True)

        st.markdown("### Black–Scholes Role")
        st.markdown("""<div class='warn'>
        Black–Scholes is used <b>only as a European benchmark</b> to validate
        the binomial tree's convergence. It <em>cannot</em> price American options
        because it does not model the early exercise decision.
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown("### SpaceX/SPCX Findings")
        for label, val, note in [
            ("Implied Volatility", "107.4%",
             "Consistent with a newly-listed stock where the market expects extreme moves"),
            ("Binomial American Put", "11.30 USD",
             "Calibrated exactly to the market premium — confirms the model"),
            ("Early Exercise Premium", "0.03 USD",
             "Just 0.3% of the option value — early exercise is almost irrelevant here"),
            ("LSMC American Put", "≈ 11.30 USD",
             "Both methods agree closely — confirming robustness of the result"),
        ]:
            st.markdown(f"""<div class='step'>
            <div class='step-num'>{label}</div>
            <div class='step-head'>{val}</div>
            <div class='step-body'>{note}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div class='ans'>
    <b>Main conclusion:</b> For the SpaceX/SPCX September 135 put,
    the 1,130 USD contract price is almost entirely a <em>volatility story</em>
    — not an early exercise story. The option is deeply out of the money
    (stock at 201.80 vs. strike at 135), so immediate exercise is never attractive.
    The market's expectation of extreme price movements — reflected in an implied
    volatility of ~107% — is what drives the premium.
    The American early exercise feature is present and correctly modelled,
    but contributes only ~0.03 USD to the 11.30 USD price.
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "*Frankfurt University of Applied Sciences · Computer Based Investment Analysis · "
        "Summer Semester 2026*  \n"
        "Ilyos Umurzakov (1615067) · Leon Ye (1616910)  \n"
        "Lecturers: Ferdinand Wöhrle · Lukas Müller")
