# ML Model-Building Workflow

[![CI](https://github.com/Avinash186200/ml-model-building-workflow/actions/workflows/ci.yml/badge.svg)](https://github.com/Avinash186200/ml-model-building-workflow/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.11-blue) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

The three-step workflow I used to turn price bars and a list of trade entries into a dataset a classifier can learn from: build technical features per symbol and timeframe, attach them to each trade entry without look-ahead, then standardise, cluster into regimes and fit a first model.

It runs end to end on synthetic bars and synthetic trades, so no data files are needed.

## What problem this solves

You have a list of trades (when you entered, which way, did it win) and price bars for the same symbols. You want a model that says, at entry, how likely a trade is to win. To get there you need features from the bars, joined to each trade using only bars that had already closed, then scaled and modelled without letting the test period leak into training. These three notebooks walk through that pipeline step by step.

## What you will learn

- How to compute common technical indicators (stochastic, EMA, RSI, ATR, Bollinger position) in plain pandas, per symbol and timeframe.
- How to attach features from several timeframes to an event with a point-in-time merge, so no trade sees a bar that had not closed.
- How to split by time, and fit the scaler and the clustering on the training period only.
- How to turn clusters into regime flags and interaction features a model can use.
- How to compare a logistic regression and a random forest by test AUC against the base rate.

## How it works

Run the notebooks in order. Each one writes a CSV to `data/outputs/` at the repo root that the next one reads; 02 and 03 stop with a clear message if the previous step has not been run.

1. [`01_feature_engineering.ipynb`](notebooks/01_feature_engineering.ipynb): makes 3,000 synthetic OHLC bars for each of 3 symbols on 3 timeframes (H1, H4, D1) and computes the indicators per symbol and timeframe. The first 24 rows of each series, where a rolling indicator is still empty, are dropped, leaving 2,976 per series. Teaches: indicator definitions, and why you compute them per group. Writes `features.csv`.
2. [`02_merge_features_with_entries.ipynb`](notebooks/02_merge_features_with_entries.ipynb): makes 800 synthetic trade entries at random minutes inside H1 bars and attaches the last closed H1, H4 and D1 bar's features to each one. The synthetic win/loss outcome is tied to the D1 trend and the trade direction, plus noise. Rows without a full feature set are dropped, leaving 644 rows with 34 columns. Teaches: the point-in-time join. Writes `model_dataset.csv`.
3. [`03_standardize_cluster_flag.ipynb`](notebooks/03_standardize_cluster_flag.ipynb): splits by entry time (first 70% train), fits `StandardScaler` and a 4-cluster KMeans on the D1 features of the training rows only, adds one-hot regime flags and direction interactions, then fits two models. On the default seed: logistic regression test AUC 0.737, random forest 0.777, test base rate 0.404. Teaches: train-only preprocessing and a fair first model.

## Key concepts

- **Timeframe:** the bar length. H1 is one hour, H4 four hours, D1 one day.
- **Indicator warm-up:** a 20-bar range needs 20 bars before its first value. Rows where a rolling indicator is still empty are dropped. (The EMA has a value from the first bar, but a 200-bar EMA is not reliable until it has seen a few hundred bars.)
- **Bar close time:** a bar stamped 10:00 on H1 is only complete at 11:00. Here `available_at = date + bar length`.
- **Point-in-time merge:** `pandas.merge_asof(..., by="symbol", direction="backward")` on `available_at` gives each trade the latest bar that had closed by entry time.
- **Look-ahead:** using information that did not exist yet at decision time. It makes backtests look better than reality.
- **Time-ordered split:** train on earlier trades, test on later ones, never shuffled.
- **Train-only scaling:** the scaler's mean and standard deviation come from training rows only, then the same transform is applied to test rows.
- **Regime flags:** KMeans groups training rows by their D1 features; each cluster becomes a 0/1 column.
- **Interaction feature:** `direction x feature`, so the model can learn that an up-trend helps longs and hurts shorts.
- **AUC and base rate:** AUC 0.5 is a coin flip; the base rate is the share of wins in the test set.

## Repo layout

```
notebooks/
  01_feature_engineering.ipynb          stochastic, EMA trend, RSI, ATR, Bollinger position, returns
  02_merge_features_with_entries.ipynb  point-in-time join of H1/H4/D1 features onto entries
  03_standardize_cluster_flag.ipynb     train-only scaling and KMeans regimes, flags, logistic and random forest
tests/
  test_notebooks.py   every notebook is valid, output-free, with no credentials or local paths
docs/
  README.md           index of the docs
  methodology.md      method notes and the reasons behind each choice
original/             the original research notebooks (read-only record)
.github/workflows/ci.yml   runs the tests on every push
.env.example · requirements.txt · CHANGELOG.md · CONTRIBUTING.md · LICENSE
```

## How to run

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
jupyter lab notebooks/
```

Outputs go to `data/outputs/` at the repo root (git-ignored), whether you start Jupyter from the repo root or from `notebooks/`. Set `DATA_DIR` to read and write somewhere else. Notebooks are committed without outputs; run them to see the tables.

## What I learned

- The join between features and entries is where look-ahead sneaks in. A bar's features are only usable once the bar has closed, so I key the merge on the bar's close time, not its open time.
- Scalers and clustering are part of the model. Fitting them on the whole dataset leaks the test period's distribution into training.
- Regime flags from clustering are easy to explain to non-technical readers, but they rarely beat giving the model the raw features plus a few interactions.
- Writing indicators in pandas instead of a compiled library made the pipeline easier to install and to check by hand.

## Status

A teaching and reference version of an older workflow, rebuilt cleanly. The synthetic outcome has a planted trend effect so the model has something to find; the AUC it prints says nothing about real trading.

## Original research code

[`original/`](original/README.md) holds the code as I first wrote it for this project. It is kept so you can
read the first version alongside the maintained one; some of it contains the issues in the audit table above,
and comparing the two shows each fix.

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [CHANGELOG](CHANGELOG.md).
