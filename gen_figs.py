# -*- coding: utf-8 -*-
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["savefig.dpi"] = 150

rng = np.random.default_rng(42)

COLOR_A = "#2E5EAA"
COLOR_B = "#D9534F"
COLOR_C = "#4C9A6B"
COLOR_GRID = "#DDDDDD"

def style_ax(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=COLOR_GRID, linewidth=0.6)
    ax.set_axisbelow(True)

# ------------------------------------------------------------------
# 図1: PRISM / 5パラメータ変化点モデル
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)

T = np.linspace(0, 35, 300)

def changepoint(T, Tb_h, Tb_c, base, bh, bc, noise=0.0):
    y = base + bh * np.maximum(Tb_h - T, 0) + bc * np.maximum(T - Tb_c, 0)
    return y + noise

# 世帯A: 断熱良好・バランス温度が低め寄り (暖房側16度, 冷房側26度)
Tb_h_A, Tb_c_A = 16, 26
yA = changepoint(T, Tb_h_A, Tb_c_A, base=8, bh=0.55, bc=0.45)
Tobs = rng.uniform(2, 33, 90)
yobs_A = changepoint(Tobs, Tb_h_A, Tb_c_A, base=8, bh=0.55, bc=0.45, noise=rng.normal(0, 1.1, 90))

# 世帯B: 断熱が弱い・行動特性が違う世帯 (暖房側20度, 冷房側24度)
Tb_h_B, Tb_c_B = 20, 24
yB = changepoint(T, Tb_h_B, Tb_c_B, base=6, bh=0.9, bc=0.7)
yobs_B = changepoint(Tobs, Tb_h_B, Tb_c_B, base=6, bh=0.9, bc=0.7, noise=rng.normal(0, 1.1, 90))

# 「全軒共通」の仮定ライン (18/24度で固定)
y_common_onA = changepoint(T, 18, 24, base=8, bh=0.55, bc=0.45)

for ax, yobs, ycurve, Tb_h, Tb_c, label, color in [
    (axes[0], yobs_A, yA, Tb_h_A, Tb_c_A, "世帯A（断熱良好）", COLOR_A),
    (axes[1], yobs_B, yB, Tb_h_B, Tb_c_B, "世帯B（断熱が弱い）", COLOR_B),
]:
    ax.scatter(Tobs, yobs, s=14, color=color, alpha=0.45, label="実測（日次）")
    ax.plot(T, ycurve, color=color, lw=2.4, label=f"個別推定 Tb={Tb_h}/{Tb_c}℃")
    ax.plot(T, changepoint(T, 18, 24, base=(8 if label=="世帯A（断熱良好）" else 6),
                            bh=(0.55 if label=="世帯A（断熱良好）" else 0.9),
                            bc=(0.45 if label=="世帯A（断熱良好）" else 0.7)),
            color="#888888", lw=1.6, ls="--", label="全軒共通の仮定 (18/24℃)")
    ax.set_title(label, fontsize=11)
    ax.set_xlabel("日平均気温 (℃)")
    style_ax(ax)

axes[0].set_ylabel("日積算電力量 (kWh)")
axes[0].legend(fontsize=8, loc="upper center", frameon=False)
axes[1].legend(fontsize=8, loc="upper center", frameon=False)
fig.suptitle("図1｜PRISM・変化点モデル：世帯ごとにバランス温度 Tb は異なる", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("/home/claude/figs/fig1_changepoint.png")
plt.close(fig)

# ------------------------------------------------------------------
# 図2: 階層モデルによる部分プーリング（縮小推定）
# ------------------------------------------------------------------
n_house = 40
n_days_options = rng.choice([8, 15, 30, 60, 92], size=n_house,
                             p=[0.15, 0.2, 0.25, 0.2, 0.2])
true_b_global = 0.6
true_sd_between = 0.18
true_b = rng.normal(true_b_global, true_sd_between, n_house)

noindep = np.zeros(n_house)
se_indep = np.zeros(n_house)
for i in range(n_house):
    n = n_days_options[i]
    resid_sd = 1.0
    se = resid_sd / np.sqrt(n) / 3.0  # simplistic
    noindep[i] = true_b[i] + rng.normal(0, se * 2.2)
    se_indep[i] = se * 2.2

# 単純なJamesStein型の縮小近似（デモ用。厳密な階層ベイズ推定ではない）
tau2 = np.var(noindep) - np.mean(se_indep**2)
tau2 = max(tau2, 1e-4)
shrink_w = tau2 / (tau2 + se_indep**2)
pooled_mean = np.average(noindep, weights=1/se_indep**2)
b_partial = pooled_mean + shrink_w * (noindep - pooled_mean)

order = np.argsort(n_days_options)
x = np.arange(n_house)

fig, ax = plt.subplots(figsize=(10, 4.6))
ax.errorbar(x - 0.15, noindep[order], yerr=1.96*se_indep[order], fmt="o", ms=4,
            color=COLOR_B, ecolor=COLOR_B, alpha=0.55, elinewidth=1.1, capsize=2,
            label="個別推定（プーリングなし）")
ax.scatter(x + 0.15, b_partial[order], s=22, color=COLOR_A, zorder=5,
           label="部分プーリング推定（階層モデル）")
ax.axhline(pooled_mean, color="#555555", lw=1.3, ls="--", label="全体平均")
ax.axhline(0, color="#999999", lw=0.9)
ax.set_xlabel("世帯（観測日数が少ない順 → 多い順）")
ax.set_ylabel("気温感度係数 b（推定値）")
style_ax(ax)
ax.legend(fontsize=9, frameon=False, loc="lower right")
fig.suptitle("図2｜階層（マルチレベル）モデルによる部分プーリング：\n"
             "データが薄い世帯ほど極端な（時に符号が反転した）b が全体平均へ縮小される", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig("/home/claude/figs/fig2_hierarchical.png")
plt.close(fig)

# ------------------------------------------------------------------
# 図3: 分位点回帰 vs OLS
# ------------------------------------------------------------------
n = 400
Temp = rng.uniform(25, 38, n)
base_load = 3.0 + 0.15 * (Temp - 25)
# 分散が気温とともに拡大する（不均一分散・裾が重い）
noise = rng.gamma(shape=2.0, scale=0.3 + 0.10 * (Temp - 25), size=n)
Peak = base_load + noise

# OLS
A = np.vstack([np.ones(n), Temp]).T
ols_coef, *_ = np.linalg.lstsq(A, Peak, rcond=None)

def quantile_reg_grad(X, y, tau, lr=0.05, iters=3000):
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        resid = y - X @ beta
        grad = -X.T @ (tau - (resid < 0).astype(float)) / len(y)
        beta -= lr * grad
    return beta

Tgrid = np.linspace(25, 38, 100)
Ag = np.vstack([np.ones(100), Tgrid]).T

fig, ax = plt.subplots(figsize=(8.5, 5))
ax.scatter(Temp, Peak, s=14, color="#999999", alpha=0.5, label="日次ピーク需要（世帯合成）")
ax.plot(Tgrid, Ag @ ols_coef, color="#333333", lw=2.2, label="OLS（条件付き平均）")

for tau, color, lbl in [(0.5, COLOR_A, "τ=0.50（中央値）"),
                        (0.9, COLOR_B, "τ=0.90"),
                        (0.97, COLOR_C, "τ=0.97（変圧器設計で重要な裾）")]:
    b = quantile_reg_grad(A, Peak, tau)
    ax.plot(Tgrid, Ag @ b, color=color, lw=2.2, label=f"分位点回帰 {lbl}")

ax.set_xlabel("日平均気温 (℃)")
ax.set_ylabel("日次ピーク需要 (kW)")
style_ax(ax)
ax.legend(fontsize=9, frameon=False, loc="upper left")
fig.suptitle("図3｜分位点回帰：容量計画で意味を持つのは条件付き平均ではなく上側分位点", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("/home/claude/figs/fig3_quantile.png")
plt.close(fig)

# ------------------------------------------------------------------
# 図4: ADMD / 同時率カーブ
# ------------------------------------------------------------------
n_customers = np.arange(1, 101)

def admd_curve(n, admd1, admd_inf, k):
    return admd_inf + (admd1 - admd_inf) * np.exp(-k * (n - 1))

curves = {
    "夏型クラスタ（冷房卓越）": dict(admd1=3.2, admd_inf=1.35, k=0.045, color=COLOR_B),
    "冬型クラスタ（暖房卓越）": dict(admd1=2.6, admd_inf=1.15, k=0.06, color=COLOR_A),
    "フラット/低感応クラスタ": dict(admd1=1.4, admd_inf=0.75, k=0.08, color=COLOR_C),
}

fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))

ax = axes[0]
for label, p in curves.items():
    y = admd_curve(n_customers, p["admd1"], p["admd_inf"], p["k"])
    ax.plot(n_customers, y, color=p["color"], lw=2.2, label=label)
ax.set_xlabel("集約世帯数 n")
ax.set_ylabel("ADMD（1世帯あたり, kW/customer）")
ax.set_title("ADMD カーブ：n が増えるほど分散平準化が進む", fontsize=10.5)
style_ax(ax)
ax.legend(fontsize=8.5, frameon=False)

ax2 = axes[1]
for label, p in curves.items():
    total_individual_max = n_customers * p["admd1"]
    diversified_max = n_customers * admd_curve(n_customers, p["admd1"], p["admd_inf"], p["k"])
    coincidence_factor = diversified_max / total_individual_max
    ax2.plot(n_customers, coincidence_factor, color=p["color"], lw=2.2, label=label)
ax2.set_xlabel("集約世帯数 n")
ax2.set_ylabel("同時率（Coincidence Factor）")
ax2.set_title("同時率：需要率(Demand Factor)の逆数に相当", fontsize=10.5)
style_ax(ax2)
ax2.legend(fontsize=8.5, frameon=False)

fig.suptitle("図4｜クラスタ類型別に見た ADMD と同時率（配電変圧器容量計画の古典概念）", fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig("/home/claude/figs/fig4_admd.png")
plt.close(fig)

# ------------------------------------------------------------------
# 図5: 湿度・不快指数と冷房需要
# ------------------------------------------------------------------
n = 300
Tdb = rng.uniform(26, 35, n)
RH = rng.uniform(40, 90, n)
DI = 0.81 * Tdb + 0.01 * RH * (0.99 * Tdb - 14.3) + 46.3  # 不快指数(近似式)

demand = 2.0 + 0.22 * (Tdb - 26) + 0.05 * (RH - 40) * 0.06 + rng.normal(0, 0.35, n)
# ↑温度だけでなく湿度からも負荷が乗る設定

fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

sc = axes[0].scatter(Tdb, demand, c=RH, cmap="coolwarm", s=22, alpha=0.85)
axes[0].set_xlabel("乾球温度 (℃)")
axes[0].set_ylabel("冷房期 電力需要 (kW)")
axes[0].set_title("乾球温度だけでは同じ気温でもばらつく\n（色 = 相対湿度）", fontsize=10.5)
style_ax(axes[0])
cb = fig.colorbar(sc, ax=axes[0])
cb.set_label("相対湿度 (%)")

axes[1].scatter(DI, demand, color=COLOR_A, s=22, alpha=0.7)
z = np.polyfit(DI, demand, 1)
DIgrid = np.linspace(DI.min(), DI.max(), 50)
axes[1].plot(DIgrid, np.polyval(z, DIgrid), color=COLOR_B, lw=2.2)
corr_T = np.corrcoef(Tdb, demand)[0, 1]
corr_DI = np.corrcoef(DI, demand)[0, 1]
axes[1].set_xlabel("不快指数 DI")
axes[1].set_ylabel("冷房期 電力需要 (kW)")
axes[1].set_title(f"不快指数との相関の方が強くなりやすい\n(相関: 温度 r={corr_T:.2f} → DI r={corr_DI:.2f})",
                   fontsize=10.5)
style_ax(axes[1])

fig.suptitle("図5｜湿度・不快指数を加味すると冷房需要との対応が改善する", fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.88])
fig.savefig("/home/claude/figs/fig5_humidity.png")
plt.close(fig)

# ------------------------------------------------------------------
# 図6: 系列相関と Newey-West HAC 標準誤差
# ------------------------------------------------------------------
n_days = 92
Temp2 = 10 + 10*np.sin(np.linspace(0, 3.1, n_days)) + rng.normal(0, 1.5, n_days)

# AR(1)誤差を持つ残差を作る
phi = 0.65
eps = np.zeros(n_days)
eps[0] = rng.normal(0, 1)
for t in range(1, n_days):
    eps[t] = phi * eps[t-1] + rng.normal(0, 1)

y2 = 5 + 0.4 * Temp2 + eps

X2 = np.vstack([np.ones(n_days), Temp2]).T
beta2, *_ = np.linalg.lstsq(X2, y2, rcond=None)
resid = y2 - X2 @ beta2

# 素朴なOLS標準誤差
sigma2 = np.sum(resid**2) / (n_days - 2)
XtX_inv = np.linalg.inv(X2.T @ X2)
se_ols = np.sqrt(sigma2 * XtX_inv[1, 1])

# Newey-West HAC標準誤差（簡易実装）
def newey_west_se(X, resid, lag):
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    S = np.zeros((k, k))
    for t in range(n):
        S += resid[t]**2 * np.outer(X[t], X[t])
    for L in range(1, lag + 1):
        w = 1 - L / (lag + 1)
        Gamma = np.zeros((k, k))
        for t in range(L, n):
            Gamma += resid[t] * resid[t-L] * np.outer(X[t], X[t-L])
        S += w * (Gamma + Gamma.T)
    cov = XtX_inv @ S @ XtX_inv
    return np.sqrt(np.diag(cov))

lags = [0, 1, 2, 3, 5, 8, 12]
se_hac = []
for L in lags:
    if L == 0:
        se_hac.append(se_ols)
    else:
        se_hac.append(newey_west_se(X2, resid, L)[1])

fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))

axes[0].axhline(0, color="#999999", lw=1)
axes[0].plot(np.arange(n_days), resid, color=COLOR_A, lw=1.4, marker="o", ms=3)
axes[0].set_xlabel("日")
axes[0].set_ylabel("回帰残差")
axes[0].set_title("残差の系列相関：隣接日が似た符号で連続しやすい\n（独立の仮定が崩れている）", fontsize=10.5)
style_ax(axes[0])

axes[1].bar([str(l) if l>0 else "0\n(素朴なOLS)" for l in lags], se_hac, color=COLOR_B, alpha=0.85)
axes[1].set_xlabel("Newey-West ラグ次数")
axes[1].set_ylabel("気温係数の標準誤差 SE(β)")
axes[1].set_title("ラグを考慮すると標準誤差は素朴なOLSより増加する\n（＝有意性を過大評価していた）", fontsize=10.5)
style_ax(axes[1])

fig.suptitle("図6｜系列相関を無視した OLS は標準誤差を過小評価する", fontsize=11.5)
fig.tight_layout(rect=[0, 0, 1, 0.88])
fig.savefig("/home/claude/figs/fig6_neweywest.png")
plt.close(fig)

print("done")
