import streamlit as st

# ------------------ Helpers ------------------
def decimals_count(value_str: str) -> int:
    if "." in value_str:
        return len(value_str.split(".")[1])
    return 0

def format_with_decimals(value: float, decimals: int) -> str:
    fmt = "{:." + str(decimals) + "f}"
    return fmt.format(value)

# ------------------ Defaults ------------------
SL_DISTANCE_DEFAULT = 50.0  # fixed stop distance for ETH (points/$)

# ------------------ Page Setup ------------------
st.set_page_config(page_title="Trade Text Builder – Web", page_icon="📈", layout="centered")
st.title("📈 Trade Text Builder — ETH • Fixed SL 50 • 3×TP")

st.caption("Web version built with Streamlit. Fill in the fields below, then click **Generate Text**.")

# ------------------ Sidebar (Settings) ------------------
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.text_input("Symbol (default ETH)", value="ETH").strip().upper() or "ETH"
risk_pct = st.sidebar.number_input("Risk per trade (%)", min_value=0.0, value=5.0, step=0.1)
leverage = st.sidebar.number_input("Leverage (fixed)", min_value=0.0, value=20.0, step=1.0)
sl_distance = st.sidebar.number_input("Stop distance ($)", min_value=0.0, value=SL_DISTANCE_DEFAULT, step=5.0)

st.sidebar.markdown("---")
st.sidebar.caption("Tip: keep 50 for ETH, as in the desktop version.")

# ------------------ Main Form ------------------
with st.form("trade_form", clear_on_submit=False):
    direction = st.radio("Direction", options=["LONG", "SHORT"], horizontal=True, index=0)
    entry_str = st.text_input("Entry Price (e.g., 3543.5)")

    submit = st.form_submit_button("⚡ Generate Text")

# ------------------ Computation ------------------
if submit:
    # Basic validations
    if not entry_str.strip():
        st.error("Please enter an **entry price**.")
        st.stop()

    try:
        entry = float(entry_str)
        if entry <= 0:
            st.error("**Entry price** must be greater than 0.")
            st.stop()
    except ValueError:
        st.error("Invalid **Entry** format. Use numbers only (e.g., 3543.5).")
        st.stop()

    move_fraction = sl_distance / entry if entry else 0.0
    move_pct = move_fraction * 100.0

    # TP/SL logic (same as original)
    if direction == "LONG":
        sl = entry - sl_distance
        tp1 = entry + 0.5 * sl_distance
        tp2 = entry + 1.0 * sl_distance
        tp3 = entry + 2.0 * sl_distance
    else:  # SHORT
        sl = entry + sl_distance
        tp1 = entry - 0.5 * sl_distance
        tp2 = entry - 1.0 * sl_distance
        tp3 = entry - 2.0 * sl_distance

    # Margin calculation
    if leverage <= 0 or move_fraction == 0:
        margin_pct = 0.0
    else:
        margin_pct = (risk_pct / (move_fraction * leverage))

    # Formatting
    decs = max(decimals_count(entry_str), 0)
    entry_fmt = format_with_decimals(entry, decs)
    sl_fmt    = format_with_decimals(sl, decs)
    tp1_fmt   = format_with_decimals(tp1, decs)
    tp2_fmt   = format_with_decimals(tp2, decs)
    tp3_fmt   = format_with_decimals(tp3, decs)

    # Headline
    headline = (
        f"Entriamo ora a Mercato - {symbol} {direction} {entry_fmt}  -  Margine {margin_pct:.0f}%\n"
        f"🟥SL {sl_fmt}  -  🟩TP1 {tp1_fmt}  •  🟩TP2 {tp2_fmt}  •  🟩TP3 {tp3_fmt}"
    )

    extra_info = (
        f"SL distance: {move_pct:.2f}% (≈{sl_distance:.0f}$) | "
        f"Risk: {risk_pct:.2f}% | Leverage: {leverage:.0f}x"
    )

    # ------------------ Output ------------------
    st.success("Text generated successfully!")

    st.markdown("**Preview (copyable):**")
    st.code(headline, language="markdown")

    st.markdown(f"**Additional info:** {extra_info}")

    # Quick copies for TP/SL/BE updates
    st.markdown("**TP/SL/BE Updates (click Copy to copy):**")
    col_a, col_b = st.columns(2)
    with col_a:
        st.code(f"✅ Take Profit 1 preso a {tp1_fmt}", language="markdown")
        st.code(f"✅ Take Profit 2 preso a {tp2_fmt}", language="markdown")
    with col_b:
        st.code(f"✅ Take Profit 3 preso a {tp3_fmt}", language="markdown")
        st.code(f"❌ Stop Loss preso a {sl_fmt}", language="markdown")

    # Break Even line (separate)
    st.code(f"🟦 Break Even preso a {entry_fmt}", language="markdown")

    # Download text file
    full_txt = headline + "\n\n" + extra_info
    st.download_button(
        label="⬇️ Download as .txt",
        data=full_txt,
        file_name=f"{symbol}_{direction}_{entry_fmt}.txt",
        mime="text/plain",
    )

    st.divider()
    st.caption("You can edit the fields above and click **Generate Text** again to recalculate.")




