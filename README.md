# 変圧器容量計画のための統計モデリング・トピック集

スマートメーターによる需要データのクラスタリングと、配電用変圧器の容量計画を対象に、
関連する統計モデリング手法を **6つの論点** に整理した解説ノートです。各手法について
「考え方 → 数式 → 図解 → 現行分析パイプラインへの接続点」をまとめています。

👉 **[ノートを開く（GitHub Pages）](https://hrtkhr3-lab.github.io/transformer-capacity-notes/)** — クリックすると全文をブラウザで閲覧できます。

（ソースを見る場合は [index.html](index.html)）

---

## 収録トピック

| # | トピック | 要点 |
|---|---------|------|
| 01 | **PRISM と変化点モデル** | 世帯ごとにバランス温度 Tb を推定する5パラメータ変化点モデル（Fels 1986 / ASHRAE Guideline 14） |
| 02 | **階層モデル／部分プーリング** | 観測日数の少ない世帯の不安定な係数を全体平均へ縮小推定（shrinkage）する |
| 03 | **分位点回帰** | 条件付き平均（OLS）ではなく上側分位点を直接モデル化し、「厳しい日」の需要を捉える |
| 04 | **ADMD と同時率** | After Diversity Maximum Demand。集約世帯数による需要平準化をクラスタ類型別に定量化 |
| 05 | **冷房需要と湿度・不快指数** | 乾球温度に加え相対湿度・不快指数（DI）を特徴量化し、夏型負荷の説明力を上げる |
| 06 | **系列相関と Newey-West 標準誤差** | 日次残差の自己相関を考慮した HAC 標準誤差で、係数の有意性の過大評価を防ぐ |

末尾には、6論点を `01→02→03→04` と `05` `06` の流れで統合する「まとめ」を収録しています。

---

## リポジトリ構成

```
transformer-capacity-notes/
├── index.html        # 解説ノート本体（figs/ の画像を参照）
├── gen_figs.py       # 図1〜6を生成する matplotlib スクリプト
├── figs/             # 生成済みの図（PNG）
│   ├── fig1_changepoint.png
│   ├── fig2_hierarchical.png
│   ├── fig3_quantile.png
│   ├── fig4_admd.png
│   ├── fig5_humidity.png
│   └── fig6_neweywest.png
└── README.md
```

> **Note** — `index.html` は `figs/*.png` を相対パスで参照するため、`index.html` と `figs/`
> ディレクトリは同じ場所に置いてください。画像を1ファイルに埋め込んだ自己完結版（配布・
> 共有向け）が別途必要な場合は、各 PNG を data URI 化して差し込む方法があります。

---

## 図の再生成

図はすべて **模擬データ（乱数シード固定）による手法の直感の例示** であり、実データの分析
結果ではありません。再生成するには次の環境が必要です。

### 必要なもの

- Python 3.8+
- `numpy`, `matplotlib`
- 日本語フォント **Noto Sans CJK JP**（未インストールだと日本語ラベルが豆腐□になります）

```bash
pip install numpy matplotlib
```

### 実行

```bash
python gen_figs.py
```

> ⚠️ **保存先パスについて** — 現状 `gen_figs.py` は保存先を
> `/home/claude/figs/...` にハードコードしています（生成時の環境の名残）。
> 手元で実行する場合は、スクリプト内の `fig.savefig("/home/claude/figs/...")` を
> `fig.savefig("figs/...")` などローカルの相対パスに書き換えてから実行してください。
> `figs/` ディレクトリが無ければ事前に作成が必要です。

---

## 出典・キーワード

各手法の一次資料・検索キーワードは `index.html` の各トピック末尾に記載しています。主なものを抜粋:

- PRISM: Fels (1986), *Energy and Buildings* / ASHRAE Guideline 14（変化点回帰）
- 階層モデル: Gelman & Hill, *Data Analysis Using Regression and Multilevel/Hierarchical Models*
- 分位点回帰: Koenker, *Quantile Regression*
- ADMD / 同時率: `after diversity maximum demand residential smart meter`, `需要率 不等率 変圧器 容量計画`
- Newey-West: `Newey-West standard errors time series regression`

---

## ライセンス / 注意

本ノートの図・数値はいずれも手法の説明のための模擬例です。実データへ適用する際は、
モデル選択・妥当性検証（交差検証、残差診断、非線形最適化の初期値依存性など）を別途
行ってください。
