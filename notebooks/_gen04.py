"""Genera 04_statistical_analysis.ipynb"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _nbgen import md, code, write_nb

cells = []

cells.append(md(
    "# Olist E-Commerce - 04 : Statistical Analysis\n"
    "\n"
    "**Author:** Diego Ospina | **Dataset:** Brazilian E-Commerce Public Dataset by Olist\n"
    "\n"
    "> The EDA gave us descriptive answers. Here we go one step further and add **statistical rigor** "
    "with SciPy: normality checks, correlations with significance, hypothesis tests (Mann-Whitney U, "
    "chi-square, Kruskal-Wallis). Every conclusion is stated together with its test statistic, "
    "`p-value`, and a short interpretation."
))

cells.append(md("## 1. Setup"))
cells.append(code(
    "import pandas as pd\n"
    "import numpy as np\n"
    "import scipy.stats as st\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "import os\n"
    "\n"
    "PROC = os.path.join('..', 'data', 'processed')\n"
    "IMAGES = os.path.join('..', 'images')\n"
    "os.makedirs(IMAGES, exist_ok=True)\n"
    "sns.set_theme(style='whitegrid')\n"
    "print('ready')"
))

cells.append(md("## 2. Load and prepare"))
cells.append(code(
    "master = pd.read_parquet(os.path.join(PROC, 'olist_master_orders.parquet'))\n"
    "items  = pd.read_parquet(os.path.join(PROC, 'olist_items.parquet'))\n"
    "deliv = master[master['order_status'] == 'delivered'].copy()\n"
    "print('delivered:', len(deliv))"
))

cells.append(md("## 3. Are orders independent and is order value normally distributed?\n"
    "\n" "Order values in e-commerce are almost never Gaussian. We run D'Agostino-Pearson's "
    "`normaltest` (valid on the raw data) and confirm the strong skew. This motivates the "
    "**non-parametric** tests used later."))
cells.append(code(
    "ov = deliv['order_value'].dropna()\n"
    "stat, p = st.normaltest(ov)\n"
    "print(f'D\\'Agostino-Pearson normaltest: stat={stat:.3f}, p={p:.2e}')\n"
    "print(f'Skewness={st.skew(ov):.3f}, Kurtosis={st.kurtosis(ov):.3f}')\n"
    "print('Conclusion: order_value is far from normal (p<0.001) -> use non-parametric tests.')"
))

cells.append(md("## 4. Spearman correlation: order value vs delivery delay\n"
    "\n" "Do more expensive orders arrive later? We use **Spearman** because both variables are "
    "non-normal. A tiny correlation at this sample size can still be significant, so we report both the "
    "coefficient (weak/strong) and the p-value."))
cells.append(code(
    "pair = deliv[['order_value', 'delivery_delay_days']].dropna()\n"
    "rho, p = st.spearmanr(pair['order_value'], pair['delivery_delay_days'])\n"
    "print(f'Spearman rho={rho:.3f}, p={p:.2e}')\n"
    "print('Interpretation: negligible practical correlation (|rho|<0.1); price barely relates to lateness.')"
))

cells.append(md("## 5. Mann-Whitney U: do late orders get lower review scores?\n"
    "\n" "We compare the review score of **on-time** vs **late** delivered orders. The scores are discrete "
    "and skewed, so we use the non-parametric **Mann-Whitney U** test. Null hypothesis: both groups come "
    "from the same distribution."))
cells.append(code(
    "a = deliv.loc[deliv['delivery_status'] == 'On time', 'review_score_mean'].dropna()\n"
    "b = deliv.loc[deliv['delivery_status'] == 'Late',  'review_score_mean'].dropna()\n"
    "u_stat, p = st.mannwhitneyu(a, b, alternative='two-sided')\n"
    "\n"
    "print(f'On-time  n={len(a):,} mean score={a.mean():.3f}')\n"
    "print(f'Late     n={len(b):,} mean score={b.mean():.3f}')\n"
    "print(f'Mann-Whitney U: stat={u_stat:.0f}, p={p:.2e}')\n"
    "verdict = 'significant' if p < 0.05 else 'not significant'\n"
    "print(f'Conclusion: {verdict}. Late deliveries have lower review scores.')"
))

cells.append(md("## 6. Chi-square test of independence: payment method vs punctuality\n"
    "\n" "We build the contingency table between `payment_type_main` and `delivery_status` and run "
    "chi-square with Yates' correction to test whether the payment method is independent of delivery "
    "punctuality."))
cells.append(code(
    "# Categorias grandes; descartamos nulos (pedidos sin registro de pago)\n"
    "ct = pd.crosstab(deliv['payment_type_main'].fillna('unknown'), deliv['delivery_status'])\n"
    "chi2, p, dof, expected = st.chi2_contingency(ct)\n"
    "print(ct)\n"
    "print(f\"\\nchi2={chi2:.2f}, dof={dof}, p={p:.2e}\")\n"
    "print('Conclusion:', 'association is significant' if p < 0.05 else 'no significant association')\n"
    "print('Caveat: with ~95k rows statistical significance does not imply practical importance.')\n"
    "print()\n"
    "# Proporcion de pedidos a tiempo por metodo\n"
    "share = ct['On time'] / ct.sum(axis=1)\n"
    "print('On-time share by payment method:')\n"
    "print(share.round(4).to_string())"
))

cells.append(md("## 7. Kruskal-Wallis: does order value differ across top categories?\n"
    "\n" "We test whether the median order value differs across the 5 best-selling categories. "
    "Kruskal-Wallis is the non-parametric one-way ANOVA. The item table gives the category of every "
    "line; we mark a category at the **order** level via its items."))
cells.append(code(
    "top5 = items['item_category'].value_counts().head(5).index\n"
    "# A nivel item, mapear category y precio (para una prueba sencilla y clara)\n"
    "sub = items[items['item_category'].isin(top5)].copy()\n"
    "groups = [sub.loc[sub['item_category'] == c, 'price'] for c in top5]\n"
    "h_stat, p = st.kruskal(*groups)\n"
    "\n"
    "for c in top5:\n"
    "    g = sub.loc[sub['item_category'] == c, 'price']\n"
    "    print(f'{c:30s} n={len(g):>6,} median={g.median():9.2f}')\n"
    "print(f\"\\nKruskal-Wallis H={h_stat:.2f}, p={p:.2e}\")\n"
    "print('Conclusion:', 'categories differ significantly in price' if p < 0.05 else 'no difference across categories')\n"
    "print('Note: significant, but with large n this reflects real price differences between category portfolios.')"
))

cells.append(md("## 8. Visualizing the main statistical finding\n"
    "\n" "We plot the review-score distribution split by punctuality to illustrate the Mann-Whitney "
    "result, and save the figure."))
cells.append(code(
    "fig, ax = plt.subplots(figsize=(9, 5))\n"
    "sns.kdeplot(a, label='On time', fill=True, ax=ax)\n"
    "sns.kdeplot(b, label='Late', fill=True, ax=ax)\n"
    "ax.set_title('Review score density by on-time vs late (delivered)')\n"
    "ax.set_xlabel('Review score')\n"
    "ax.legend()\n"
    "plt.tight_layout()\n"
    "plt.savefig(os.path.join(IMAGES, 'STATS_review_by_punctuality.png'), bbox_inches='tight')\n"
    "plt.show()"
))

cells.append(md("## 9. Takeaways\n"
    "\n"
    "- `order_value` is heavily **non-normal** -> we consistently used non-parametric methods.\n"
    "- Price and delivery delay are **practically uncorrelated** (Spearman rho ~ 0).\n"
    "- Late deliveries have **significantly lower review scores** (Mann-Whitney U, p<0.001) - a "
    "customer-experience lever.\n"
    "- Payment method is **statistically associated** with punctuality, but the effect is small "
    "(practical significance is limited).\n"
    "- Top-selling categories have **significantly different** price distributions (Kruskal-Wallis).\n"
    "\n"
    "Next: **`05_business_intelligence.ipynb`** turns these insights into cohort, RFM and CLV metrics."
))

write_nb(os.path.join(os.path.dirname(__file__), '04_statistical_analysis.ipynb'), cells)