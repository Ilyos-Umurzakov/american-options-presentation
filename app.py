import base64, math, pathlib
import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="American Option Pricing",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; }
html, body, [data-testid="stAppViewContainer"] { background-color: #07070f; color: #ffffff; }
[data-testid="stHeader"] { background: rgba(7,7,15,0.97); }
[data-testid="stSidebar"] { background: #0d0d1a; }
.block-container { padding: 0 2rem 4rem 2rem; max-width: 1400px; margin: auto; }
#MainMenu, footer, [data-testid="stToolbar"] { display:none !important; }

.cover {
    background: linear-gradient(135deg, #0a0a20 0%, #1a0533 40%, #001a3d 100%);
    border: 1px solid rgba(0,212,255,0.12); border-radius: 24px;
    padding: 64px 60px 56px; margin: 24px 0 40px;
    position: relative; overflow: hidden; text-align: center;
}
.cover::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(ellipse at 25% 60%, rgba(124,58,237,0.18) 0%, transparent 55%),
                radial-gradient(ellipse at 75% 40%, rgba(0,212,255,0.12) 0%, transparent 55%);
}
.cover-university { font-size:13px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:rgba(255,255,255,0.5); margin-bottom:5px; }
.cover-module { font-size:14px; color:rgba(255,255,255,0.38); margin-bottom:30px; }
.cover-badge { display:inline-block; background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.35); border-radius:50px; padding:6px 20px; font-size:12px; font-weight:700; color:#00d4ff; letter-spacing:2px; text-transform:uppercase; margin-bottom:22px; }
.cover h1 { font-size:clamp(34px,5vw,68px); font-weight:900; line-height:1.05; margin:0 0 22px; background:linear-gradient(135deg,#ffffff 0%,#00d4ff 50%,#7c3aed 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.cover-sub { font-size:19px; color:rgba(255,255,255,0.62); max-width:660px; margin:0 auto 36px; line-height:1.55; text-align:center; }
.cover-authors { display:flex; justify-content:center; gap:36px; flex-wrap:wrap; border-top:1px solid rgba(255,255,255,0.08); padding-top:28px; margin-top:8px; }
.cover-author-name { font-size:16px; font-weight:700; color:#fff; }
.cover-author-id { font-size:12px; color:rgba(255,255,255,0.42); margin-top:2px; }
.cover-prof { font-size:14px; color:rgba(255,255,255,0.5); margin-top:3px; }

.stat-card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:24px 18px; text-align:center; }
.stat-number { font-size:36px; font-weight:800; color:#00d4ff; line-height:1; }
.stat-label { font-size:12px; color:rgba(255,255,255,0.48); margin-top:8px; font-weight:500; }

.section-tag { display:inline-block; background:rgba(124,58,237,0.14); border:1px solid rgba(124,58,237,0.35); border-radius:50px; padding:4px 16px; font-size:11px; font-weight:700; color:#a78bfa; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px; }
.section-title { font-size:clamp(24px,3.5vw,44px); font-weight:800; line-height:1.1; margin:0 0 6px; }
.section-sub { font-size:16px; color:rgba(255,255,255,0.5); margin-bottom:34px; line-height:1.5; }

.card { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:20px; padding:30px; }

.step-row { display:flex; gap:12px; align-items:flex-start; margin-bottom:18px; }
.step-dot { width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:15px; font-weight:800; flex-shrink:0; }
.step-title { font-weight:600; margin-bottom:3px; font-size:15px; }
.step-desc { color:rgba(255,255,255,0.56); font-size:13px; line-height:1.6; }

.kpi-row { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:16px; }
.kpi-box { background:rgba(0,212,255,0.09); border:1px solid rgba(0,212,255,0.22); border-radius:12px; padding:14px 18px; text-align:center; flex:1; min-width:120px; }
.kpi-num { font-size:26px; font-weight:800; color:#00d4ff; line-height:1; }
.kpi-lbl { font-size:10px; color:rgba(255,255,255,0.42); margin-top:4px; }

.chip { display:inline-block; border-radius:50px; padding:6px 16px; font-size:12px; font-weight:600; margin:4px; }
.chip-blue   { background:rgba(0,212,255,0.12); border:1px solid rgba(0,212,255,0.3); color:#00d4ff; }
.chip-purple { background:rgba(124,58,237,0.12); border:1px solid rgba(124,58,237,0.3); color:#a78bfa; }
.chip-green  { background:rgba(0,255,136,0.12); border:1px solid rgba(0,255,136,0.3); color:#00ff88; }

.reco-box { background:linear-gradient(135deg,rgba(0,255,136,0.05),rgba(0,212,255,0.05)); border:2px solid rgba(0,255,136,0.28); border-radius:24px; padding:48px; text-align:center; }
.reco-verdict { font-size:48px; font-weight:900; background:linear-gradient(135deg,#00ff88,#00d4ff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:16px; }

.divider { border:none; border-top:1px solid rgba(255,255,255,0.06); margin:52px 0; }
.info-box { background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.22); border-radius:14px; padding:18px 22px; margin-top:14px; }
</style>
""", unsafe_allow_html=True)


# ── helpers ──────────────────────────────────────────────────────────────────
def c_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


@st.cache_data
def logo_b64():
    p = pathlib.Path(__file__).parent / "frauas_logo.png"
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None


# ── pricing functions ────────────────────────────────────────────────────────
@st.cache_data
def binomial_price(S0, K, r, sigma, T, N=200, option="put"):
    dt = T / N
    u  = math.exp(sigma * math.sqrt(dt))
    d  = 1 / u
    q  = (math.exp(r * dt) - d) / (u - d)
    disc = math.exp(-r * dt)
    prices = np.array([S0 * (u**j) * (d**(N - j)) for j in range(N + 1)])
    vals = np.maximum(K - prices, 0) if option == "put" else np.maximum(prices - K, 0)
    for _ in range(N - 1, -1, -1):
        prices = prices[:-1] / d
        hold   = disc * (q * vals[1:] + (1 - q) * vals[:-1])
        ex     = np.maximum(K - prices, 0) if option == "put" else np.maximum(prices - K, 0)
        vals   = np.maximum(hold, ex)
    return float(vals[0])


@st.cache_data
def black_scholes_put(S0, K, r, sigma, T):
    from scipy.stats import norm
    if T <= 0 or sigma <= 0:
        return max(K - S0, 0)
    d1 = (math.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)


@st.cache_data
def lsmc_put(S0, K, r, sigma, T, M=20000, N=50, seed=42):
    rng = np.random.default_rng(seed)
    dt  = T / N
    Z   = rng.standard_normal((M, N))
    S   = np.zeros((M, N + 1)); S[:, 0] = S0
    for t in range(N):
        S[:, t + 1] = S[:, t] * np.exp(
            (r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z[:, t]
        )
    payoff = np.maximum(K - S[:, -1], 0)
    for t in range(N - 1, 0, -1):
        itm = K - S[:, t] > 0
        if itm.sum() < 5:
            continue
        X    = S[itm, t]
        Y    = payoff[itm] * math.exp(-r * dt)
        A    = np.column_stack([np.ones_like(X), X, X**2])
        coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
        cont = A @ coef
        ex   = np.maximum(K - X, 0)
        idx  = np.where(itm)[0][ex > cont]
        payoff[idx] = ex[ex > cont]
    return float(np.mean(payoff) * math.exp(-r * T))


@st.cache_data
def implied_vol(S0, K, r, T, market_price, lo=0.01, hi=5.0, tol=1e-6):
    for _ in range(100):
        mid = (lo + hi) / 2
        v   = binomial_price(S0, K, r, mid, T)
        if abs(v - market_price) < tol:
            return mid
        lo, hi = (mid, hi) if v < market_price else (lo, mid)
    return (lo + hi) / 2


@st.cache_data
def simulate_paths(S0, r, sigma, T, M=1000, N=93, seed=42):
    rng = np.random.default_rng(seed)
    dt  = T / N
    Z   = rng.standard_normal((M, N))
    S   = np.zeros((M, N + 1)); S[:, 0] = S0
    for t in range(N):
        S[:, t + 1] = S[:, t] * np.exp(
            (r - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * Z[:, t]
        )
    return S


# ── charts ───────────────────────────────────────────────────────────────────
BG_CHART  = "rgba(0,0,0,0)"
GRID_CLR  = "rgba(255,255,255,0.06)"
CYAN  = "#00d4ff"
GREEN = "#00ff88"
RED   = "#ff4757"
PRP   = "#a78bfa"
GOLD  = "#ffa502"
TXT   = "rgba(255,255,255,0.85)"

def chart_layout(title="", h=380):
    return dict(
        paper_bgcolor=BG_CHART, plot_bgcolor=BG_CHART,
        height=h, font=dict(family="Inter", color=TXT, size=12),
        title=dict(text=title, font=dict(size=14, color=TXT), x=0.02, xanchor="left"),
        margin=dict(l=52, r=24, t=48, b=40),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, tickfont=dict(color="rgba(255,255,255,0.5)")),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, tickfont=dict(color="rgba(255,255,255,0.5)")),
        legend=dict(font=dict(color="rgba(255,255,255,0.62)"), bgcolor="rgba(0,0,0,0)"),
    )


@st.cache_data
def fig_convergence():
    steps  = [5, 10, 20, 50, 100, 200, 500, 1000]
    prices = [binomial_price(100, 100, 0.05, 0.20, 1.0, N=n) for n in steps]
    bs_ref = black_scholes_put(100, 100, 0.05, 0.20, 1.0)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=steps, y=prices, mode="lines+markers",
        line=dict(color=CYAN, width=2.5),
        marker=dict(size=7, color=CYAN),
        name="Binomial price",
        hovertemplate="N=%{x}<br>Price=$%{y:.4f}<extra></extra>",
    ))
    fig.add_hline(y=bs_ref, line=dict(color=GREEN, dash="dash", width=1.5),
                  annotation_text=f"BS European ${bs_ref:.3f}",
                  annotation_font_color=GREEN)
    fig.update_layout(**chart_layout("Binomial Price Convergence (S0=100, K=100, σ=20%, T=1y)"))
    fig.update_layout(xaxis_title="Steps N", yaxis_title="Put Price ($)")
    return fig, bs_ref


@st.cache_data
def fig_tree():
    N = 3; u = 1.2; d = 1 / 1.2; S0 = 100
    nodes, edges = [], []
    for t in range(N + 1):
        for j in range(t + 1):
            px = t * 2.0; py = (t - 2 * j) * 1.4
            S  = S0 * (u ** (t - j)) * (d ** j)
            pv = max(100 - S, 0)
            early = (t > 0) and (pv > 0) and (t < N)
            nodes.append(dict(px=px, py=py, S=S, pv=pv, early=early, t=t, j=j))
            if t > 0:
                for nj in [j, j - 1]:
                    p = next((n for n in nodes if n["t"] == t - 1 and n["j"] == nj), None)
                    if p:
                        edges.append((p["px"], p["py"], px, py))

    xl, yl = [], []
    for e in edges:
        xl += [e[0], e[2], None]; yl += [e[1], e[3], None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xl, y=yl, mode="lines",
                             line=dict(color="rgba(255,255,255,0.12)", width=1.5),
                             showlegend=False, hoverinfo="skip"))

    for n in nodes:
        fill = c_rgba("#ff4757", 0.25) if n["early"] else c_rgba("#7c3aed", 0.18)
        border = "#ff4757" if n["early"] else "#00d4ff"
        fig.add_shape(type="rect",
                      x0=n["px"] - .62, y0=n["py"] - .52,
                      x1=n["px"] + .62, y1=n["py"] + .52,
                      fillcolor=fill,
                      line=dict(color=border, width=1.5))
        for i, line in enumerate(f"S={n['S']:.0f}\nP={n['pv']:.1f}".split("\n")):
            fig.add_annotation(
                x=n["px"], y=n["py"] + (0.14 if i == 0 else -0.14),
                text=line, showarrow=False,
                font=dict(color="white", size=11, family="Inter"),
            )

    layout = chart_layout("3-Step Binomial Tree (S0=100, K=100)  ·  red = early exercise", h=320)
    layout["xaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.9, 6.5])
    layout["yaxis"] = dict(showgrid=False, zeroline=False, showticklabels=False)
    fig.update_layout(**layout)
    return fig


@st.cache_data
def fig_mc_paths():
    S = simulate_paths(201.80, 0.037, 1.074, 93/365)
    t = np.linspace(0, 93/365, 94)
    fig = go.Figure()
    for i in range(120):
        fig.add_trace(go.Scatter(
            x=t, y=S[i], mode="lines",
            line=dict(color="rgba(0,212,255,0.06)", width=1),
            showlegend=False, hoverinfo="skip",
        ))
    fig.add_hline(y=135, line=dict(color="#ff4757", dash="dot", width=1.8),
                  annotation_text="Strike K=$135", annotation_font_color="#ff4757")
    fig.add_hline(y=201.80, line=dict(color=GOLD, dash="dash", width=1.2),
                  annotation_text="S0=$201.80", annotation_font_color=GOLD)
    fig.update_layout(**chart_layout("GBM Simulation — SPCX (1,000 paths, σ=107%)"))
    fig.update_layout(xaxis_title="Time (years)", yaxis_title="Price ($)")
    return fig, S


@st.cache_data
def fig_dist(S):
    finals = S[:, -1]
    below  = finals[finals < 135]
    above  = finals[finals >= 135]
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=above, nbinsx=40, name="Expire worthless",
                               marker_color="rgba(0,255,136,0.5)"))
    fig.add_trace(go.Histogram(x=below, nbinsx=40, name="In-the-money at expiry",
                               marker_color="rgba(255,71,87,0.7)"))
    fig.add_vline(x=135, line=dict(color="#ff4757", dash="dot", width=2),
                  annotation_text="K=$135", annotation_font_color="#ff4757")
    fig.update_layout(**chart_layout("Terminal Price Distribution", h=300))
    fig.update_layout(xaxis_title="Final Price ($)", yaxis_title="Number of Paths",
                      barmode="overlay",
                      legend=dict(orientation="h", y=1.1, x=0))
    return fig


@st.cache_data
def fig_decomp(am, eu, prem):
    fig = go.Figure(go.Bar(
        x=["European Put\n(Black-Scholes)", "Early Exercise\nPremium", "American Put\n(CRR)"],
        y=[eu, prem, am],
        marker_color=[CYAN, GOLD, GREEN],
        text=[f"${eu:.2f}", f"${prem:.4f}", f"${am:.2f}"],
        textposition="outside", textfont=dict(size=14, color="white"),
        width=0.45,
    ))
    fig.update_layout(**chart_layout("Price Decomposition — SPCX", h=320))
    fig.update_layout(yaxis_title="Price ($)", xaxis=dict(gridcolor="rgba(0,0,0,0)"))
    return fig


# ── pre-compute ───────────────────────────────────────────────────────────────
am_base = binomial_price(100, 100, 0.05, 0.20, 1.0)
eu_base = black_scholes_put(100, 100, 0.05, 0.20, 1.0)

S0_spx = 201.80; K_spx = 135; r_spx = 0.037; T_spx = 93 / 365
sig_iv  = implied_vol(S0_spx, K_spx, r_spx, T_spx, 11.30)
am_spx  = binomial_price(S0_spx, K_spx, r_spx, sig_iv, T_spx)
eu_spx  = black_scholes_put(S0_spx, K_spx, r_spx, sig_iv, T_spx)
prem    = am_spx - eu_spx
lsmc_v  = lsmc_put(S0_spx, K_spx, r_spx, sig_iv, T_spx)


# ════════════════════════════════════════════════════════════════════════════
# PAGE
# ════════════════════════════════════════════════════════════════════════════

# ── COVER ────────────────────────────────────────────────────────────────────
b64 = logo_b64()
logo_html = (f'<img src="data:image/png;base64,{b64}" height="72" '
             f'style="filter:brightness(0) invert(1);opacity:0.8;margin-bottom:18px;">'
             if b64 else "")

st.markdown(f"""
<div class="cover">
  {logo_html}
  <div class="cover-university">Frankfurt University of Applied Sciences &nbsp;·&nbsp; Faculty 3 – Business and Law</div>
  <div class="cover-module">Computer Based Investment Analysis &nbsp;|&nbsp; Summer Semester 2026 &nbsp;|&nbsp; Ferdinand Wöhrle &nbsp;·&nbsp; Dr. Lukas Müller</div>
  <div class="cover-badge">Research Presentation · 2026</div>
  <h1>Pricing of American Options</h1>
  <p class="cover-sub">
    How do you price the right to act early? We implement two numerical methods —
    the Cox-Ross-Rubinstein Binomial Tree and Longstaff-Schwartz LSMC —
    and apply them to a real SpaceX (SPCX) put option.
  </p>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:36px;">
    <span class="chip chip-blue">Binomial Tree (CRR)</span>
    <span class="chip chip-purple">LSMC Monte Carlo</span>
    <span class="chip chip-green">SPCX Case Study</span>
    <span class="chip chip-blue">Implied Volatility</span>
  </div>
  <div class="cover-authors">
    <div style="text-align:center;">
      <div class="cover-author-name">Ilyos Umurzakov</div>
      <div class="cover-author-id">Matriculation No. 1615067</div>
    </div>
    <div style="border-left:1px solid rgba(255,255,255,0.12);"></div>
    <div style="text-align:center;">
      <div class="cover-author-name">Leon Ye</div>
      <div class="cover-author-id">Matriculation No. 1616910</div>
    </div>
    <div style="border-left:1px solid rgba(255,255,255,0.12);"></div>
    <div style="text-align:center;">
      <div class="cover-prof">Lecturers: Ferdinand Wöhrle &nbsp;·&nbsp; Dr. Lukas Müller</div>
      <div class="cover-prof">Submitted: 1 July 2026 · Frankfurt am Main</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for col, (num, lbl) in zip([c1, c2, c3, c4], [
    ("2", "Numerical Methods"),
    (f"{sig_iv*100:.0f}%", "Implied Volatility"),
    (f"${am_spx:.2f}", "American Put (CRR)"),
    (f"${lsmc_v:.2f}", "LSMC Put Price"),
]):
    with col:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{num}</div>'
                    f'<div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── 01 THE CHALLENGE ─────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">01 · The Challenge</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Why American Options Need Numerical Methods</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">European options have a closed-form solution. American options add the right to exercise early — making exact formulas impossible.</div>', unsafe_allow_html=True)

ch1, ch2 = st.columns(2)
with ch1:
    st.markdown("""
    <div class="card">
      <div style="font-size:13px;font-weight:700;color:rgba(255,255,255,0.42);letter-spacing:2px;text-transform:uppercase;margin-bottom:18px;">European Option</div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(255,255,255,0.06);">·</div>
        <div><div class="step-title">Exercise only at expiry T</div>
             <div class="step-desc">No flexibility. You hold until maturity and then decide.</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(255,255,255,0.06);">·</div>
        <div><div class="step-title">Closed-form: Black-Scholes (1973)</div>
             <div class="step-desc">One formula. Exact answer. Fast to compute.</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(255,255,255,0.06);">·</div>
        <div><div class="step-title">Lower bound for American value</div>
             <div class="step-desc">American ≥ European always, because more rights = more value.</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with ch2:
    st.markdown(f"""
    <div class="card" style="border-color:rgba(0,212,255,0.22);">
      <div style="font-size:13px;font-weight:700;color:#00d4ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:18px;">American Option</div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(0,212,255,0.12);color:#00d4ff;">+</div>
        <div><div class="step-title">Exercise at any time 0 &le; t &le; T</div>
             <div class="step-desc">The holder can act at any moment — making the problem path-dependent.</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(0,212,255,0.12);color:#00d4ff;">+</div>
        <div><div class="step-title">No closed-form solution exists</div>
             <div class="step-desc">The optimal exercise boundary cannot be solved analytically. Numerical methods required.</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(0,212,255,0.12);color:#00d4ff;">+</div>
        <div><div class="step-title">Early exercise premium</div>
             <div class="step-desc">Value = European price + premium for the option to act early. This premium is what we are pricing.</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── 02 BINOMIAL TREE ─────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">02 · Method One</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Cox-Ross-Rubinstein Binomial Tree</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Discretise time into N steps. Build a tree of possible prices. Roll backwards comparing hold vs. exercise at every node.</div>', unsafe_allow_html=True)

bt1, bt2 = st.columns([3, 2])
with bt1:
    st.plotly_chart(fig_tree(), use_container_width=True)

with bt2:
    st.markdown(f"""
    <div class="card">
      <div style="font-size:13px;font-weight:700;color:#00d4ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:18px;">How It Works</div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(0,212,255,0.12);color:#00d4ff;font-size:13px;">1</div>
        <div><div class="step-title">Build the price tree</div>
             <div class="step-desc">At each step the stock moves up (× u) or down (× d = 1/u)</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(0,212,255,0.12);color:#00d4ff;font-size:13px;">2</div>
        <div><div class="step-title">Calculate terminal payoffs</div>
             <div class="step-desc">At expiry: max(K &minus; S, 0) for each final node</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(0,212,255,0.12);color:#00d4ff;font-size:13px;">3</div>
        <div><div class="step-title">Roll backwards</div>
             <div class="step-desc">At each node: V = max(hold value, exercise now). Red nodes = early exercise is optimal.</div></div>
      </div>
    </div>
    <div style="margin-top:14px;" class="kpi-row">
      <div class="kpi-box">
        <div class="kpi-num">${am_base:.3f}</div>
        <div class="kpi-lbl">American put N=200</div>
      </div>
      <div class="kpi-box" style="background:rgba(124,58,237,0.09);border-color:rgba(124,58,237,0.22);">
        <div class="kpi-num" style="color:#a78bfa;">${eu_base:.3f}</div>
        <div class="kpi-lbl">European BS benchmark</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

conv_fig, _ = fig_convergence()
st.plotly_chart(conv_fig, use_container_width=True)
st.markdown("""
<div class="info-box">
  <div style="font-size:12px;color:#00d4ff;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Key Insight</div>
  <div style="font-size:14px;color:rgba(255,255,255,0.72);line-height:1.6;">
    As N increases the binomial price oscillates and converges to a value <strong>slightly above</strong>
    the Black-Scholes European price — the early exercise premium.
    Convergence is rapid; N=200 is already stable.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── 03 LSMC ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">03 · Method Two</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Least-Squares Monte Carlo (LSMC)</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Longstaff & Schwartz (2001): simulate thousands of price paths, then use regression to estimate when early exercise is optimal.</div>', unsafe_allow_html=True)

mc1, mc2 = st.columns([3, 2])
mc_fig, S_paths = fig_mc_paths()
with mc1:
    st.plotly_chart(mc_fig, use_container_width=True)

with mc2:
    st.markdown(f"""
    <div class="card">
      <div style="font-size:13px;font-weight:700;color:#a78bfa;letter-spacing:2px;text-transform:uppercase;margin-bottom:18px;">Longstaff-Schwartz (2001)</div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(124,58,237,0.12);color:#a78bfa;font-size:13px;">1</div>
        <div><div class="step-title">Simulate M paths</div>
             <div class="step-desc">Generate price paths under the risk-neutral Q-measure using GBM</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(124,58,237,0.12);color:#a78bfa;font-size:13px;">2</div>
        <div><div class="step-title">Regress continuation value</div>
             <div class="step-desc">At each time step, regress future discounted payoffs on basis functions of S</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(124,58,237,0.12);color:#a78bfa;font-size:13px;">3</div>
        <div><div class="step-title">Exercise when it pays</div>
             <div class="step-desc">If immediate payoff > estimated continuation value, exercise early</div></div>
      </div>
      <div class="step-row">
        <div class="step-dot" style="background:rgba(124,58,237,0.12);color:#a78bfa;font-size:13px;">4</div>
        <div><div class="step-title">Average and discount</div>
             <div class="step-desc">Average discounted payoffs across all paths = price</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.plotly_chart(fig_dist(S_paths), use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── 04 SPACEX CASE STUDY ─────────────────────────────────────────────────────
st.markdown('<div class="section-tag">04 · Case Study</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">SPCX — SpaceX Put Option</div>', unsafe_allow_html=True)
st.markdown(f'<div class="section-sub">SPCX is a publicly traded fund with indirect SpaceX exposure. We price a real put option (K=$135, 93 days, market price $11.30) and extract implied volatility by inverting the binomial model.</div>', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)
for col, num, lbl, color in [
    (k1, "$201.80", "Current Price S0", CYAN),
    (k2, f"{sig_iv*100:.1f}%", "Implied Volatility", GREEN),
    (k3, f"${am_spx:.2f}", "American Put (CRR)", CYAN),
    (k4, f"${lsmc_v:.2f}", "LSMC Put Price", PRP),
]:
    with col:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:{color};">'
                    f'{num}</div><div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

sp1, sp2 = st.columns([2, 3])
with sp1:
    st.markdown(f"""
    <div class="card" style="border-color:rgba(0,255,136,0.2);">
      <div style="font-size:13px;font-weight:700;color:#00ff88;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">Key Findings</div>

      <div style="margin-bottom:16px;">
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">Implied vol = {sig_iv*100:.1f}%</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.56);line-height:1.6;">
          Exceptionally high. Reflects SpaceX's status as a private company with limited price discovery — not historical stock volatility.
        </div>
      </div>

      <div style="margin-bottom:16px;">
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">Early exercise premium = ${prem:.4f}</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.56);line-height:1.6;">
          Essentially zero. The put is deep out of the money (S=$201 vs K=$135), so exercising early almost never makes sense.
        </div>
      </div>

      <div>
        <div style="font-size:15px;font-weight:700;margin-bottom:4px;">CRR and LSMC agree</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.56);line-height:1.6;">
          Both methods converge to the same price, confirming model consistency across completely different mathematical approaches.
        </div>
      </div>

      <div style="margin-top:20px;display:flex;flex-wrap:wrap;gap:6px;">
        <span class="chip chip-blue">K = $135</span>
        <span class="chip chip-purple">T = 93 days</span>
        <span class="chip" style="background:rgba(255,165,2,0.12);border:1px solid rgba(255,165,2,0.3);color:#ffa502;">r = 3.7%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with sp2:
    st.plotly_chart(fig_decomp(am_spx, eu_spx, prem), use_container_width=True)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ── 05 TAKEAWAYS ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">05 · Takeaways</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What We Learned</div>', unsafe_allow_html=True)

st.markdown("""
<div class="reco-box">
  <div class="reco-verdict">Both Methods Work</div>
  <div style="font-size:18px;color:rgba(255,255,255,0.7);max-width:700px;margin:0 auto 32px;line-height:1.65;">
    CRR Binomial Tree and Longstaff-Schwartz LSMC both price the SPCX option consistently.
    The method choice is about speed vs. flexibility — not accuracy.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

ta1, ta2, ta3 = st.columns(3)
for col, color, border, num, title, body in [
    (ta1, "#00d4ff", "rgba(0,212,255,0.22)", "01", "Convergence Validates the Code",
     "As N grows, the binomial price oscillates and stabilises above the Black-Scholes European price. The gap is the early exercise premium — a real, computable number."),
    (ta2, "#ffa502", "rgba(255,165,2,0.22)", "02", "Implied Vol Encodes Information",
     f"A {sig_iv*100:.0f}% implied vol for SPCX is not noise — it is the market's honest estimate of SpaceX uncertainty, priced into a real traded contract."),
    (ta3, "#00ff88", "rgba(0,255,136,0.22)", "03", "Early Exercise Is Rare Here",
     f"Premium = ${prem:.4f}. When a put is this far OTM, holding dominates exercising early. The model finds this automatically — no assumption needed."),
]:
    with col:
        st.markdown(f"""
        <div class="card" style="border-color:{border};height:100%;">
          <div style="font-size:32px;font-weight:900;color:{color};margin-bottom:10px;">{num}</div>
          <div style="font-size:16px;font-weight:700;margin-bottom:8px;">{title}</div>
          <div style="font-size:13px;color:rgba(255,255,255,0.58);line-height:1.65;">{body}</div>
        </div>
        """, unsafe_allow_html=True)

# footer
st.markdown("""
<hr class="divider">
<div style="text-align:center;padding:24px 0;color:rgba(255,255,255,0.28);font-size:12px;">
  Frankfurt University of Applied Sciences &nbsp;·&nbsp; Computer Based Investment Analysis &nbsp;·&nbsp; July 2026<br>
  Ilyos Umurzakov (1615067) &nbsp;&amp;&nbsp; Leon Ye (1616910) &nbsp;·&nbsp; Ferdinand Wöhrle &nbsp;·&nbsp; Dr. Lukas Müller
</div>
""", unsafe_allow_html=True)
