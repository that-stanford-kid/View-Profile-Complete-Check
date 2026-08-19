# =====================================================================
# Predicting Smartphone Addiction (PS S6E8) - v5  (STACKED, best effort)
# Realistic ceiling on this data is ~0.97 AUC (public LB tops out ~0.971).
# 1) Settings -> Accelerator -> GPU P100
# 2) Paste this ENTIRE block into ONE cell and Run All.
# Pipeline:
#   - domain features + missing indicators + CV-safe target encoding
#   - 4 diverse base learners on SHARED 5 folds, 2-seed averaged:
#       LightGBM, XGBoost, CatBoost (GPU auto), HistGradientBoosting (CPU)
#   - out-of-fold (OOF) matrix -> Logistic-Regression meta-stacker
#     evaluated with honest nested CV
#   - final = argmax OOF-AUC over {stack, rank-blend, best single}
# Runtime ~20-30 min on a P100.
# =====================================================================
import glob, subprocess, warnings, numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from scipy.stats import rankdata
warnings.filterwarnings("ignore")

def find(name): return glob.glob(f"/kaggle/input/**/{name}", recursive=True)[0]
train = pd.read_csv(find("train.csv"))
test  = pd.read_csv(find("test.csv"))
sub   = pd.read_csv(find("sample_submission.csv"))
TARGET, IDCOL = "addicted_label", "id"
y = train[TARGET].astype(int).values
print("train", train.shape, "test", test.shape, "pos rate", round(train[TARGET].mean(), 4))

NUM = ["age", "daily_screen_time_hours", "social_media_hours", "gaming_hours",
       "work_study_hours", "sleep_hours", "notifications_per_day",
       "app_opens_per_day", "weekend_screen_time"]
CAT = ["gender", "stress_level", "academic_work_impact"]
E = 1e-6
full = pd.concat([train.drop(columns=[TARGET]), test], axis=0, ignore_index=True)

# ---------------- missing-value signal ----------------
miss_cols = []
for c in NUM + CAT:
    full[f"{c}_isna"] = full[c].isna().astype("int8"); miss_cols.append(f"{c}_isna")
full["n_missing"] = full[[f"{c}_isna" for c in NUM + CAT]].sum(axis=1)

# ---------------- domain-informed features ----------------
scr = full["daily_screen_time_hours"]; sm = full["social_media_hours"]
gm = full["gaming_hours"]; wk = full["work_study_hours"]; sl = full["sleep_hours"]
notif = full["notifications_per_day"]; opens = full["app_opens_per_day"]
wknd = full["weekend_screen_time"]
full["leisure_hours"] = sm + gm
full["accounted_hours"] = sm + gm + wk
full["unaccounted_screen"] = scr - (sm + gm + wk)
full["leisure_ratio"] = (sm + gm) / (scr + E)
full["social_ratio"] = sm / (scr + E)
full["gaming_ratio"] = gm / (scr + E)
full["work_ratio"] = wk / (scr + E)
full["screen_per_open"] = scr / (opens + E)
full["notif_per_open"] = notif / (opens + E)
full["notif_per_screen_hr"] = notif / (scr + E)
full["opens_per_screen_hr"] = opens / (scr + E)
full["screen_to_sleep"] = scr / (sl + E)
full["screen_share_awake"] = scr / (24 - sl + E)
full["sleep_deficit"] = 8.0 - sl
full["weekend_gap"] = wknd - scr
full["weekend_ratio"] = wknd / (scr + E)
full["social_plus_gaming_vs_sleep"] = (sm + gm) / (sl + E)
full["notif_x_opens"] = notif * opens
full["age_x_screen"] = full["age"] * scr
full["stress_ord"] = full["stress_level"].map({"Low": 0, "Medium": 1, "High": 2})
full["impact_bin"] = full["academic_work_impact"].map({"No": 0, "Yes": 1})
eng = ["leisure_hours", "accounted_hours", "unaccounted_screen", "leisure_ratio",
       "social_ratio", "gaming_ratio", "work_ratio", "screen_per_open",
       "notif_per_open", "notif_per_screen_hr", "opens_per_screen_hr",
       "screen_to_sleep", "screen_share_awake", "sleep_deficit", "weekend_gap",
       "weekend_ratio", "social_plus_gaming_vs_sleep", "notif_x_opens",
       "age_x_screen", "stress_ord", "impact_bin"]

for c in CAT:
    full[c] = full[c].astype("category")
code_cols = []
for c in CAT:
    full[f"{c}_code"] = full[c].cat.codes.astype("int32"); code_cols.append(f"{c}_code")

num_cols = NUM + eng + miss_cols + ["n_missing"]
Xtr = full.iloc[:len(train)].reset_index(drop=True)
Xte = full.iloc[len(train):].reset_index(drop=True)

# ---------------- CV-safe target encoding ----------------
def target_encode(tr_col, yv, te_col, n_splits=5, smoothing=100.0, seed=1):
    prior = yv.mean(); oof = np.full(len(tr_col), prior, float)
    s = StratifiedKFold(n_splits, shuffle=True, random_state=seed)
    tr_s = tr_col.astype(str).reset_index(drop=True)
    for i, j in s.split(tr_s, yv):
        d = pd.DataFrame({"c": tr_s.iloc[i].values, "y": yv[i]})
        st = d.groupby("c")["y"].agg(["mean", "count"])
        enc = (st["mean"] * st["count"] + prior * smoothing) / (st["count"] + smoothing)
        oof[j] = tr_s.iloc[j].map(enc).fillna(prior).values
    d = pd.DataFrame({"c": tr_s.values, "y": yv})
    st = d.groupby("c")["y"].agg(["mean", "count"])
    enc = (st["mean"] * st["count"] + prior * smoothing) / (st["count"] + smoothing)
    return oof, te_col.astype(str).map(enc).fillna(prior).values

te_cols = []
for c in CAT:
    a, b = target_encode(Xtr[c], y, Xte[c])
    Xtr[f"te_{c}"] = a; Xte[f"te_{c}"] = b; te_cols.append(f"te_{c}")

num_all  = num_cols + te_cols
lgb_cols = num_all + CAT              # native categoricals for LGB / CatBoost
xgb_cols = num_all + code_cols        # ordinal codes for XGB / HistGB
print(f"features: {len(num_all)} numeric (+3 target-enc), {len(CAT)} categorical")

# ---------------- GPU detection (count devices for multi-GPU CatBoost) ----------------
N_GPU = 0
try:
    r = subprocess.run(["nvidia-smi", "-L"], capture_output=True, timeout=15, text=True)
    if r.returncode == 0:
        N_GPU = sum(1 for ln in r.stdout.splitlines() if ln.strip().startswith("GPU"))
except Exception:
    N_GPU = 0
CUDA_OK = N_GPU >= 1
CAT_DEVICES = "0:1" if N_GPU >= 2 else "0"          # CatBoost spans both T4s if present
print(f"CUDA GPUs detected: {N_GPU}  ->", "GPU" if CUDA_OK else "CPU",
      f"(CatBoost devices={CAT_DEVICES})" if CUDA_OK else "")

# ---------------- shared folds + base-learner OOF framework ----------------
N_SPLITS, SEEDS = 5, [42, 2026]
skf = StratifiedKFold(N_SPLITS, shuffle=True, random_state=2024)
folds = list(skf.split(Xtr, y))
oof, pred = {}, {}

import lightgbm as lgb, xgboost as xgb
from catboost import CatBoostClassifier, Pool
from sklearn.ensemble import HistGradientBoostingClassifier

LGB_DEV = "gpu"
try:
    lgb.train({"objective": "binary", "device_type": "gpu", "max_bin": 255, "verbose": -1},
              lgb.Dataset(Xtr[num_all].head(2000), y[:2000]), num_boost_round=1)
except Exception:
    LGB_DEV = "cpu"
print("LightGBM device:", LGB_DEV)

def run_lgb():
    p = dict(objective="binary", metric="auc", learning_rate=0.03, num_leaves=160,
             feature_fraction=0.6, bagging_fraction=0.8, bagging_freq=1,
             min_child_samples=80, lambda_l1=1.0, lambda_l2=3.0, max_depth=-1,
             verbose=-1, n_jobs=-1, device_type=LGB_DEV, max_bin=255)
    o = np.zeros(len(Xtr)); t = np.zeros(len(Xte))
    for i, j in folds:
        for s in SEEDS:
            dtr = lgb.Dataset(Xtr.iloc[i][lgb_cols], y[i], categorical_feature=CAT)
            dva = lgb.Dataset(Xtr.iloc[j][lgb_cols], y[j], categorical_feature=CAT)
            m = lgb.train({**p, "seed": s}, dtr, num_boost_round=6000, valid_sets=[dva],
                          callbacks=[lgb.early_stopping(100), lgb.log_evaluation(0)])
            o[j] += m.predict(Xtr.iloc[j][lgb_cols]) / len(SEEDS)
            t    += m.predict(Xte[lgb_cols]) / (len(SEEDS) * N_SPLITS)
    return o, t

def run_xgb():
    p = dict(objective="binary:logistic", eval_metric="auc", eta=0.03, max_depth=8,
             subsample=0.8, colsample_bytree=0.6, min_child_weight=5, reg_lambda=3.0,
             reg_alpha=1.0, tree_method="hist", device="cuda" if CUDA_OK else "cpu")
    dtest = xgb.DMatrix(Xte[xgb_cols]); o = np.zeros(len(Xtr)); t = np.zeros(len(Xte))
    for i, j in folds:
        dtr = xgb.DMatrix(Xtr.iloc[i][xgb_cols], y[i])
        dva = xgb.DMatrix(Xtr.iloc[j][xgb_cols], y[j])
        for s in SEEDS:
            m = xgb.train({**p, "seed": s}, dtr, num_boost_round=6000, evals=[(dva, "v")],
                          early_stopping_rounds=100, verbose_eval=False)
            o[j] += m.predict(dva) / len(SEEDS)
            t    += m.predict(dtest) / (len(SEEDS) * N_SPLITS)
    return o, t

def run_cat():
    Xc, Xtc = Xtr[lgb_cols].copy(), Xte[lgb_cols].copy()
    for c in CAT:
        Xc[c] = Xc[c].astype(str); Xtc[c] = Xtc[c].astype(str)
    ci = [lgb_cols.index(c) for c in CAT]
    gpu = dict(task_type="GPU", devices=CAT_DEVICES) if CUDA_OK else dict(task_type="CPU")
    pte = Pool(Xtc, cat_features=ci); o = np.zeros(len(Xtr)); t = np.zeros(len(Xte))
    for i, j in folds:
        for s in SEEDS:
            m = CatBoostClassifier(iterations=6000, learning_rate=0.05, depth=8,
                                   l2_leaf_reg=6.0, loss_function="Logloss",
                                   eval_metric="AUC", random_seed=s, **gpu,
                                   od_type="Iter", od_wait=100, verbose=0)
            m.fit(Pool(Xc.iloc[i], y[i], cat_features=ci),
                  eval_set=Pool(Xc.iloc[j], y[j], cat_features=ci))
            o[j] += m.predict_proba(Xc.iloc[j])[:, 1] / len(SEEDS)
            t    += m.predict_proba(pte)[:, 1] / (len(SEEDS) * N_SPLITS)
    return o, t

def run_hgb():
    o = np.zeros(len(Xtr)); t = np.zeros(len(Xte))
    for i, j in folds:
        for s in SEEDS:
            m = HistGradientBoostingClassifier(max_iter=1500, learning_rate=0.03,
                    max_leaf_nodes=63, l2_regularization=2.0, min_samples_leaf=60,
                    early_stopping=True, validation_fraction=0.1, n_iter_no_change=60,
                    random_state=s)
            m.fit(Xtr.iloc[i][xgb_cols], y[i])
            o[j] += m.predict_proba(Xtr.iloc[j][xgb_cols])[:, 1] / len(SEEDS)
            t    += m.predict_proba(Xte[xgb_cols])[:, 1] / (len(SEEDS) * N_SPLITS)
    return o, t

for name, fn in [("lgb", run_lgb), ("xgb", run_xgb), ("cat", run_cat), ("hgb", run_hgb)]:
    o, t = fn(); oof[name], pred[name] = o, t
    print(f"{name.upper()} OOF AUC: {roc_auc_score(y, o):.5f}")

# ---------------- meta-stacker (honest nested CV) ----------------
names = list(oof.keys())
OOF = np.column_stack([oof[n] for n in names])
TEST = np.column_stack([pred[n] for n in names])

meta_oof = np.zeros(len(Xtr))
for i, j in folds:
    lr = LogisticRegression(C=1.0, max_iter=2000)
    lr.fit(OOF[i], y[i]); meta_oof[j] = lr.predict_proba(OOF[j])[:, 1]
stack_auc = roc_auc_score(y, meta_oof)
lr_full = LogisticRegression(C=1.0, max_iter=2000).fit(OOF, y)
meta_test = lr_full.predict_proba(TEST)[:, 1]
print("STACK  OOF AUC:", round(stack_auc, 5), "| coefs:",
      dict(zip(names, np.round(lr_full.coef_[0], 3))))

# ---------------- rank-blend + best single ----------------
def rank01(a): return rankdata(a) / len(a)
w = {n: max(roc_auc_score(y, oof[n]) - 0.5, 1e-6) for n in names}
sw = sum(w.values()); w = {n: v / sw for n, v in w.items()}
blend_oof = sum(w[n] * rank01(oof[n]) for n in names)
blend_test = sum(w[n] * rank01(pred[n]) for n in names)
blend_auc = roc_auc_score(y, blend_oof)
best_n = max(names, key=lambda n: roc_auc_score(y, oof[n]))
best_auc = roc_auc_score(y, oof[best_n])
print("BLEND  OOF AUC:", round(blend_auc, 5))
print("BEST SINGLE:", best_n, round(best_auc, 5))

cands = {"stack": (stack_auc, rank01(meta_test)),
         "blend": (blend_auc, blend_test),
         "single": (best_auc, rank01(pred[best_n]))}
winner = max(cands, key=lambda k: cands[k][0])
print(f"==> FINAL = {winner}  (OOF AUC {cands[winner][0]:.5f})")

sub[TARGET] = cands[winner][1]
sub.to_csv("submission.csv", index=False)
print("submission.csv written", sub.shape); print(sub.head())
