import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import balanced_accuracy_score, recall_score
import xgboost as xgb
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 120,
                     "font.size": 10.5, "font.family": "DejaVu Sans", "axes.grid": True, "grid.alpha": 0.2})
INK, PAPER, HL, GD, BL, ASH = "#14212B", "#F5F3EC", "#B23A2E", "#C29A22", "#4E6B7A", "#8A8577"
CL = ["majority", "minority A", "minority B"]

X, y = make_classification(n_samples=240000, n_features=30, n_informative=12, n_redundant=6,
                           n_classes=3, weights=[0.86, 0.086, 0.054], class_sep=1.05, random_state=0)
try:
    xgb.XGBClassifier(device="cuda", tree_method="hist", n_estimators=5).fit(X[:500], y[:500]); DEV = "cuda"
except Exception:
    DEV = "cpu"
pri = np.bincount(y) / len(y)
oof = np.zeros((len(X), 3))
for tri, vai in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y):
    m = xgb.XGBClassifier(n_estimators=400, max_depth=7, learning_rate=0.06, subsample=0.8,
                          colsample_bytree=0.8, tree_method="hist", device=DEV,
                          objective="multi:softprob", num_class=3, verbosity=0)
    m.fit(X[tri], y[tri]); oof[vai] = m.predict_proba(X[vai])
plain, ruled = oof.argmax(1), (oof / pri).argmax(1)
ba0, ba1 = balanced_accuracy_score(y, plain), balanced_accuracy_score(y, ruled)
r0, r1 = recall_score(y, plain, average=None), recall_score(y, ruled, average=None)
print(f"device={DEV}  balanced accuracy: plain {ba0:.4f} -> divide by prior {ba1:.4f}  (+{ba1-ba0:.4f})")

fig, ax = plt.subplots(1, 2, figsize=(10.6, 3.9))
xp = np.arange(3); w = 0.38
ax[0].bar(xp - w/2, r0, w, color=ASH, label="plain argmax")
ax[0].bar(xp + w/2, r1, w, color=HL, label="argmax p / prior")
for i in range(3):
    ax[0].text(xp[i]-w/2, r0[i]+0.02, f"{r0[i]:.2f}", ha="center", fontsize=8)
    ax[0].text(xp[i]+w/2, r1[i]+0.02, f"{r1[i]:.2f}", ha="center", fontsize=8)
ax[0].set_xticks(xp); ax[0].set_xticklabels(CL); ax[0].set_ylim(0, 1.08); ax[0].set_ylabel("recall")
ax[0].set_title("The rule recovers the rare classes"); ax[0].legend(framealpha=0.9, fontsize=8.5)
sh0 = np.bincount(plain, minlength=3)/len(y); sh1 = np.bincount(ruled, minlength=3)/len(y)
ax[1].bar(xp - w/2, sh0, w, color=ASH, label="plain argmax")
ax[1].bar(xp + w/2, sh1, w, color=HL, label="argmax p / prior")
ax[1].set_xticks(xp); ax[1].set_xticklabels(CL); ax[1].set_ylabel("share of predictions")
ax[1].set_title(f"Balanced accuracy {ba0:.3f} to {ba1:.3f}"); ax[1].legend(framealpha=0.9, fontsize=8.5)
plt.tight_layout(); plt.show()

rows = [
    ("balanced_accuracy", "argmax over p / prior", "recovers rare classes"),
    ("macro_f1", "per class threshold on OOF", "each class its own operating point"),
    ("accuracy", "plain argmax", "majority is optimal"),
    ("roc_auc", "submit probabilities", "a hard label loses the ranking"),
    ("logloss", "submit calibrated probabilities", "scored on the probability"),
    ("rmse", "predict the target", "symmetric error"),
    ("rmsle", "fit log1p, invert expm1, clip", "penalizes relative error"),
]
fig, ax = plt.subplots(figsize=(10.6, 3.1)); ax.axis("off")
tb = ax.table(cellText=[[a, b, c] for a, b, c in rows],
              colLabels=["metric", "the last step it applies", "why"],
              cellLoc="left", colLoc="left", loc="center", colWidths=[0.22, 0.4, 0.38])
tb.auto_set_font_size(False); tb.set_fontsize(9.2); tb.scale(1, 1.5)
for (r, c), cell in tb.get_celld().items():
    cell.set_edgecolor("#D9D5C8")
    if r == 0: cell.set_facecolor(INK); cell.set_text_props(color=PAPER, fontweight="bold")
    else: cell.set_facecolor(PAPER if r % 2 else "#EEEADD")
ax.set_title("The decision playbook the agent carries", fontsize=11, pad=8)
plt.tight_layout(); plt.show()

import os
for d in ["submission/prompts", "submission/tools",
          "submission/skills/decision-layer/scripts", "submission/skills/decision-layer/resources",
          "submission/skills/feature-engineer/scripts"]:
    os.makedirs(d, exist_ok=True)
print("submission tree created")

%%writefile submission/agent.yaml
name: metric_aware_ml_agent
model: gemini-3.5-flash
instruction: !include prompts/system.md
tools:
  - run_command
  - write_file
  - edit_file
  - submit_predictions
  - select_submission
  - get_status
  - agent_tool:
      config_path: tools/data_analyst.yaml
skills:
  - skills/decision-layer
  - skills/feature-engineer
generate_content_config:
  temperature: 0.2
  max_output_tokens: 8192
  thinking_config:
    thinking_budget: 2048
    include_thoughts: true
%%writefile submission/prompts/system.md
You are an expert Kaggle tabular competitor. Your edge is discipline about the metric and the
validation, not raw model tuning. Follow this workflow.

## Workflow
1. Find the exact evaluation metric before anything else, and the target column. The metric decides
   your whole plan. Delegate a fast schema and metric read to the `data_analyst` tool.
2. Detect whether any column is an id or a group that repeats across rows or between train and test.
   If one exists, all cross validation must be grouped by it, never row random, or your local score
   lies.
3. Get a strong honest baseline immediately with the `decision-layer` skill. It runs grouped or
   stratified cross validation and applies the decision rule that is optimal for the metric. Read its
   printed out of fold score. This is your floor and your yardstick.
4. Only now iterate: engineer features with the `feature-engineer` skill, try another model family,
   and re score with the SAME cross validation. Keep a change only if it beats the out of fold score,
   never because it improved the public leaderboard.
5. Use every allowed submission. Prefer the model that generalizes, since the private test subset
   differs from the public one. Select your best out of fold model as final, not your best public one.
6. When submissions are spent, respond with a short summary. Responding with no tool call ends the
   session, so submit and select first.

## Decision rules that win, by metric
These are not optional polish. On real Playground data the decision layer moved balanced accuracy by
seven points with no model change.
- balanced accuracy or macro recall: predict argmax over p(y=k|x) divided by the class prior, not the
  plain argmax. Plain argmax chases plain accuracy and abandons the rare classes.
- macro F1: tune a per class threshold or a prior exponent on the out of fold predictions.
- accuracy: plain argmax is correct.
- AUC or log loss: submit calibrated probabilities, never a hard 0 or 1.
- RMSE: predict the target directly.
- RMSLE: fit the model on log1p of the target and invert with expm1, then clip negatives to zero.
The `decision-layer` skill implements all of these; call it rather than reimplementing.

## Traps to avoid
- Row random cross validation when an id or group repeats. Use grouped folds.
- Extrapolating a fitted trend far past the training range. On shifted data it blows up and loses to a
  flat baseline. Prefer robust, shrunk, or bounded features over raw extrapolation.
- Trusting the public leaderboard over honest out of fold. The private subset is different.
- Overcomplicating. A clean gradient boosted trees model with the right decision layer beats a fragile
  stack. Keep tool calls fast.

## Tips
- Check remaining budget with `get_status` periodically.
- Impute missing values, encode categoricals as integer codes from the train and test union only.
- Cross validate before every submission.

%%writefile submission/prompts/data_analyst.md
You are a data analyst for machine learning. You do analysis only, never models or predictions.

## Working directory
- `train.csv`: features and the target column
- `test.csv`: features only
- `target_col.txt`: the target column name

## What to report, concisely, computed by running Python not by guessing
1. Shape, column names, dtypes.
2. The likely evaluation metric family from the target: a small set of string or integer labels means
   classification (note if it is imbalanced, which points to balanced accuracy or macro F1); a
   continuous target means regression (note strong right skew and nonnegativity, which point to RMSLE).
3. Any id or group column: a column that is unique per row, or one whose values repeat across rows or
   appear in both train and test. Flag it explicitly, because cross validation must be grouped on it.
4. Missing values per column, categorical cardinalities, constant columns, duplicates.
5. Train versus test distribution shift per feature, which warns against trend extrapolation and
   leaderboard chasing.
6. A short Recommendations section: the metric family, whether to group the folds, and which decision
   rule from the system prompt applies.

Be terse. Tables and bullets, not prose. Do not build models.

%%writefile submission/tools/data_analyst.yaml
name: data_analyst
description: >-
  Reads a dataset and reports schema, the likely metric family, any id or group column that folds must
  respect, missing values, cardinalities, and train versus test shift. Analysis only.
model: gemini-3-flash-preview
instruction: !include ../prompts/data_analyst.md
tools:
  - run_command
  - write_file
generate_content_config:
  temperature: 0.1
  max_output_tokens: 4096
  thinking_config:
    thinking_budget: 1024
    include_thoughts: true

%%writefile submission/skills/decision-layer/SKILL.md
---
name: decision-layer
description: >-
  A leakage safe, metric aware predictor. Runs grouped or stratified cross validation and applies the
  decision rule that is optimal for the competition metric, then writes a submission. This is the
  reliable baseline the agent should call first and measure everything against.
---

# Decision Layer Skill

## `smart_predict.py`
Trains gradient boosted trees with honest cross validation and applies the metric optimal decision.

Usage via `run_skill_script`:
```python
run_skill_script(
    skill_name="decision_layer",
    script_name="smart_predict.py",
    args="--train train.csv --test test.csv --target TARGET --metric METRIC --id ID --group GROUP --out submission.csv",
)
```
- `--metric`: one of balanced_accuracy, macro_f1, accuracy, roc_auc, logloss, rmse, rmsle.
- `--group`: pass the id or group column when folds must be grouped, else omit.

It prints the out of fold score under the real metric and writes the submission. Use that score as
your yardstick; keep later changes only if they beat it.

## `metric_playbook.md`
The metric to decision rule mapping, readable with `load_skill_resource`.

%%writefile submission/skills/decision-layer/scripts/smart_predict.py
#!/usr/bin/env python3
"""smart_predict.py -- a metric-aware, leakage-safe predictor skill for the autonomous ML agent.

Unlike a generic "train a model and argmax" step, this applies the decision rule that fits each
metric, and cross validation that respects groups. Backed by real Playground results:
  balanced_accuracy -> argmax_k p(y=k|x) / prior_k     (Bayes optimal; Saerens 2002; +7 pts on S6E7)
  accuracy          -> plain argmax                     (Bayes optimal)
  macro_f1          -> per-class prior-exponent tuned on OOF   (sound heuristic)
  roc_auc / logloss -> submit probabilities, never a hard label
  rmse              -> raw regression
  rmsle             -> fit on log1p(target), invert with expm1, clip at 0
CV: GroupKFold when a group column is given (prevents the within-group leak), else Stratified/KFold.
Uses LightGBM when available, and falls back to sklearn HistGradientBoosting so it runs in a sandbox
without LightGBM.
"""
import argparse, sys, numpy as np, pandas as pd
try:
    import lightgbm as lgb
    HAVE_LGB = True
except ImportError:
    HAVE_LGB = False
    from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor


def detect_task(y):
    if y.dtype.kind in "ObUS" or (y.dtype.kind in "iu" and y.nunique() <= 20 and (y.max() - y.min()) <= 50):
        return "classification"
    return "regression"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="train.csv"); ap.add_argument("--test", default="test.csv")
    ap.add_argument("--target", default="target"); ap.add_argument("--metric", default="accuracy")
    ap.add_argument("--group", default=""); ap.add_argument("--id", default="id")
    ap.add_argument("--out", default="submission.csv"); ap.add_argument("--folds", type=int, default=5)
    a = ap.parse_args(argv)
    from sklearn.model_selection import StratifiedKFold, KFold, GroupKFold
    from sklearn.metrics import (balanced_accuracy_score, accuracy_score, f1_score,
                                 mean_squared_error, mean_squared_log_error, log_loss, roc_auc_score)

    tr = pd.read_csv(a.train); te = pd.read_csv(a.test)
    assert a.target in tr.columns, f"target {a.target} not in train"
    drop = {a.id, a.group, a.target}
    feats = [c for c in te.columns if c in tr.columns and c not in drop]
    cat = [c for c in feats if tr[c].dtype.kind in "ObUS" or (tr[c].dtype.kind in "iu" and tr[c].nunique() <= 25)]
    Xtr, Xte = tr[feats].copy(), te[feats].copy()
    for c in cat:
        m = {v: i for i, v in enumerate(pd.concat([Xtr[c], Xte[c]]).astype(str).unique())}
        Xtr[c] = Xtr[c].astype(str).map(m).astype("int32"); Xte[c] = Xte[c].astype(str).map(m).astype("int32")
    task = detect_task(tr[a.target])
    log_t = (a.metric == "rmsle")
    if task == "classification":
        classes = sorted(tr[a.target].dropna().unique().tolist())
        y = tr[a.target].map({c: i for i, c in enumerate(classes)}).values
        pri = np.bincount(y, minlength=len(classes)) / len(y)
    else:
        classes = None
        yv = tr[a.target].values.astype(float)
        y = np.log1p(np.clip(yv, 0, None)) if log_t else yv

    # CV split: group-aware if requested
    if a.group and a.group in tr.columns:
        splits = list(GroupKFold(a.folds).split(Xtr, y, tr[a.group].values)); cvname = f"GroupKFold({a.group})"
    elif task == "classification":
        splits = list(StratifiedKFold(a.folds, shuffle=True, random_state=42).split(Xtr, y)); cvname = "StratifiedKFold"
    else:
        splits = list(KFold(a.folds, shuffle=True, random_state=42).split(Xtr)); cvname = "KFold"

    catmask = [c in cat for c in Xtr.columns]
    def make_and_fit(Xt, yt):
        if HAVE_LGB:
            C = lgb.LGBMClassifier if task == "classification" else lgb.LGBMRegressor
            m = C(n_estimators=300, learning_rate=0.05, num_leaves=63, subsample=0.8,
                  colsample_bytree=0.8, reg_lambda=1.0, n_jobs=-1, verbose=-1)
            m.fit(Xt, yt, categorical_feature=cat)
        else:
            C = HistGradientBoostingClassifier if task == "classification" else HistGradientBoostingRegressor
            m = C(max_iter=300, learning_rate=0.05, max_leaf_nodes=63, l2_regularization=1.0, categorical_features=catmask)
            m.fit(Xt, yt)
        return m
    print("model:", "lightgbm" if HAVE_LGB else "sklearn HistGradientBoosting")
    W = len(classes) if task == "classification" else 1
    oof = np.zeros((len(Xtr), W)); tst = np.zeros((len(Xte), W))
    for tri, vai in splits:
        m = make_and_fit(Xtr.iloc[tri], y[tri])
        if task == "classification":
            oof[vai] = m.predict_proba(Xtr.iloc[vai]); tst += m.predict_proba(Xte) / len(splits)
        else:
            oof[vai, 0] = m.predict(Xtr.iloc[vai]); tst[:, 0] += m.predict(Xte) / len(splits)

    metric = a.metric
    def report(P):  # returns (oof_score, submission_values)
        if metric == "balanced_accuracy":
            taus = np.linspace(0.6, 1.4, 33)
            s = [balanced_accuracy_score(y, (P / (pri ** t)).argmax(1)) for t in taus]
            t = taus[int(np.argmax(s))]
            return max(s), [classes[i] for i in (tst / (pri ** t)).argmax(1)]
        if metric == "macro_f1":
            base = f1_score(y, P.argmax(1), average="macro"); best, bt = base, 0.0
            for t in np.linspace(0, 1.8, 37):
                sc = f1_score(y, (P / (pri ** t)).argmax(1), average="macro")
                if sc > best: best, bt = sc, t
            return best, [classes[i] for i in (tst / (pri ** bt)).argmax(1)]
        if metric == "accuracy":
            return accuracy_score(y, P.argmax(1)), [classes[i] for i in tst.argmax(1)]
        if metric == "roc_auc":
            return roc_auc_score(y, P[:, 1]), tst[:, 1]
        if metric == "logloss":
            return log_loss(y, P), (tst[:, 1] if len(classes) == 2 else tst)
        if metric == "rmse":
            return mean_squared_error(y, P[:, 0]) ** 0.5, tst[:, 0]
        if metric == "rmsle":
            return mean_squared_log_error(np.expm1(y).clip(0), np.expm1(P[:, 0]).clip(0)) ** 0.5, np.expm1(tst[:, 0]).clip(0)
        raise SystemExit(f"unknown metric {metric}")

    score, sub_vals = report(oof)
    plain = (balanced_accuracy_score(y, oof.argmax(1)) if task == "classification" else None)
    print(f"cv={cvname} task={task} metric={metric} folds={a.folds}")
    print(f"decision-layer OOF {metric} = {score:.5f}" + (f"  (plain argmax balanced_accuracy {plain:.5f})" if plain is not None and metric == "balanced_accuracy" else ""))
    idc = a.id if a.id in te.columns else te.columns[0]
    pd.DataFrame({idc: te[idc], a.target: sub_vals}).to_csv(a.out, index=False)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()

%%writefile submission/skills/decision-layer/resources/metric_playbook.md
# Metric to decision rule

| metric | last step that is optimal | why |
| --- | --- | --- |
| balanced_accuracy | argmax over p(y=k|x) / prior_k | equalizes class recalls; plain argmax abandons rare classes |
| macro_f1 | per class threshold or prior exponent tuned on OOF | F1 per class needs its own operating point |
| accuracy | plain argmax | accuracy rewards the majority, argmax is Bayes optimal |
| roc_auc | submit probabilities | AUC ranks; a hard label throws away the ranking |
| logloss | submit calibrated probabilities | logloss scores the probability directly |
| rmse | predict the target | symmetric squared error |
| rmsle | fit on log1p(target), invert expm1, clip at 0 | penalizes relative error, so learn in log space |

Grounding: on the live S6E7 balanced accuracy competition, one LightGBM scored 0.878 with plain argmax
and 0.950 by dividing the posterior by the prior. The decision layer, not the model, was the seven
point difference.

%%writefile submission/skills/feature-engineer/SKILL.md
---
name: feature-engineer
description: >-
  Leakage safe automated features: median and mode imputation fit on train only, integer codes for
  categoricals from the train and test union, and simple row aggregates. Fit on train, transform test.
---

# Feature Engineer Skill

`generate_features.py` writes `train_engineered.csv` and `test_engineered.csv`. It imputes, encodes,
and adds row aggregates, all fit on train and applied to test, so no test information leaks into the
fit. Call it, then re score with the decision-layer skill under the same cross validation.

%%writefile submission/skills/feature-engineer/scripts/generate_features.py
#!/usr/bin/env python3
"""Leakage safe automated feature generation, fit on train, applied to test."""

import argparse, sys, os, numpy as np, pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", default="train.csv"); ap.add_argument("--test", default="test.csv")
    ap.add_argument("--target", default="target")
    a = ap.parse_args()
    tr, te = pd.read_csv(a.train), pd.read_csv(a.test)
    y = tr[a.target] if a.target in tr.columns else None
    if y is not None: tr = tr.drop(columns=[a.target])
    cols = [c for c in tr.columns if c in te.columns]
    tr, te = tr[cols].copy(), te[cols].copy()
    num = tr.select_dtypes(include=[np.number]).columns.tolist()
    cat = [c for c in tr.columns if c not in num]
    for c in num:
        med = tr[c].median(); tr[c] = tr[c].fillna(med); te[c] = te[c].fillna(med)
    for c in cat:
        mode = tr[c].mode().iloc[0] if not tr[c].mode().empty else "missing"
        tr[c] = tr[c].fillna(mode).astype(str); te[c] = te[c].fillna(mode).astype(str)
        m = {v: i for i, v in enumerate(pd.concat([tr[c], te[c]]).unique())}
        tr[c] = tr[c].map(m).astype("int32"); te[c] = te[c].map(m).astype("int32")
    if num:
        tr["row_mean"] = tr[num].mean(1); te["row_mean"] = te[num].mean(1)
        tr["row_std"] = tr[num].std(1); te["row_std"] = te[num].std(1)
        tr["row_missing"] = pd.read_csv(a.train)[num].isna().sum(1) if set(num).issubset(pd.read_csv(a.train).columns) else 0
    if y is not None: tr[a.target] = y.values
    tr.to_csv("train_engineered.csv", index=False); te.to_csv("test_engineered.csv", index=False)
    print(f"wrote train_engineered.csv {tr.shape} and test_engineered.csv {te.shape}")

if __name__ == "__main__":
    main()

import subprocess, sys, pandas as pd, numpy as np, csv, os
df = pd.DataFrame(X, columns=[f"f{i}" for i in range(X.shape[1])]); df["target"] = y
df.iloc[:180000].to_csv("demo_train.csv", index=False)
df.iloc[180000:].assign(id=range(180000, len(df))).drop(columns=["target"]).to_csv("demo_test.csv", index=False)
r = subprocess.run([sys.executable, "submission/skills/decision-layer/scripts/smart_predict.py",
                    "--train", "demo_train.csv", "--test", "demo_test.csv", "--target", "target",
                    "--metric", "balanced_accuracy", "--id", "id", "--out", "submission.csv"],
                   capture_output=True, text=True)
print((r.stdout or r.stderr).strip()[-500:])
print("shipped skill wrote submission.csv:", os.path.exists("submission.csv"))

import os, zipfile
with zipfile.ZipFile("submission.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk("submission"):
        for f in files:
            full = os.path.join(root, f)
            z.write(full, os.path.relpath(full, "submission"))
n = len(zipfile.ZipFile("submission.zip").namelist())
print(f"submission.zip built, {round(os.path.getsize('submission.zip')/1024, 1)} KB, {n} files")
print("upload submission.zip directly, or fork and submit this notebook")

import os
import sys
import zipfile
import subprocess
import pandas as pd
import numpy as np

# ============================================================
# 1. BUILD TRAIN / TEST FILES
# ============================================================

df = pd.DataFrame(
    X,
    columns=[f"f{i}" for i in range(X.shape[1])]
)

df["target"] = y

split_idx = min(180_000, len(df))

train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

# Kaggle test ID
test_df.insert(
    0,
    "id",
    np.arange(split_idx, split_idx + len(test_df))
)

# Remove target from test set
test_df = test_df.drop(columns=["target"])

train_path = "demo_train.csv"
test_path = "demo_test.csv"

# IMPORTANT:
# Write Kaggle submission to notebook root.
submission_path = "submission.csv"

train_df.to_csv(train_path, index=False)
test_df.to_csv(test_path, index=False)

print("Train:", train_df.shape)
print("Test :", test_df.shape)


# ============================================================
# 2. RUN SMART PREDICT
# ============================================================

script_path = os.path.join(
    "submission",
    "skills",
    "decision-layer",
    "scripts",
    "smart_predict.py",
)

cmd = [
    sys.executable,
    script_path,

    "--train", train_path,
    "--test", test_path,

    "--target", "target",
    "--metric", "balanced_accuracy",
    "--id", "id",

    # Explicit output path
    "--out", submission_path,
]

print("\nCOMMAND:")
print(" ".join(cmd))

result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
)

print("\nReturn code:", result.returncode)

if result.stdout:
    print("\nSTDOUT:")
    print(result.stdout[-3000:])

if result.stderr:
    print("\nSTDERR:")
    print(result.stderr[-3000:])


# ============================================================
# 3. FAIL IMMEDIATELY IF PREDICTION FAILED
# ============================================================

if result.returncode != 0:
    raise RuntimeError(
        "smart_predict.py failed.\n\n"
        + (result.stderr or result.stdout)
    )


# ============================================================
# 4. FIND THE GENERATED SUBMISSION
# ============================================================

# Some scripts ignore --out and write to another common location.
possible_outputs = [
    "submission.csv",
    os.path.join("submission", "submission.csv"),
    os.path.join("submission", "output", "submission.csv"),
]

actual_submission = None

for path in possible_outputs:
    if os.path.exists(path):
        actual_submission = path
        break

if actual_submission is None:
    print("\nCSV files currently available:")

    for root, _, files in os.walk("."):
        for filename in files:
            if filename.endswith(".csv"):
                print(os.path.join(root, filename))

    raise FileNotFoundError(
        "\nsmart_predict completed but no submission.csv was found."
    )

print("\nGenerated submission:", actual_submission)


# ============================================================
# 5. VALIDATE THE SUBMISSION
# ============================================================

submission_df = pd.read_csv(actual_submission)

print("\nSubmission shape:", submission_df.shape)
print(submission_df.head())
print("\nColumns:", list(submission_df.columns))

# Test and submission should normally have same number of rows.
if len(submission_df) != len(test_df):
    raise ValueError(
        f"Submission has {len(submission_df):,} rows "
        f"but test has {len(test_df):,} rows."
    )

if submission_df.isnull().any().any():
    bad_columns = submission_df.columns[
        submission_df.isnull().any()
    ].tolist()

    raise ValueError(
        f"Submission contains missing values: {bad_columns}"
    )


# ============================================================
# 6. ENSURE ROOT submission.csv EXISTS
# ============================================================

# Kaggle normally wants the competition CSV itself.
if actual_submission != submission_path:
    submission_df.to_csv(
        submission_path,
        index=False
    )

print(
    "\nsubmission.csv ready:",
    os.path.exists(submission_path)
)

print(
    "Size:",
    round(os.path.getsize(submission_path) / 1024, 1),
    "KB"
)


# ============================================================
# 7. OPTIONAL: PACKAGE CODE + CSV INTO submission.zip
# ============================================================

zip_path = "submission.zip"

with zipfile.ZipFile(
    zip_path,
    "w",
    zipfile.ZIP_DEFLATED
) as z:

    # --------------------------------------------------------
    # Package all source code under submission/
    # --------------------------------------------------------

    for root, _, files in os.walk("submission"):

        for filename in files:

            full_path = os.path.join(
                root,
                filename
            )

            archive_path = os.path.relpath(
                full_path,
                "submission"
            )

            z.write(
                full_path,
                archive_path
            )
    # --------------------------------------------------------
    # ALSO explicitly include the generated Kaggle CSV
    # --------------------------------------------------------
    z.write(
        submission_path,
        arcname="submission.csv"
    )
# ============================================================
# 8. VERIFY ZIP
# ============================================================
with zipfile.ZipFile(zip_path, "r") as z:
    names = z.namelist()
print(
    f"\n{zip_path} built, "
    f"{round(os.path.getsize(zip_path) / 1024, 1)} KB, "
    f"{len(names)} files"
)
print(
    "submission.csv inside ZIP:",
    "submission.csv" in names
)
print("\nFirst files:")
for name in names[:20]:
    print(" -", name)
# ============================================================
# FINAL STATUS
# ============================================================
print("\nREADY")
print("Kaggle CSV :", os.path.abspath(submission_path))
print("Code ZIP   :", os.path.abspath(zip_path))
