"""
app.py — Interactive FRED Time Series Decomposition Dashboard

Launch with: streamlit run app.py

Requires: streamlit, plotly, fredapi, statsmodels, ruptures, pandas, numpy
Set your FRED API key as an environment variable:
    export FRED_API_KEY="your_key_here"
Or enter it directly in the sidebar.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fredapi import Fred
from decompose import (
    run_stl,
    run_mstl,
    test_stationarity,
    detect_breaks,
    block_bootstrap_trend,
)

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="FRED Decomposition Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 FRED Time Series Decomposition Dashboard")
st.caption(
    "Explore STL, MSTL, stationarity tests, structural breaks, "
    "and bootstrap trend confidence intervals for any FRED series."
)

# =============================================================================
# SIDEBAR — INPUTS
# =============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "FRED API Key",
        value=os.environ.get("FRED_API_KEY", ""),
        type="password",
        help="Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html",
    )

    series_id = st.text_input(
        "FRED Series ID",
        value="RSXFSN",
        help="Examples: RSXFSN (retail), GDPC1 (real GDP), INDPRO (industrial production)",
    ).upper()

    start_date = st.date_input("Start Date", value=pd.Timestamp("2000-01-01"))

    st.divider()
    st.subheader("Decomposition Method")
    method = st.radio("Method", ["STL", "MSTL", "Classical"])

    log_transform = st.checkbox("Log-transform (multiplicative data)", value=True)

    st.divider()
    st.subheader("STL / MSTL Parameters")

    if method == "MSTL":
        periods_input = st.text_input(
            "Seasonal periods (comma-separated)",
            value="12,3",
            help="e.g. '7,365' for daily data with weekly + annual cycles",
        )
        try:
            periods = [int(p.strip()) for p in periods_input.split(",")]
        except ValueError:
            st.error("Periods must be integers, e.g. '12,3'")
            periods = [12]
    else:
        period = st.slider("Seasonal Period", min_value=2, max_value=52, value=12)

    robust = st.checkbox("Robust fitting (downweights outliers)", value=True)

    st.divider()
    st.subheader("Structural Breaks (PELT)")
    pen = st.slider(
        "Penalty",
        min_value=1.0,
        max_value=50.0,
        value=10.0,
        step=0.5,
        help=(
            "Higher penalty → fewer breaks detected. "
            "This is the bias-variance tradeoff: low penalty overfits noise; "
            "high penalty misses real structural changes."
        ),
    )

    st.divider()
    st.subheader("Block Bootstrap CI")
    run_bootstrap = st.checkbox("Run block bootstrap (slow)", value=False)
    n_bootstrap = st.slider("Bootstrap replications", 100, 1000, 300, step=100)
    block_size = st.slider(
        "Block size",
        min_value=3,
        max_value=36,
        value=12,
        help=(
            "Blocks preserve autocorrelation. "
            "i.i.d. resampling would destroy temporal dependence, "
            "producing artificially narrow CIs."
        ),
    )

    run_btn = st.button("▶ Run Analysis", type="primary", use_container_width=True)

# =============================================================================
# HELPERS
# =============================================================================

FREQ_TO_PERIOD = {"MS": 12, "QS": 4, "Q": 4, "A": 1, "AS": 1, "W": 52, "D": 365}


def detect_freq_period(series: pd.Series) -> int:
    """Infer a sensible default seasonal period from the series frequency."""
    freq = pd.infer_freq(series.index)
    if freq is None:
        return 12
    for key, val in FREQ_TO_PERIOD.items():
        if freq.startswith(key):
            return val
    return 12


@st.cache_data(show_spinner=False)
def fetch_series(api_key: str, series_id: str, start: str) -> pd.Series:
    fred = Fred(api_key=api_key)
    s = fred.get_series(series_id, observation_start=start)
    s = s.dropna()
    s.index = pd.DatetimeIndex(s.index)
    s = s.resample(pd.infer_freq(s.index) or "MS").last()
    return s


def make_decomp_figure(components: dict, break_dates: list, title: str) -> go.Figure:
    """Build a 4-panel plotly figure for decomposition components."""
    panels = list(components.items())
    fig = make_subplots(
        rows=len(panels), cols=1,
        shared_xaxes=True,
        subplot_titles=[p[0] for p in panels],
        vertical_spacing=0.06,
    )
    colors = ["#2c3e50", "#e67e22", "#27ae60", "#c0392b", "#8e44ad", "#2980b9"]

    for i, (name, series) in enumerate(panels, 1):
        fig.add_trace(
            go.Scatter(
                x=series.index, y=series.values,
                mode="lines",
                line=dict(color=colors[(i - 1) % len(colors)], width=0.9),
                name=name,
            ),
            row=i, col=1,
        )
        if name == "Residual":
            fig.add_hline(y=0, line_dash="dash", line_color="gray",
                          line_width=0.7, row=i, col=1)

    # Overlay structural breaks on the observed panel
    for bd in break_dates:
        fig.add_vline(
            x=bd, line_dash="dot", line_color="red",
            line_width=1.2, opacity=0.7,
        )

    fig.update_layout(
        title=title,
        height=160 * len(panels),
        showlegend=False,
        margin=dict(t=60, b=20),
        template="plotly_white",
    )
    return fig


def stationarity_table(result: dict) -> pd.DataFrame:
    verdict_colors = {
        "stationary": "🟢 Stationary",
        "non-stationary": "🔴 Non-stationary",
        "contradictory": "🟡 Contradictory",
        "inconclusive": "⚪ Inconclusive",
    }
    rows = [
        ["ADF statistic", f"{result['adf_stat']:.4f}"],
        ["ADF p-value", f"{result['adf_p']:.4f}"],
        ["KPSS statistic", f"{result['kpss_stat']:.4f}"],
        ["KPSS p-value", f"{result['kpss_p']:.4f}"],
        ["Verdict", verdict_colors.get(result["verdict"], result["verdict"])],
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

if not run_btn:
    st.info("Configure parameters in the sidebar and click **▶ Run Analysis**.")
    st.stop()

if not api_key:
    st.error("Please enter a FRED API key in the sidebar.")
    st.stop()

# --- Fetch data ---
with st.spinner(f"Fetching {series_id} from FRED..."):
    try:
        series = fetch_series(api_key, series_id, str(start_date))
    except Exception as e:
        st.error(f"Failed to fetch series: {e}")
        st.stop()

st.success(f"Loaded **{series_id}**: {len(series)} observations "
           f"({series.index[0].date()} → {series.index[-1].date()})")

# Auto-detect period if STL and user hasn't changed it
if method != "MSTL":
    auto_period = detect_freq_period(series)
    if period != auto_period:
        st.info(f"Detected frequency period: **{auto_period}**. "
                f"You selected {period} — adjust in the sidebar if needed.")

# =============================================================================
# DECOMPOSITION
# =============================================================================

with st.spinner("Running decomposition..."):
    try:
        if method == "STL":
            result = run_stl(series, period=period,
                             log_transform=log_transform, robust=robust)
            components = {
                "Observed": result.observed,
                "Trend": result.trend,
                "Seasonal": result.seasonal,
                "Residual": result.resid,
            }
            decomp_title = f"STL Decomposition — {series_id} (period={period})"

        elif method == "MSTL":
            result = run_mstl(series, periods=periods,
                              log_transform=log_transform, robust=robust)
            components = {"Observed": result.observed, "Trend": result.trend}
            seasonal_df = result.seasonal
            if isinstance(seasonal_df, pd.DataFrame):
                for col in seasonal_df.columns:
                    components[f"Seasonal ({col})"] = seasonal_df[col]
            else:
                components["Seasonal"] = seasonal_df
            components["Residual"] = result.resid
            decomp_title = (f"MSTL Decomposition — {series_id} "
                            f"(periods={periods})")

        else:  # Classical — use STL with default period as proxy
            from statsmodels.tsa.seasonal import seasonal_decompose
            work = np.log(series) if log_transform else series
            result = seasonal_decompose(work, model="additive",
                                        period=period, extrapolate_trend="freq")
            components = {
                "Observed": result.observed,
                "Trend": result.trend.dropna(),
                "Seasonal": result.seasonal,
                "Residual": result.resid.dropna(),
            }
            decomp_title = (f"Classical Decomposition — {series_id} "
                            f"(period={period})")

    except ValueError as e:
        st.error(f"Decomposition error: {e}")
        st.stop()

# --- Structural breaks on the observed series ---
with st.spinner("Detecting structural breaks..."):
    work_for_breaks = np.log(series) if log_transform else series
    break_dates = detect_breaks(work_for_breaks, pen=pen)

# --- Plot decomposition ---
st.plotly_chart(
    make_decomp_figure(components, break_dates, decomp_title),
    use_container_width=True,
)

if break_dates:
    st.caption(
        f"🔴 **{len(break_dates)} structural break(s) detected** "
        f"(penalty={pen}): " +
        ", ".join(str(d.date()) for d in break_dates)
    )
else:
    st.caption(f"No structural breaks detected at penalty={pen}.")

# =============================================================================
# STATIONARITY TESTS
# =============================================================================

st.subheader("🔬 Stationarity Tests")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Levels**")
    with st.spinner("Running ADF + KPSS on levels..."):
        stat_levels = test_stationarity(work_for_breaks)
    st.dataframe(stationarity_table(stat_levels), hide_index=True, use_container_width=True)

with col2:
    st.markdown("**First Differences**")
    with st.spinner("Running ADF + KPSS on first differences..."):
        diff_series = work_for_breaks.diff().dropna()
        stat_diff = test_stationarity(diff_series)
    st.dataframe(stationarity_table(stat_diff), hide_index=True, use_container_width=True)

with st.expander("📖 How to read these results"):
    st.markdown("""
    | ADF rejects H₀ | KPSS rejects H₀ | Conclusion |
    |---|---|---|
    | ✅ Yes | ❌ No | 🟢 **Stationary** |
    | ❌ No | ✅ Yes | 🔴 **Non-stationary** (unit root) |
    | ✅ Yes | ✅ Yes | 🟡 **Contradictory** — possible structural break |
    | ❌ No | ❌ No | ⚪ **Inconclusive** — tests have low power |

    **ADF** (H₀: unit root present) uses `regression='ct'` (constant + trend) —
    correct for trended macro series. Using `regression='n'` would inflate the
    test statistic and potentially give a false rejection.

    **KPSS** (H₀: series is stationary) complements ADF because the two tests
    have opposite null hypotheses, making their agreement more informative.
    """)

# =============================================================================
# SEASONAL AMPLITUDE DIAGNOSTICS
# =============================================================================

if method in ("STL", "MSTL") and "Seasonal" in components:
    st.subheader("📊 Seasonal Amplitude Stability")
    seasonal = components["Seasonal"]
    by_year = seasonal.groupby(seasonal.index.year)
    counts = by_year.count()
    full_years = counts[counts == 12].index
    amp = by_year.apply(lambda x: x.max() - x.min())
    amp_full = amp[amp.index.isin(full_years)]

    fig_amp = go.Figure(go.Bar(
        x=amp_full.index.astype(str), y=amp_full.values,
        marker_color="#27ae60", name="Annual amplitude"
    ))
    fig_amp.update_layout(
        title="Seasonal Amplitude by Year (should be ~constant for additive STL)",
        xaxis_title="Year", yaxis_title="Amplitude",
        template="plotly_white", height=300,
    )
    st.plotly_chart(fig_amp, use_container_width=True)

    if len(amp_full) >= 2:
        ratio = amp_full.iloc[-1] / amp_full.iloc[0]
        if 0.7 <= ratio <= 1.3:
            st.success(f"✅ Amplitude ratio (last/first full year): **{ratio:.2f}x** — "
                       "additive assumption holds.")
        else:
            st.warning(f"⚠️ Amplitude ratio: **{ratio:.2f}x** — consider toggling "
                       "log-transform or switching method.")

# =============================================================================
# BLOCK BOOTSTRAP TREND CI
# =============================================================================

if run_bootstrap and method == "STL":
    st.subheader("🎲 Block Bootstrap Trend Confidence Interval")

    with st.spinner(f"Running {n_bootstrap} bootstrap replications "
                    f"(block size={block_size})..."):
        ci_df = block_bootstrap_trend(
            series,
            n_bootstrap=n_bootstrap,
            block_size=block_size,
            period=period,
            log_transform=log_transform,
            robust=robust,
        )

    fig_ci = go.Figure()
    fig_ci.add_trace(go.Scatter(
        x=ci_df.index, y=ci_df["upper"],
        mode="lines", line=dict(width=0), showlegend=False,
    ))
    fig_ci.add_trace(go.Scatter(
        x=ci_df.index, y=ci_df["lower"],
        mode="lines", fill="tonexty",
        fillcolor="rgba(41,128,185,0.2)",
        line=dict(width=0), name="95% CI",
    ))
    fig_ci.add_trace(go.Scatter(
        x=ci_df.index, y=ci_df["median"],
        mode="lines", line=dict(color="#2980b9", width=1.5),
        name="Bootstrap median trend",
    ))
    fig_ci.add_trace(go.Scatter(
        x=result.trend.index, y=result.trend.values,
        mode="lines", line=dict(color="#e67e22", width=1.2, dash="dash"),
        name="Original STL trend",
    ))
    fig_ci.update_layout(
        title=f"Block Bootstrap Trend CI ({n_bootstrap} reps, block={block_size})",
        template="plotly_white", height=380,
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig_ci, use_container_width=True)

    with st.expander("📖 Why block bootstrap, not i.i.d. bootstrap?"):
        st.markdown("""
        **i.i.d. bootstrap** randomly resamples individual observations.
        This destroys temporal autocorrelation — the synthetic series has no
        memory, which is statistically impossible for an economic time series.
        The resulting confidence intervals are **too narrow**.

        **Block bootstrap** resamples contiguous blocks (length = `block_size`).
        Within each block, the original autocorrelation structure is preserved.
        Concatenating random blocks produces synthetic series that plausibly
        could have been generated by the same process as the original data.

        Rule of thumb: `block_size ≈ seasonal period` (12 for monthly data),
        or `block_size ≈ n^(1/3)` for a more data-driven choice.
        """)

elif run_bootstrap and method != "STL":
    st.info("Block bootstrap is currently implemented for STL only.")

# =============================================================================
# RAW DATA
# =============================================================================

with st.expander("🗂️ Raw series data"):
    st.dataframe(
        series.rename("value").to_frame().tail(60),
        use_container_width=True,
    )

# =============================================================================
# SENSITIVITY EXPLAINER
# =============================================================================

with st.expander("🔍 What does this app reveal about parameter sensitivity?"):
    st.markdown("""
    ### Decomposition Sensitivity to Parameter Choices

    **1. Period (`period` slider)**
    Setting the wrong period misattributes variance. A monthly series run
    with `period=4` will fold three months of seasonal signal into the
    residual, producing a noisier residual and a trend that absorbs seasonal
    variation. The amplitude stability chart immediately reveals this.

    **2. Log-transform toggle**
    For multiplicative series (retail, GDP), skipping the log transform
    produces a seasonal component whose amplitude grows over time — violating
    STL's additive assumption. The amplitude bar chart will show a ratio >> 1.
    Turning on the log transform collapses seasonal swings to a stable band.

    **3. Robust fitting**
    The 2020 COVID shock is a single large outlier. Without `robust=True`,
    that outlier contaminates the trend and seasonal estimates around it.
    With robust fitting, it's correctly isolated into the residual.

    **4. Break penalty**
    Drag the penalty slider from 2 to 40 on GDPC1. At low penalties, every
    recession trough triggers a false break. At high penalties, the 2008
    crisis and 2020 COVID shock — genuine structural shifts — are missed.
    The right penalty is data-dependent; there's no universal answer.

    **5. STL vs MSTL**
    For monthly data with a single annual cycle, STL and MSTL (periods=[12])
    produce identical results. Switch to hourly electricity data and add
    `periods=[24, 168]` (daily + weekly) — STL with a single period will
    conflate the two cycles into one noisy seasonal component, while MSTL
    separates them cleanly.
    """)
