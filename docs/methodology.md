# Methodology

Short notes on the choices in the three notebooks. The README has the reading order; this file says why.

## Data

All data is synthetic and seeded (42). Bars are random walks for 3 symbols on H1, H4 and D1. Trades are 800
random entries inside H1 bars with a random direction. The outcome is planted: a trade tends to win when its
direction agrees with the D1 EMA trend (`ema_20 > ema_200`), plus noise. So there is something to find, and the
AUC printed in step 3 says nothing about real trading.

## Step 1: features

Computed separately for each symbol and timeframe, after sorting by time:

| Feature | Definition |
|---|---|
| `stoch_k`, `stoch_d`, `stoch_up` | Close within the 20-bar high-low range (0-100), its 6-bar mean, and k above d |
| `ema_trend_up`, `dist_ema_200` | 20-bar EMA above 200-bar EMA; close relative to the 200-bar EMA |
| `rsi_14` | Wilder-style RSI over 14 bars |
| `atr_14_pct` | 14-bar mean true range divided by close |
| `bb_position` | (close - 20-bar mean) / (2 x 20-bar standard deviation) |
| `ret_1`, `ret_5`, `ret_20` | Percentage change over 1, 5 and 20 bars |

Every feature uses only the current bar and earlier ones. Rows with an empty rolling value are dropped.

## Step 2: the point-in-time join

- Each bar gets `available_at = bar start + bar length`. That is when its close, and so its features, are known.
- For each timeframe, `merge_asof` on `available_at` with `direction="backward"` and `by="symbol"` picks the last
  bar that had closed at or before the entry time.
- Columns are prefixed `H1_`, `H4_`, `D1_` so the three timeframes sit side by side.
- Joining on the bar's start time instead would hand each trade the bar it is sitting inside, whose close is in
  the future. That is the most common look-ahead bug in this kind of pipeline.

## Step 3: preprocessing and models

- Time split: entries up to the 70th percentile of entry time train, the rest test.
- `StandardScaler` is fitted on training rows and applied to both sets.
- KMeans (4 clusters, `n_init=10`) is fitted on the scaled D1 features of training rows only. Test rows are
  assigned with `predict`. Cluster labels become `regime_0` to `regime_3`.
- `direction` and `direction x D1 feature` interactions are added.
- Logistic regression and a random forest (300 trees, at least 20 rows per leaf). Metric: test AUC, with the
  test base rate for context.

## Known limitations

- Synthetic data with a planted effect; the model is only shown to find what was planted.
- One split, no cross-validation, about 190 test rows, so AUC differences of a few hundredths are noise.
- The 200-bar EMA starts from the first bar, so early values lean on very little history.
- Trades are independent random draws; real trades cluster in time and share market moves.
