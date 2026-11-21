"""Spin by OXXO - Customer value & Flip-Out executive dashboard (Streamlit)."""
import json
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Spin | CLTV & Flip-Out dashboard', page_icon=':credit_card:', layout='wide')
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Spin by OXXO palette: purple, orange, white, light blue. Text colors come from the Streamlit theme
# (.streamlit/config.toml has a light and a dark theme), so everything below works in both modes.
PURPLE, PURPLE_DARK, ORANGE, LIGHT_BLUE = '#6A2BC4', '#4B1A9E', '#FF7A00', '#5EC4F0'
WHITE, GREY = '#FFFFFF', '#9A93A8'
MUTED, GRID = GREY, 'rgba(128,128,128,0.22)'
FONT = dict(family='system-ui, -apple-system, Segoe UI, sans-serif', size=13)
DAYS_PER_MONTH = 30.4375

st.markdown(f"""
<style>
.spin-header {{background: linear-gradient(120deg, {PURPLE_DARK} 0%, {PURPLE} 65%, #8A55E0 100%);
  border-radius: 14px; padding: 20px 26px 16px; margin-bottom: 10px; color: {WHITE};
  border-bottom: 5px solid {ORANGE};}}
.spin-header .brand {{font-weight: 800; font-size: 1rem; letter-spacing: .05em;}}
.spin-header .brand span {{color: {ORANGE};}}
.spin-header .title {{font-size: 1.85rem; font-weight: 700; line-height: 1.2; margin: 4px 0 8px;}}
.spin-header .sub {{font-size: .85rem; opacity: .92;}}
.st-key-kpis_overview div[data-testid="stMetric"], .st-key-kpis_target div[data-testid="stMetric"],
.st-key-kpis_model div[data-testid="stMetric"] {{
  background: rgba(106,43,196,0.08); border-left: 4px solid {PURPLE}; border-radius: 10px; padding: 10px 14px;}}
.stTabs [data-baseweb="tab"] {{font-weight: 600;}}
.tab-card {{border: 1px solid rgba(128,128,128,0.28); border-radius: 10px; padding: 12px 14px;
  height: 100%; margin-bottom: 8px;}}
.tab-card .t {{font-weight: 700; margin-bottom: 4px;}}
.tab-card .d {{font-size: .88rem; opacity: .85;}}
.pgrid {{container-type: inline-size; display: grid; grid-template-columns: 1fr 1fr; gap: 12px 14px; margin: 6px 0 12px;}}
.pgrid .pl {{font-size: .78rem; opacity: .7; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}}
.pgrid .pv {{font-size: 1.2rem; font-size: clamp(.95rem, 8.5cqw, 1.45rem); font-weight: 600; line-height: 1.25;
  white-space: nowrap; font-variant-numeric: tabular-nums;}}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load():
    personas = pd.read_csv(os.path.join(DATA, 'personas.csv'))
    targets = pd.read_csv(os.path.join(DATA, 'target_list.csv'))
    by_persona = pd.read_csv(os.path.join(DATA, 'model_by_persona.csv'))
    drivers = pd.read_csv(os.path.join(DATA, 'drivers.csv'))
    with open(os.path.join(DATA, 'model_card.json')) as f:
        card = json.load(f)
    with open(os.path.join(DATA, 'kpis.json')) as f:
        kpis = json.load(f)
    return personas, targets, by_persona, drivers, card, kpis


personas, targets, by_persona, drivers, card, kpis = load()
COLOR = dict(zip(personas['name'], personas['color']))
ORDER = list(personas['name'])

# ------------------------------------------------------------------ commission assumptions (sliders in Overview)
BASE_OXXO, BASE_OUT = round(kpis['c_oxxo'] * 100, 2), round(kpis['c_out'] * 100, 2)   # 0.5% / 1.0%
c_oxxo = st.session_state.get('c_oxxo_pct', BASE_OXXO) / 100
c_out = st.session_state.get('c_out_pct', BASE_OUT) / 100


def blended(oxxo_share):
    return oxxo_share * c_oxxo + (1 - oxxo_share) * c_out


# CLTV = avg monthly spend x blended commission x lifespan (months), recomputed with the slider commissions
personas['cltv_per_user'] = personas['avg_monthly_spend'] * blended(personas['oxxo_spend_share']) * personas['lifespan_months']
personas['revenue_2025'] = (personas['oxxo_spend_2025'] * c_oxxo
                            + (personas['spend_2025'] - personas['oxxo_spend_2025']) * c_out)
personas['pct_revenue'] = personas['revenue_2025'] / personas['revenue_2025'].sum()
personas['total_cltv'] = personas['cltv_per_user'] * personas['users']
personas['pct_total_cltv'] = personas['total_cltv'] / personas['total_cltv'].sum()
targets['cltv_mxn'] = (targets['avg_monthly_spend'] * blended(targets['oxxo_spend_share'])
                       * targets['account_age_days'] / DAYS_PER_MONTH)
lifespan_all = kpis.get('lifespan_months', kpis['account_age_days'] / DAYS_PER_MONTH)
cltv_user = kpis['avg_monthly_spend'] * blended(kpis['oxxo_spend_share']) * lifespan_all


def style(fig, height=360, legend=True):
    fig.update_layout(height=height, font=FONT, margin=dict(l=10, r=10, t=40, b=10),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=legend,
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0, title=None, traceorder='normal'),
                      hoverlabel=dict(font=FONT))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def money(x, d=0):
    return f'${x:,.{d}f}'


def signed_money(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):,.0f}"


# ------------------------------------------------------------------ header
st.markdown(
    f"<div class='spin-header'><div class='brand'>Spin <span>by OXXO</span></div>"
    f"<div class='title'>Customer Value &amp; Flip-Out Dashboard</div>"
    f"<div class='sub'>{kpis['users']:,} users, monthly data Jan 2025 - Jul 2026. Personas built on 2025 behaviour; "
    f"Flip-Out scores as of 31-May-2026 ({kpis['eligible_users']:,} eligible users). CLTV = avg monthly spend x blended "
    f"commission ({c_oxxo:.2%} OXXO / {c_out:.2%} outside, adjustable in Overview) x lifespan in months. "
    f"Light / dark theme: menu &#8942; (top right).</div></div>",
    unsafe_allow_html=True)

tab_over, tab_pers, tab_target, tab_model = st.tabs(['Overview', 'Personas', 'Target list', 'Model'])

# ------------------------------------------------------------------ OVERVIEW
with tab_over:
    TAB_GUIDE = [
        ('Overview', PURPLE, 'Headline KPIs, how users, revenue and CLTV split across personas, key insights, and '
                             'commission sliders to test how CLTV changes with the OXXO / non-OXXO commission.'),
        ('Personas', ORANGE, 'One card per persona (size, CLTV, spend, OXXO share, account age, profile and Flip-Out '
                             'rate) plus a radar, heatmap or side-by-side view to compare them.'),
        ('Target list', LIGHT_BLUE, 'Users ranked by Flip-Out score. Filter by persona and score decile, set the campaign '
                                    'capacity and see the flip-outs captured by the model vs. random selection; '
                                    'download the contact list.'),
        ('Model', PURPLE_DARK, 'Current Flip-Out model: test metrics (PR-AUC, capture and lift at 10%), top drivers, '
                               'performance by persona and a comparison with the previous model.'),
    ]
    for col, (name, color, desc) in zip(st.columns(4), TAB_GUIDE):
        col.markdown(f"<div class='tab-card' style='border-top:4px solid {color}'>"
                     f"<div class='t'>{name}</div><div class='d'>{desc}</div></div>",
                     unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('**CLTV commission assumptions** (team assumption; Spin does not publish its rates). '
                    'The sliders update CLTV and revenue in every tab.')
        s1, s2 = st.columns(2)
        s1.slider('Commission on OXXO spend', 0.25, 2.0, BASE_OXXO, step=0.05, format='%.2f%%', key='c_oxxo_pct')
        s2.slider('Commission on spend outside OXXO', 0.25, 2.0, BASE_OUT, step=0.05, format='%.2f%%', key='c_out_pct')

    changed = abs(cltv_user - kpis['cltv_per_user']) > 0.005
    c = st.container(key='kpis_overview').columns(5)
    c[0].metric('Users', f"{kpis['users']:,}", help='Unique users in the dataset')
    c[1].metric('OXXO spend share', f"{kpis['oxxo_spend_share']:.1%}",
                help='Share of 2025 spend made at OXXO (estimated as OXXO share of transactions x spend)')
    c[2].metric('Flip-Out rate', f"{kpis['flipout_rate']:.1%}",
                help='Share of eligible users that moved >= 10 pp of their spend outside OXXO in Jun-Jul 2026')
    c[3].metric('Avg monthly spend', money(kpis['avg_monthly_spend']), help='Average 2025 monthly spend per user (MXN)')
    c[4].metric('CLTV per user', money(cltv_user),
                f"{signed_money(cltv_user - kpis['cltv_per_user'])} vs {BASE_OXXO:.1f}% / {BASE_OUT:.1f}%" if changed else None,
                help=f"Commission {c_oxxo:.2%} OXXO / {c_out:.2%} outside; average account age "
                     f"{kpis['account_age_days']:,.0f} days used as lifespan")

    left, right = st.columns([3, 2])
    with left:
        st.subheader('Users by persona vs. where the value is')
        rows = {'Users': 'pct_users', 'Revenue 2025': 'pct_revenue', 'Total CLTV': 'pct_total_cltv'}
        fig = go.Figure()
        for _, p in personas.iterrows():
            fig.add_bar(y=list(rows), x=[p[v] for v in rows.values()], name=p['name'], orientation='h',
                        marker=dict(color=p['color'], line=dict(width=0)),
                        text=[f"{p[v]:.0%}" if p[v] >= 0.05 else '' for v in rows.values()],
                        textposition='inside', insidetextanchor='middle',
                        customdata=[[int(p['users'])]] * 3,
                        hovertemplate=f"<b>{p['name']}</b><br>%{{y}}: %{{x:.1%}}<br>Users: %{{customdata[0]:,}}<extra></extra>")
        fig.update_layout(barmode='stack', bargap=0.35, xaxis=dict(tickformat='.0%', range=[0, 1]), yaxis=dict(autorange='reversed'))
        st.plotly_chart(style(fig, 330), width='stretch')
    with right:
        st.subheader('CLTV per user by persona (MXN)')
        p = personas.sort_values('cltv_per_user')
        fig = go.Figure(go.Bar(x=p['cltv_per_user'], y=p['name'], orientation='h', marker_color=list(p['color']),
                               text=[money(v) for v in p['cltv_per_user']], textposition='outside', cliponaxis=False,
                               hovertemplate='<b>%{y}</b><br>CLTV per user: $%{x:,.0f}<extra></extra>'))
        fig.update_xaxes(range=[0, p['cltv_per_user'].max() * 1.4], tickprefix='$')
        st.plotly_chart(style(fig, 330, legend=False), width='stretch')

    pw = personas.set_index('name')
    top = pw['pct_revenue'].idxmax()
    oxxo = pw['oxxo_spend_share'].idxmax()
    pool = by_persona.sort_values('pct_in_top10', ascending=False).iloc[0]
    st.subheader('Key insights')
    st.markdown(
        f"- **{top}** is {pw.loc[top, 'pct_users']:.0%} of users but **{pw.loc[top, 'pct_revenue']:.0%} of 2025 revenue**; "
        f"its CLTV ({money(pw.loc[top, 'cltv_per_user'])}) is {pw.loc[top, 'cltv_per_user'] / cltv_user:.1f}x the average. Retaining it is priority #1.\n"
        f"- **{oxxo}** spends **{pw.loc[oxxo, 'oxxo_spend_share']:.0%} at OXXO**, where Spin earns {c_oxxo:.2%} vs. "
        f"{c_out:.2%} outside: each peso moved outside OXXO earns {c_out / c_oxxo:.1f}x the commission.\n"
        f"- **{pool['persona']}** concentrates the model's targets: {pool['pct_in_top10']:.0%} of its eligible users are in "
        f"the top 10% of Flip-Out scores (flip-out rate {pool['flipout_rate']:.0%}).\n"
        f"- Account age is similar across personas (~{kpis['account_age_days'] / DAYS_PER_MONTH:.0f} months), so CLTV differences "
        f"come from **spend level and OXXO share**, not tenure.")

# ------------------------------------------------------------------ PERSONAS
with tab_pers:
    st.subheader('Persona cards')
    cols = st.columns(len(personas))
    for col, (_, p) in zip(cols, personas.iterrows()):
        with col.container(border=True):
            st.markdown(f"<div style='height:6px;border-radius:3px;background:{p['color']};margin-bottom:8px'></div>"
                        f"<b style='font-size:1.05rem'>{p['name']}</b>", unsafe_allow_html=True)
            st.caption(f"{int(p['users']):,} users | {p['pct_users']:.1%} of base | {p['pct_revenue']:.1%} of revenue")
            stats = [('CLTV / user', money(p['cltv_per_user'])), ('Monthly spend', money(p['avg_monthly_spend'])),
                     ('OXXO share', f"{p['oxxo_spend_share']:.1%}"), ('Account age', f"{p['account_age_days']:,.0f} d")]
            st.markdown("<div class='pgrid'>" + ''.join(f"<div><div class='pl'>{lab}</div><div class='pv'>{val}</div></div>"
                                                        for lab, val in stats) + "</div>", unsafe_allow_html=True)
            st.markdown(f"**Profile.** {p['profile']}")
            st.markdown(f"**Flip-Out rate:** {p['flipout_rate']:.0%} of {int(p['eligible_users']):,} eligible users")

    st.subheader('Compare personas')
    METRICS = {'cltv_per_user': ('CLTV per user', lambda v: money(v)),
               'avg_monthly_spend': ('Avg monthly spend', lambda v: money(v)),
               'oxxo_spend_share': ('OXXO spend share', lambda v: f'{v:.1%}'),
               'account_age_days': ('Account age (days)', lambda v: f'{v:,.0f}'),
               'tx_per_month': ('Purchases / month', lambda v: f'{v:.1f}'),
               'active_months_pct': ('Active months', lambda v: f'{v:.0%}'),
               'merchant_entropy': ('Merchant diversity', lambda v: f'{v:.2f}'),
               'ecommerce_ratio': ('E-commerce share', lambda v: f'{v:.0%}'),
               'app_onboarded': ('Onboarded in app', lambda v: f'{v:.0%}'),
               'flipout_rate': ('Flip-Out rate', lambda v: f'{v:.0%}')}
    view = st.radio('View', ['Radar', 'Heatmap', 'Side by side'], horizontal=True, label_visibility='collapsed')
    chosen = st.multiselect('Personas to compare', ORDER, default=ORDER)
    sub = personas[personas['name'].isin(chosen)]
    if sub.empty:
        st.warning('Select at least one persona.')
    elif view == 'Radar':
        keys = list(METRICS)
        scale = personas[keys].max()                       # 1 = best persona on that metric
        fig = go.Figure()
        for _, p in sub.iterrows():
            r = (p[keys] / scale).tolist()
            fig.add_scatterpolar(r=r + r[:1], theta=[METRICS[k][0] for k in keys] + [METRICS[keys[0]][0]],
                                 name=p['name'], line=dict(color=p['color'], width=2), fill='toself', opacity=0.55,
                                 customdata=[METRICS[k][1](p[k]) for k in keys] + [METRICS[keys[0]][1](p[keys[0]])],
                                 hovertemplate=f"<b>{p['name']}</b><br>%{{theta}}: %{{customdata}}<extra></extra>")
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0, 1], showticklabels=False, gridcolor=GRID),
                                     angularaxis=dict(gridcolor=GRID)))
        st.plotly_chart(style(fig, 520), width='stretch')
        st.caption('Each axis is scaled to the persona with the highest value (= outer ring). Hover for the real values.')
    elif view == 'Heatmap':
        keys = list(METRICS)
        z = (sub[keys] - personas[keys].mean()) / personas[keys].std()
        txt = [[METRICS[k][1](v) for k, v in zip(keys, row)] for row in sub[keys].values]
        fig = go.Figure(go.Heatmap(z=z.values, x=[METRICS[k][0] for k in keys], y=sub['name'], text=txt,
                                   texttemplate='%{text}', colorscale='RdBu_r', zmid=0, zmin=-1.6, zmax=1.6, colorbar=dict(title='vs. avg<br>persona (z)'),
                                   hovertemplate='<b>%{y}</b><br>%{x}: %{text}<extra></extra>'))
        fig.update_yaxes(autorange='reversed')
        st.plotly_chart(style(fig, 120 + 70 * len(sub), legend=False), width='stretch')
        st.caption('Color = how far each persona is from the average persona (red above, blue below). Text = real value.')
    else:
        table = sub.set_index('name')[list(METRICS)].T
        table = table.apply(lambda col: [METRICS[k][1](v) for k, v in zip(table.index, col)])
        table.index = [METRICS[k][0] for k in METRICS]
        st.dataframe(table, width='stretch')

# ------------------------------------------------------------------ TARGET LIST
with tab_target:
    st.subheader('Who should Marketing contact for a Flip-Out campaign?')
    st.warning('Demo only: the target list is synthetic and must not be used to contact real users.')
    f1, f2, f3 = st.columns([2, 2, 2])
    sel_p = f1.multiselect('Persona', ORDER, default=ORDER)
    sel_d = f2.multiselect('Score decile (1 = highest scores)', list(range(1, 11)), default=list(range(1, 11)))
    cap = f3.slider('Campaign capacity (% of the filtered users contacted)', 5, 30, 10, step=1, format='%d%%')

    pool = targets[targets['persona'].isin(sel_p) & targets['score_decile'].isin(sel_d)].sort_values('rank')
    if pool.empty:
        st.warning('No users match the filters.')
    else:
        n = len(pool)
        k = max(1, int(np.ceil(cap / 100 * n)))
        contact = pool.head(k)
        events = pool['actual_flip_out'].sum()
        captured = int(contact['actual_flip_out'].sum())
        random_hits = events * k / n
        cltv_model = contact.loc[contact['actual_flip_out'] == 1, 'cltv_mxn'].sum()
        cltv_random = pool.loc[pool['actual_flip_out'] == 1, 'cltv_mxn'].sum() * k / n

        m = st.container(key='kpis_target').columns(5)
        m[0].metric('Users to contact', f'{k:,}', help=f'{cap}% of {n:,} filtered users')
        m[1].metric('Flip-outs captured (model)', f'{captured:,}', f'{captured - random_hits:+,.0f} vs random')
        m[2].metric('Flip-outs captured (random)', f'{random_hits:,.0f}')
        m[3].metric('Lift vs random', f'{captured / random_hits:.2f}x' if random_hits else '-',
                    help='Flip-outs captured by the model / flip-outs a random selection of the same size would capture')
        m[4].metric('CLTV of captured flip-outs', money(cltv_model), f'{signed_money(cltv_model - cltv_random)} vs random')

        left, right = st.columns([3, 2])
        with left:
            st.markdown('**Cumulative flip-outs captured** (backtest Jun-Jul 2026)')
            y = pool['actual_flip_out'].values
            x = np.arange(1, n + 1) / n
            cum = np.cumsum(y) / max(y.sum(), 1)
            step = max(1, n // 400)
            fig = go.Figure()
            fig.add_scatter(x=[0, 1], y=[0, 1], name='Random selection', mode='lines',
                            line=dict(color=GREY, dash='dash', width=2), hoverinfo='skip')
            fig.add_scatter(x=np.r_[0, x[::step]], y=np.r_[0, cum[::step]], name='Flip-Out model', mode='lines',
                            line=dict(color=PURPLE, width=2.5),
                            hovertemplate='Contact top %{x:.0%}<br>Capture %{y:.0%} of flip-outs<extra></extra>')
            fig.add_vline(x=k / n, line=dict(color=ORANGE, width=1.5, dash='dot'))
            fig.add_scatter(x=[k / n], y=[captured / max(events, 1)], mode='markers+text', showlegend=False,
                            marker=dict(size=11, color=ORANGE, line=dict(color=WHITE, width=2)),
                            text=[f'  {captured / max(events, 1):.0%} captured at {cap}%'], textposition='middle right',
                            hoverinfo='skip')
            fig.update_layout(xaxis=dict(title='% of filtered users contacted (by score)', tickformat='.0%', range=[0, 1]),
                              yaxis=dict(title='% of flip-outs captured', tickformat='.0%', range=[0, 1.02]))
            st.plotly_chart(style(fig, 400), width='stretch')
        with right:
            st.markdown(f'**Distribution of the Flip-Out score** (top {cap}% contacted)')
            HIST_BLUE, HIST_ORANGE, HIST_INK = '#2a78d6', '#dd8452', '#52514e'   # original colors (same as Figure F8a)
            cutoff = contact['flipout_score'].min()                  # score of the last user inside the top cap%
            bins = np.linspace(0, 1, 41)                             # 40 bins of width 0.025
            centers = (bins[:-1] + bins[1:]) / 2
            in_list = pool.index.isin(contact.index)
            h_out, _ = np.histogram(pool.loc[~in_list, 'flipout_score'], bins=bins)
            h_in, _ = np.histogram(pool.loc[in_list, 'flipout_score'], bins=bins)

            fig = go.Figure()
            fig.add_bar(x=centers, y=h_out, width=0.025, marker_color=HIST_BLUE,
                        name=f'Not contacted ({100 - cap}%, {n - k:,} users)',
                        hovertemplate='Score ≈ %{x:.2f}<br>%{y:,} users<extra>Not contacted</extra>')
            fig.add_bar(x=centers, y=h_in, width=0.025, marker_color=HIST_ORANGE,
                        name=f'Contacted - top {cap}% ({k:,} users)',
                        hovertemplate='Score ≈ %{x:.2f}<br>%{y:,} users<extra>Contacted</extra>')
            fig.add_vline(x=cutoff, line=dict(color=HIST_INK, width=1.5, dash='dash'),
                          annotation_text=f'Top {cap}% cut-off = {cutoff:.3f}<br>{k:,} users contacted',
                          annotation_position='top right', annotation_font=dict(color=HIST_INK, size=11))
            fig.update_traces(marker_line=dict(color='white', width=0.5))
            fig.update_layout(barmode='stack', bargap=0,
                              xaxis=dict(title='Predicted Flip-Out score', range=[0, 1]),
                              yaxis_title='Number of users')
            st.plotly_chart(style(fig, 400), width='stretch')

        st.markdown(f'**Contact list - top {k:,} users by Flip-Out score**')
        show = contact[['rank', 'userId', 'persona', 'flipout_score', 'score_decile', 'avg_monthly_spend',
                        'oxxo_spend_share', 'account_age_days', 'cltv_mxn', 'actual_flip_out']].copy()
        show['oxxo_spend_share'] *= 100
        st.dataframe(show, hide_index=True, width='stretch', height=380, column_config={
            'rank': st.column_config.NumberColumn('Rank'),
            'userId': 'User',
            'persona': 'Persona',
            'flipout_score': st.column_config.ProgressColumn('Flip-Out score', min_value=0, max_value=1, format='%.2f'),
            'score_decile': st.column_config.NumberColumn('Decile'),
            'avg_monthly_spend': st.column_config.NumberColumn('Avg monthly spend', format='$%.0f'),
            'oxxo_spend_share': st.column_config.NumberColumn('OXXO share', format='%.0f%%'),
            'account_age_days': st.column_config.NumberColumn('Account age (d)', format='%d'),
            'cltv_mxn': st.column_config.NumberColumn('CLTV (MXN)', format='$%.0f'),
            'actual_flip_out': st.column_config.CheckboxColumn('Flipped out (backtest)')})
        st.download_button('Download contact list (CSV)', contact.to_csv(index=False).encode('utf-8'),
                           file_name=f'spin_flipout_targets_top{cap}pct.csv', mime='text/csv')
        st.caption('Scores as of 31-May-2026. "Flipped out" is the real outcome in Jun-Jul 2026 (out-of-time backtest), '
                   'used to compare the model with a random selection of the same size. Deciles are computed on all '
                   f"{len(targets):,} eligible users; capacity is applied to the filtered users. "
                   f"CLTV uses the commission set in Overview ({c_oxxo:.2%} OXXO / {c_out:.2%} outside).")

# ------------------------------------------------------------------ MODEL
with tab_model:
    cur, prev = card['current'], card['previous']
    st.subheader(f"Current model: {card['version']}")
    st.markdown(f"**{card['name']}**  \n{card['target']}")
    m = st.container(key='kpis_model').columns(4)
    m[0].metric('PR-AUC (test)', f"{cur['pr_auc']:.3f}", f"{cur['pr_auc'] - card['base_rate']:+.3f} vs random ({card['base_rate']:.3f})")
    m[1].metric('Capture at 10%', f"{cur['capture_top10']:.1%}", f"{cur['capture_top10'] - 0.10:+.1%} vs random (10%)",
                help='Share of all flip-outs found by contacting the 10% of users with the highest scores')
    m[2].metric('Lift at 10%', f"{cur['lift_top10']:.2f}x", help='Precision in the top 10% / flip-out rate')
    m[3].metric('ROC-AUC (test)', f"{cur['roc_auc']:.3f}")
    with st.expander('Training and test setup'):
        st.markdown(f"- **Train:** {card['train']}\n- **Test:** {card['test']}\n- **Hyper-parameters:** {card['params']}"
                    f"\n- **CV PR-AUC (T1):** {card['cv_pr_auc']:.3f}")

    left, right = st.columns([3, 2])
    with left:
        st.markdown('**Top drivers** (mean |SHAP| of the gradient boosting model)')
        d = drivers.sort_values('mean_abs_shap').tail(8)
        fig = go.Figure(go.Bar(x=d['mean_abs_shap'], y=d['driver'], orientation='h', marker_color=PURPLE,
                               customdata=d['direction'],
                               hovertemplate='<b>%{y}</b><br>Mean |SHAP|: %{x:.3f}<br>%{customdata}<extra></extra>'))
        fig.update_xaxes(title='Average impact on the Flip-Out score')
        st.plotly_chart(style(fig, 380, legend=False), width='stretch')
    with right:
        st.markdown('**How to read the drivers**')
        for _, r in drivers.head(5).iterrows():
            arrow = 'raises' if r['lr_coefficient'] > 0 else 'lowers'
            st.markdown(f"- **{r['driver']}**: a higher value {arrow} the chance of a flip-out")
        st.caption('Direction taken from the standardized logistic regression coefficients.')
        st.success('**Takeaway:** flip-outs come from users who buy rarely and still lean on OXXO. Low-frequency, '
                   'OXXO-heavy users are the best campaign targets; frequent, diversified users have little room to flip.')

    st.markdown('**Performance by persona** (global top-10% threshold)')
    bp = by_persona.drop(columns='persona_id').rename(columns={
        'persona': 'Persona', 'eligible_users': 'Eligible users', 'flipout_rate': 'Flip-Out rate', 'avg_score': 'Avg score',
        'pct_in_top10': '% in top 10%', 'capture_top10': 'Capture at 10%', 'pr_auc': 'PR-AUC'})
    st.dataframe(bp.style.format({'Eligible users': '{:,}', 'Flip-Out rate': '{:.1%}', 'Avg score': '{:.3f}',
                                  '% in top 10%': '{:.1%}', 'Capture at 10%': '{:.1%}', 'PR-AUC': '{:.3f}'}),
                 hide_index=True, width='stretch')

    st.subheader('Model comparison')
    comp = pd.DataFrame({
        'Version': [f"{card['previous_version']} - {card['previous_name']}", f"{card['version']} - {card['name']}",
                    'Random selection'],
        'PR-AUC': [prev['pr_auc'], cur['pr_auc'], card['base_rate']],
        'ROC-AUC': [prev['roc_auc'], cur['roc_auc'], 0.5],
        'Capture at 10%': [prev['capture_top10'], cur['capture_top10'], 0.10],
        'Lift at 10%': [prev['lift_top10'], cur['lift_top10'], 1.0]})
    st.dataframe(comp.style.format({'PR-AUC': '{:.3f}', 'ROC-AUC': '{:.3f}', 'Capture at 10%': '{:.1%}', 'Lift at 10%': '{:.2f}x'}),
                 hide_index=True, width='stretch')
    st.markdown('\n'.join(f'- {c}' for c in card['changes']))
