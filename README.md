# ML Model-Building Workflow

The three-step workflow I used to turn price bars and a list of trade entries into a dataset a classifier can learn from: build technical features per symbol and timeframe, attach them to each trade entry without look-ahead, then standardise, cluster into regimes and fit a first model.

It runs end to end on synthetic bars and synthetic trades, so no data files are needed.

## Structure

```
notebooks/
  01_feature_engineering.ipynb          stochastic, EMA trend, RSI, ATR, Bollinger position, returns
  02_merge_features_with_entries.ipynb  point-in-time join of H1/H4/D1 features onto entries
  03_standardize_cluster_flag.ipynb     train-only scaling and KMeans regimes, flags, logistic and random forest
```

Run them in order; each one writes its output to `data/outputs/` for the next.

## How to run

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab notebooks/
```

Set `DATA_DIR` to read and write somewhere other than `data/`.

## What I learned

- The join between features and entries is where look-ahead sneaks in. A bar's features are only usable once the bar has closed, so I key the merge on the bar's close time, not its open time.
- Scalers and clustering are part of the model. Fitting them on the whole dataset leaks the test period's distribution into training.
- Regime flags from clustering are easy to explain to non-technical readers, but they rarely beat giving the model the raw features plus a few interactions.
- Writing indicators in pandas instead of a compiled library made the pipeline easier to install and to check by hand.

## Status

A teaching and reference version of an older workflow, rebuilt cleanly. The synthetic outcome has a planted trend effect so the model has something to find; the AUC it prints says nothing about real trading.
