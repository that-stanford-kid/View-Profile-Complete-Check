from __future__ import annotations

import math
import random
from collections import deque, namedtuple
from dataclasses import dataclass
from typing import Deque, List, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical

# Reproducibility / device

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device(
    "mps" if torch.backends.mps.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)

# Configuration

@dataclass
class Config:
    obs_dim: int = 24
    seq_len: int = 12
    hidden_dim: int = 128
    attn_heads: int = 8
    num_actions: int = 8
    num_agents: int = 6
    agent_embed_dim: int = 64

    gamma: float = 0.985
    n_step: int = 3

    replay_capacity: int = 50_000
    batch_size: int = 128
    per_alpha: float = 0.65
    per_beta_start: float = 0.40
    per_beta_end: float = 1.00
    per_beta_frames: int = 30_000
    priority_eps: float = 1e-5

    lr: float = 2e-4
    weight_decay: float = 1e-5
    grad_clip: float = 5.0
    tau: float = 0.0075

    eps_start: float = 1.0
    eps_end: float = 0.04
    eps_decay_steps: int = 20_000

    episodes: int = 220
    max_steps: int = 80
    warmup_steps: int = 1_000
    train_every: int = 1
    updates_per_step: int = 1

    eval_every: int = 20
    eval_episodes: int = 8


CFG = Config()

# Synthetic environment

class AdaptiveInvestigationEnv:
    """
    Partially observable toy environment.

    Hidden state:
      threat_level ∈ [0,1]
      uncertainty ∈ [0,1]
      persistence ∈ [0,1]
      disruption ∈ [0,1]

    Actions:
      0 observe
      1 inspect_process
      2 inspect_network
      3 inspect_memory
      4 correlate_identity
      5 spawn_specialist
      6 contain
      7 remediate

    The environment is intentionally stochastic so the agent must learn
    sequences rather than memorize a fixed action mapping.
    """

    ACTION_NAMES = [
        "observe",
        "inspect_process",
        "inspect_network",
        "inspect_memory",
        "correlate_identity",
        "spawn_specialist",
        "contain",
        "remediate",
    ]

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.rng = np.random.default_rng(SEED)
        self.step_count = 0
        self.threat = 0.0
        self.uncertainty = 1.0
        self.persistence = 0.0
        self.disruption = 0.0
        self.last_action = 0
        self.evidence = np.zeros(6, dtype=np.float32)

    def reset(self) -> np.ndarray:
        self.step_count = 0
        self.threat = float(self.rng.beta(2.2, 2.0))
        self.uncertainty = float(self.rng.uniform(0.55, 0.95))
        self.persistence = float(self.rng.beta(1.5, 3.0))
        self.disruption = 0.0
        self.last_action = 0
        self.evidence = np.zeros(6, dtype=np.float32)
        return self._observe()

    @staticmethod
    def entropy_binary(p: float) -> float:
        p = np.clip(p, 1e-6, 1 - 1e-6)
        return float(-(p * math.log(p) + (1 - p) * math.log(1 - p)))

    def _observe(self) -> np.ndarray:
        # Noisy telemetry generated from the latent state.
        noise = self.rng.normal(0, 0.08, size=8)

        telemetry = np.array([
            self.threat + noise[0],                     # risk proxy
            0.65 * self.threat + noise[1],              # process anomaly
            0.75 * self.threat + 0.15*self.persistence + noise[2],  # network anomaly
            0.55 * self.threat + 0.25*self.persistence + noise[3],  # memory anomaly
            0.45 * self.threat + noise[4],              # identity anomaly
            self.persistence + noise[5],                 # persistence proxy
            self.uncertainty + noise[6],                 # uncertainty
            self.disruption + noise[7],                  # operational disruption
        ], dtype=np.float32)

        action_onehot = np.zeros(self.cfg.num_actions, dtype=np.float32)
        action_onehot[self.last_action] = 1.0

        # 8 telemetry + 6 evidence + 8 action one-hot + 2 time signals = 24
        t = self.step_count / max(1, self.cfg.max_steps)
        time_feats = np.array(
            [math.sin(2 * math.pi * t), math.cos(2 * math.pi * t)],
            dtype=np.float32,
        )

        obs = np.concatenate([
            telemetry,
            self.evidence.astype(np.float32),
            action_onehot,
            time_feats,
        ]).astype(np.float32)

        assert obs.shape[0] == self.cfg.obs_dim
        return obs

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        self.step_count += 1
        self.last_action = int(action)

        prev_threat = self.threat
        prev_uncertainty = self.uncertainty
        prev_entropy = self.entropy_binary(np.clip(self.threat, 1e-5, 1 - 1e-5))

        # Natural dynamics
        drift = self.rng.normal(0.015 + 0.025*self.persistence, 0.02)
        self.threat = float(np.clip(self.threat + drift, 0, 1))

        # Action effects
        investigation_gain = 0.0
        remediation_gain = 0.0
        disruption_cost = 0.0
        compute_cost = 0.0

        if action == 0:  # observe
            investigation_gain = 0.02
            compute_cost = 0.01

        elif action == 1:  # inspect_process
            signal = 0.10 + 0.18*self.threat
            self.evidence[0] = np.clip(self.evidence[0] + signal, 0, 1)
            self.uncertainty *= 0.90
            investigation_gain = 0.10
            compute_cost = 0.03

        elif action == 2:  # inspect_network
            signal = 0.12 + 0.22*self.threat
            self.evidence[1] = np.clip(self.evidence[1] + signal, 0, 1)
            self.uncertainty *= 0.86
            investigation_gain = 0.13
            compute_cost = 0.05

        elif action == 3:  # inspect_memory
            signal = 0.10 + 0.26*self.persistence
            self.evidence[2] = np.clip(self.evidence[2] + signal, 0, 1)
            self.uncertainty *= 0.84
            investigation_gain = 0.15
            compute_cost = 0.08

        elif action == 4:  # correlate_identity
            signal = 0.08 + 0.18*self.threat
            self.evidence[3] = np.clip(self.evidence[3] + signal, 0, 1)
            self.uncertainty *= 0.89
            investigation_gain = 0.11
            compute_cost = 0.05

        elif action == 5:  # spawn specialist
            # More expensive, broad uncertainty reduction.
            self.evidence[4] = np.clip(
                self.evidence[4] + 0.10 + 0.20*self.threat, 0, 1
            )
            self.uncertainty *= 0.78
            investigation_gain = 0.18
            compute_cost = 0.14

        elif action == 6:  # contain
            # Effective when threat is real, harmful when unnecessary.
            effectiveness = 0.20 + 0.35*self.threat
            self.threat = float(np.clip(self.threat - effectiveness, 0, 1))
            self.persistence *= 0.78
            disruption_cost = 0.16 + 0.20*(1.0 - prev_threat)
            self.disruption = float(np.clip(self.disruption + disruption_cost, 0, 1))
            remediation_gain = prev_threat - self.threat
            compute_cost = 0.08

        elif action == 7:  # remediate
            # Stronger if enough evidence has been accumulated.
            evidence_strength = float(np.mean(self.evidence[:5]))
            success_prob = np.clip(
                0.20 + 0.55*evidence_strength + 0.20*(1-self.uncertainty),
                0.05,
                0.95,
            )
            if self.rng.random() < success_prob:
                reduction = 0.30 + 0.50*self.threat
                self.threat = float(np.clip(self.threat - reduction, 0, 1))
                self.persistence *= 0.45
                remediation_gain = prev_threat - self.threat
            else:
                self.threat = float(np.clip(self.threat + 0.04, 0, 1))

            disruption_cost = 0.10 + 0.25*(1.0-prev_threat)
            self.disruption = float(np.clip(self.disruption + disruption_cost, 0, 1))
            compute_cost = 0.12

        # Uncertainty slowly returns if the agent does nothing useful.
        self.uncertainty = float(np.clip(self.uncertainty + 0.008, 0.02, 1.0))

        # Evidence decays slightly over time.
        self.evidence *= 0.992

        # Reward components
        new_entropy = self.entropy_binary(np.clip(self.threat, 1e-5, 1 - 1e-5))
        info_gain = max(0.0, prev_entropy - new_entropy) + max(
            0.0, prev_uncertainty - self.uncertainty
        )

        risk_reduction = max(0.0, prev_threat - self.threat)
        unresolved_penalty = 0.40 * self.threat
        false_positive_penalty = (
            0.45 * disruption_cost if prev_threat < 0.30 else 0.0
        )

        reward = (
            2.2 * investigation_gain
            + 4.5 * remediation_gain
            + 2.5 * risk_reduction
            + 1.6 * info_gain
            - unresolved_penalty
            - 2.5 * false_positive_penalty
            - 1.5 * disruption_cost
            - compute_cost
        )

        done_success = self.threat < 0.06 and self.step_count >= 4
        done_timeout = self.step_count >= self.cfg.max_steps
        done = done_success or done_timeout

        if done_success:
            reward += 6.0
        elif done_timeout and self.threat > 0.40:
            reward -= 3.0

        info = {
            "threat": self.threat,
            "uncertainty": self.uncertainty,
            "risk_reduction": risk_reduction,
            "info_gain": info_gain,
            "disruption": self.disruption,
            "action_name": self.ACTION_NAMES[action],
            "success": done_success,
        }

        return self._observe(), float(reward), done, info

# Prioritized Replay Buffer

Transition = namedtuple(
    "Transition",
    ["state_seq", "action", "reward", "next_state_seq", "done"]
)


class PrioritizedReplayBuffer:
    def __init__(self, capacity: int, alpha: float):
        self.capacity = capacity
        self.alpha = alpha
        self.data: List[Transition] = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.pos = 0

    def __len__(self):
        return len(self.data)

    def add(self, transition: Transition):
        max_p = self.priorities[:len(self.data)].max() if self.data else 1.0

        if len(self.data) < self.capacity:
            self.data.append(transition)
        else:
            self.data[self.pos] = transition

        self.priorities[self.pos] = max_p
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size: int, beta: float):
        n = len(self.data)
        probs = self.priorities[:n] ** self.alpha
        probs = probs / probs.sum()

        idxs = np.random.choice(n, batch_size, p=probs, replace=False)
        samples = [self.data[i] for i in idxs]

        weights = (n * probs[idxs]) ** (-beta)
        weights /= weights.max()
        weights = torch.tensor(weights, dtype=torch.float32, device=DEVICE)

        return samples, idxs, weights

    def update_priorities(self, idxs, priorities):
        for idx, p in zip(idxs, priorities):
            self.priorities[idx] = float(p) + CFG.priority_eps

# N-step accumulator

class NStepAccumulator:
    def __init__(self, n_step: int, gamma: float):
        self.n_step = n_step
        self.gamma = gamma
        self.buffer: Deque = deque()

    def reset(self):
        self.buffer.clear()

    def append(self, state_seq, action, reward, next_state_seq, done):
        self.buffer.append((state_seq, action, reward, next_state_seq, done))
        out = []

        if len(self.buffer) >= self.n_step:
            out.append(self._build_transition())

        if done:
            while self.buffer:
                out.append(self._build_transition())

        return out

    def _build_transition(self):
        reward = 0.0
        next_state = self.buffer[0][3]
        done = False

        for i, (_, _, r, ns, d) in enumerate(self.buffer):
            if i >= self.n_step:
                break
            reward += (self.gamma ** i) * r
            next_state = ns
            done = d
            if d:
                break

        state, action = self.buffer[0][0], self.buffer[0][1]
        self.buffer.popleft()

        return Transition(state, action, reward, next_state, done)

# Model components

class FeatureGate(nn.Module):
    """
    Learns adaptive per-feature attention weights.
    """
    def __init__(self, obs_dim: int, hidden: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.GELU(),
            nn.Linear(hidden, obs_dim),
        )

    def forward(self, x):
        # x: [B, T, D]
        logits = self.net(x)
        gates = torch.softmax(logits, dim=-1) * x.size(-1)
        return x * gates, gates


class AgentRouter(nn.Module):
    """
    Attention-like routing over learned agent embeddings.
    """
    def __init__(self, state_dim: int, num_agents: int, agent_embed_dim: int):
        super().__init__()
        self.agent_embeddings = nn.Parameter(
            torch.randn(num_agents, agent_embed_dim) * 0.05
        )
        self.query = nn.Linear(state_dim, agent_embed_dim)
        self.temperature = nn.Parameter(torch.tensor(1.0))

    def forward(self, state):
        # state: [B, H]
        q = F.normalize(self.query(state), dim=-1)
        k = F.normalize(self.agent_embeddings, dim=-1)

        logits = q @ k.T
        logits = logits / torch.clamp(self.temperature.abs(), min=0.15)
        probs = torch.softmax(logits, dim=-1)

        routed = probs @ self.agent_embeddings
        return routed, probs


class AdaptiveAttentionQNet(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg

        self.feature_gate = FeatureGate(cfg.obs_dim, cfg.hidden_dim)

        self.input_proj = nn.Sequential(
            nn.Linear(cfg.obs_dim, cfg.hidden_dim),
            nn.LayerNorm(cfg.hidden_dim),
            nn.GELU(),
        )

        self.lstm = nn.LSTM(
            input_size=cfg.hidden_dim,
            hidden_size=cfg.hidden_dim,
            num_layers=2,
            dropout=0.10,
            batch_first=True,
        )

        self.self_attn = nn.MultiheadAttention(
            embed_dim=cfg.hidden_dim,
            num_heads=cfg.attn_heads,
            dropout=0.10,
            batch_first=True,
        )

        self.attn_norm = nn.LayerNorm(cfg.hidden_dim)

        self.temporal_score = nn.Sequential(
            nn.Linear(cfg.hidden_dim, cfg.hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(cfg.hidden_dim // 2, 1),
        )

        self.agent_router = AgentRouter(
            cfg.hidden_dim,
            cfg.num_agents,
            cfg.agent_embed_dim,
        )

        fusion_dim = cfg.hidden_dim + cfg.agent_embed_dim

        self.fusion = nn.Sequential(
            nn.Linear(fusion_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Dropout(0.10),
            nn.Linear(256, 192),
            nn.GELU(),
        )

        self.value_head = nn.Sequential(
            nn.Linear(192, 128),
            nn.GELU(),
            nn.Linear(128, 1),
        )

        self.adv_head = nn.Sequential(
            nn.Linear(192, 128),
            nn.GELU(),
            nn.Linear(128, cfg.num_actions),
        )

        # Auxiliary risk prediction encourages useful latent representations.
        self.risk_head = nn.Sequential(
            nn.Linear(192, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        # x: [B,T,D]
        gated, feature_weights = self.feature_gate(x)
        h = self.input_proj(gated)
        h, _ = self.lstm(h)

        attn_out, attn_matrix = self.self_attn(
            h, h, h,
            need_weights=True,
            average_attn_weights=False
        )
        h = self.attn_norm(h + attn_out)

        # Learned temporal attention pooling
        time_logits = self.temporal_score(h).squeeze(-1)
        time_weights = torch.softmax(time_logits, dim=-1)
        pooled = torch.sum(h * time_weights.unsqueeze(-1), dim=1)

        routed, agent_probs = self.agent_router(pooled)
        z = self.fusion(torch.cat([pooled, routed], dim=-1))

        value = self.value_head(z)
        advantage = self.adv_head(z)
        q = value + advantage - advantage.mean(dim=1, keepdim=True)

        risk = self.risk_head(z)

        aux = {
            "risk": risk,
            "feature_weights": feature_weights,
            "time_weights": time_weights,
            "agent_probs": agent_probs,
            "attn_matrix": attn_matrix,
        }
        return q, aux

# Utility functions

def make_sequence(history: Deque[np.ndarray], cfg: Config) -> np.ndarray:
    items = list(history)
    if len(items) < cfg.seq_len:
        pad = [np.zeros(cfg.obs_dim, dtype=np.float32)] * (cfg.seq_len - len(items))
        items = pad + items
    else:
        items = items[-cfg.seq_len:]
    return np.stack(items).astype(np.float32)


def epsilon_by_step(step: int, cfg: Config) -> float:
    frac = min(1.0, step / cfg.eps_decay_steps)
    return cfg.eps_start + frac * (cfg.eps_end - cfg.eps_start)


def beta_by_step(step: int, cfg: Config) -> float:
    frac = min(1.0, step / cfg.per_beta_frames)
    return cfg.per_beta_start + frac * (cfg.per_beta_end - cfg.per_beta_start)


@torch.no_grad()
def select_action(
    net: nn.Module,
    state_seq: np.ndarray,
    epsilon: float,
    cfg: Config,
):
    if random.random() < epsilon:
        return random.randrange(cfg.num_actions), None

    x = torch.tensor(state_seq, dtype=torch.float32, device=DEVICE).unsqueeze(0)
    q, aux = net(x)
    action = int(q.argmax(dim=1).item())
    return action, aux


def soft_update(target: nn.Module, online: nn.Module, tau: float):
    with torch.no_grad():
        for tp, op in zip(target.parameters(), online.parameters()):
            tp.data.mul_(1.0 - tau).add_(op.data, alpha=tau)



# Training step

def train_batch(
    online: AdaptiveAttentionQNet,
    target: AdaptiveAttentionQNet,
    optimizer: torch.optim.Optimizer,
    replay: PrioritizedReplayBuffer,
    beta: float,
    cfg: Config,
):
    samples, idxs, is_weights = replay.sample(cfg.batch_size, beta)

    states = torch.tensor(
        np.stack([s.state_seq for s in samples]),
        dtype=torch.float32,
        device=DEVICE,
    )
    actions = torch.tensor(
        [s.action for s in samples],
        dtype=torch.long,
        device=DEVICE,
    ).unsqueeze(1)
    rewards = torch.tensor(
        [s.reward for s in samples],
        dtype=torch.float32,
        device=DEVICE,
    ).unsqueeze(1)
    next_states = torch.tensor(
        np.stack([s.next_state_seq for s in samples]),
        dtype=torch.float32,
        device=DEVICE,
    )
    dones = torch.tensor(
        [s.done for s in samples],
        dtype=torch.float32,
        device=DEVICE,
    ).unsqueeze(1)

    q, aux = online(states)
    q_sa = q.gather(1, actions)

    with torch.no_grad():
        # Double DQN:
        # online chooses next action, target evaluates it.
        next_q_online, _ = online(next_states)
        next_actions = next_q_online.argmax(dim=1, keepdim=True)

        next_q_target, _ = target(next_states)
        next_q = next_q_target.gather(1, next_actions)

        gamma_n = cfg.gamma ** cfg.n_step
        td_target = rewards + (1.0 - dones) * gamma_n * next_q

    td_error = td_target - q_sa

    # PER-weighted Huber loss
    rl_loss = (
        is_weights.unsqueeze(1)
        * F.smooth_l1_loss(q_sa, td_target, reduction="none")
    ).mean()

    # Auxiliary risk supervision:
    # first telemetry feature is a noisy risk proxy, so use last observation.
    risk_target = states[:, -1, 0].clamp(0, 1).unsqueeze(1)
    risk_loss = F.mse_loss(aux["risk"], risk_target)

    # Small entropy regularizer encourages non-degenerate agent routing.
    agent_probs = aux["agent_probs"].clamp_min(1e-8)
    routing_entropy = -(agent_probs * agent_probs.log()).sum(dim=1).mean()

    loss = rl_loss + 0.15 * risk_loss - 0.002 * routing_entropy

    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    nn.utils.clip_grad_norm_(online.parameters(), cfg.grad_clip)
    optimizer.step()

    priorities = td_error.detach().abs().squeeze(1).cpu().numpy()
    replay.update_priorities(idxs, priorities)

    return {
        "loss": float(loss.item()),
        "rl_loss": float(rl_loss.item()),
        "risk_loss": float(risk_loss.item()),
        "routing_entropy": float(routing_entropy.item()),
        "mean_abs_td": float(np.mean(priorities)),
    }

# Evaluation

@torch.no_grad()
def evaluate(net: AdaptiveAttentionQNet, cfg: Config, episodes: int = 5):
    net.eval()
    env = AdaptiveInvestigationEnv(cfg)

    rewards = []
    successes = 0
    final_risks = []

    for _ in range(episodes):
        obs = env.reset()
        history = deque([obs], maxlen=cfg.seq_len)
        total = 0.0
        done = False

        while not done:
            seq = make_sequence(history, cfg)
            action, _ = select_action(net, seq, epsilon=0.0, cfg=cfg)
            next_obs, reward, done, info = env.step(action)
            history.append(next_obs)
            total += reward

        rewards.append(total)
        successes += int(info["success"])
        final_risks.append(info["threat"])

    net.train()

    return {
        "reward": float(np.mean(rewards)),
        "success_rate": successes / episodes,
        "final_risk": float(np.mean(final_risks)),
    }



# Main training loop

def main():
    print(f"Device: {DEVICE}")
    print("Architecture: LSTM + Multihead Attention + Feature Attention + Agent Router")
    print("RL: Dueling Double DQN + PER + N-step returns + soft target updates\n")

    env = AdaptiveInvestigationEnv(CFG)

    online = AdaptiveAttentionQNet(CFG).to(DEVICE)
    target = AdaptiveAttentionQNet(CFG).to(DEVICE)
    target.load_state_dict(online.state_dict())
    target.eval()

    optimizer = torch.optim.AdamW(
        online.parameters(),
        lr=CFG.lr,
        weight_decay=CFG.weight_decay,
    )

    replay = PrioritizedReplayBuffer(CFG.replay_capacity, CFG.per_alpha)
    nstep = NStepAccumulator(CFG.n_step, CFG.gamma)

    global_step = 0
    recent_returns = deque(maxlen=20)
    recent_success = deque(maxlen=20)

    for episode in range(1, CFG.episodes + 1):
        obs = env.reset()
        history = deque([obs], maxlen=CFG.seq_len)
        nstep.reset()

        ep_return = 0.0
        done = False
        last_info = None
        train_stats = None

        while not done:
            state_seq = make_sequence(history, CFG)
            eps = epsilon_by_step(global_step, CFG)

            action, _ = select_action(
                online,
                state_seq,
                epsilon=eps,
                cfg=CFG,
            )

            next_obs, reward, done, info = env.step(action)
            history.append(next_obs)
            next_state_seq = make_sequence(history, CFG)

            transitions = nstep.append(
                state_seq,
                action,
                reward,
                next_state_seq,
                done,
            )

            for tr in transitions:
                replay.add(tr)

            ep_return += reward
            last_info = info
            global_step += 1

            if (
                len(replay) >= max(CFG.warmup_steps, CFG.batch_size)
                and global_step % CFG.train_every == 0
            ):
                for _ in range(CFG.updates_per_step):
                    beta = beta_by_step(global_step, CFG)
                    train_stats = train_batch(
                        online,
                        target,
                        optimizer,
                        replay,
                        beta,
                        CFG,
                    )
                    soft_update(target, online, CFG.tau)

        recent_returns.append(ep_return)
        recent_success.append(int(last_info["success"]))

        if episode % 5 == 0:
            stat_text = ""
            if train_stats:
                stat_text = (
                    f" loss={train_stats['loss']:.4f}"
                    f" td={train_stats['mean_abs_td']:.4f}"
                )

            print(
                f"ep={episode:03d}"
                f" step={global_step:05d}"
                f" return20={np.mean(recent_returns):7.2f}"
                f" success20={np.mean(recent_success):.2f}"
                f" eps={epsilon_by_step(global_step, CFG):.3f}"
                f" risk={last_info['threat']:.3f}"
                f"{stat_text}"
            )

        if episode % CFG.eval_every == 0:
            metrics = evaluate(
                online,
                CFG,
                episodes=CFG.eval_episodes,
            )
            print(
                "  EVAL"
                f" reward={metrics['reward']:.2f}"
                f" success={metrics['success_rate']:.2%}"
                f" final_risk={metrics['final_risk']:.3f}"
            )

    # Final interpretability probe
    print("\n--- Interpretability probe ---")
    online.eval()

    obs = env.reset()
    history = deque([obs], maxlen=CFG.seq_len)

    for _ in range(5):
        seq = make_sequence(history, CFG)
        x = torch.tensor(seq, dtype=torch.float32, device=DEVICE).unsqueeze(0)

        with torch.no_grad():
            q, aux = online(x)

        action = int(q.argmax(dim=1).item())
        agent_probs = aux["agent_probs"][0].cpu().numpy()
        time_weights = aux["time_weights"][0].cpu().numpy()
        feature_weights = aux["feature_weights"][0, -1].cpu().numpy()

        top_agents = np.argsort(agent_probs)[::-1][:3]
        top_features = np.argsort(feature_weights)[::-1][:5]

        print(f"\nSelected action: {env.ACTION_NAMES[action]}")
        print("Q-values:", np.round(q[0].cpu().numpy(), 3))
        print(
            "Top agent routes:",
            [(int(i), round(float(agent_probs[i]), 3)) for i in top_agents],
        )
        print(
            "Top temporal weights:",
            np.round(time_weights[-5:], 3),
        )
        print(
            "Top feature gates:",
            [(int(i), round(float(feature_weights[i]), 3)) for i in top_features],
        )

        next_obs, reward, done, info = env.step(action)
        history.append(next_obs)

        print(
            f"reward={reward:.3f}"
            f" threat={info['threat']:.3f}"
            f" uncertainty={info['uncertainty']:.3f}"
        )

        if done:
            break

    model_path = "aahm_q_model.pt"
    torch.save(online.state_dict(), model_path)
    print(f"\nSaved model to: {model_path}")


if __name__ == "__main__":
    main()

"""
OUTPUT:
Device: mps
Architecture: LSTM + Multihead Attention + Feature Attention + Agent Router
RL: Dueling Double DQN + PER + N-step returns + soft target updates

ep=005 step=00050 return20=  11.60 success20=1.00 eps=0.998 risk=0.000
ep=010 step=00151 return20=  11.57 success20=1.00 eps=0.993 risk=0.000
ep=015 step=00201 return20=  11.52 success20=1.00 eps=0.990 risk=0.000
ep=020 step=00247 return20=  11.53 success20=1.00 eps=0.988 risk=0.000
  EVAL reward=-12.66 success=0.00% final_risk=0.995
ep=025 step=00295 return20=  11.24 success20=1.00 eps=0.986 risk=0.000
ep=030 step=00372 return20=  11.53 success20=1.00 eps=0.982 risk=0.000
ep=035 step=00405 return20=  11.24 success20=1.00 eps=0.981 risk=0.056
ep=040 step=00451 return20=  11.25 success20=1.00 eps=0.978 risk=0.000
  EVAL reward=-12.66 success=0.00% final_risk=0.995
ep=045 step=00484 return20=  11.08 success20=1.00 eps=0.977 risk=0.015
ep=050 step=00524 return20=  10.73 success20=1.00 eps=0.975 risk=0.000
ep=055 step=00565 return20=  10.95 success20=1.00 eps=0.973 risk=0.000
ep=060 step=00620 return20=  10.78 success20=1.00 eps=0.970 risk=0.000
  EVAL reward=-12.66 success=0.00% final_risk=0.995
ep=065 step=00657 return20=  10.96 success20=1.00 eps=0.968 risk=0.000
ep=070 step=00706 return20=  10.89 success20=1.00 eps=0.966 risk=0.000
ep=075 step=00779 return20=  10.92 success20=1.00 eps=0.963 risk=0.000
ep=080 step=00837 return20=  10.90 success20=1.00 eps=0.960 risk=0.000
  EVAL reward=-12.66 success=0.00% final_risk=0.995
ep=085 step=00880 return20=  11.01 success20=1.00 eps=0.958 risk=0.000
ep=090 step=00921 return20=  11.06 success20=1.00 eps=0.956 risk=0.000
ep=095 step=00981 return20=  10.85 success20=1.00 eps=0.953 risk=0.000
ep=100 step=01033 return20=  11.07 success20=1.00 eps=0.950 risk=0.000 loss=1.0321 td=3.6124
  EVAL reward=6.21 success=100.00% final_risk=0.000
ep=105 step=01074 return20=  11.21 success20=1.00 eps=0.948 risk=0.000 loss=1.0176 td=3.2833
ep=110 step=01140 return20=  11.38 success20=1.00 eps=0.945 risk=0.000 loss=0.5852 td=2.1667
ep=115 step=01179 return20=  11.43 success20=1.00 eps=0.943 risk=0.041 loss=0.5503 td=1.7919
ep=120 step=01216 return20=  11.01 success20=1.00 eps=0.942 risk=0.000 loss=0.7141 td=2.0950
  EVAL reward=6.21 success=100.00% final_risk=0.000
ep=125 step=01263 return20=  11.21 success20=1.00 eps=0.939 risk=0.000 loss=0.3972 td=1.7673
ep=130 step=01320 return20=  11.21 success20=1.00 eps=0.937 risk=0.000 loss=0.4271 td=1.5735
ep=135 step=01349 return20=  11.05 success20=1.00 eps=0.935 risk=0.000 loss=0.2859 td=1.3663
ep=140 step=01411 return20=  11.21 success20=1.00 eps=0.932 risk=0.000 loss=0.2526 td=1.2153
  EVAL reward=9.62 success=100.00% final_risk=0.004
ep=145 step=01494 return20=  11.23 success20=1.00 eps=0.928 risk=0.000 loss=0.1344 td=0.9548
ep=150 step=01561 return20=  10.80 success20=1.00 eps=0.925 risk=0.000 loss=0.1187 td=0.8130
ep=155 step=01625 return20=  11.25 success20=1.00 eps=0.922 risk=0.000 loss=0.0502 td=0.8002
ep=160 step=01671 return20=  11.27 success20=1.00 eps=0.920 risk=0.024 loss=0.1044 td=0.6685
  EVAL reward=18.66 success=100.00% final_risk=0.012
ep=165 step=01725 return20=  11.12 success20=1.00 eps=0.917 risk=0.006 loss=0.1354 td=0.7128
ep=170 step=01786 return20=  11.74 success20=1.00 eps=0.914 risk=0.007 loss=0.0674 td=0.6586
ep=175 step=01827 return20=  11.47 success20=1.00 eps=0.912 risk=0.000 loss=0.0818 td=0.6894
ep=180 step=01873 return20=  11.43 success20=1.00 eps=0.910 risk=0.012 loss=0.0542 td=0.5827
  EVAL reward=13.18 success=87.50% final_risk=0.083
ep=185 step=01924 return20=  11.55 success20=1.00 eps=0.908 risk=0.000 loss=0.0836 td=0.5915
ep=190 step=01989 return20=  11.43 success20=1.00 eps=0.905 risk=0.000 loss=0.0880 td=0.6202
ep=195 step=02021 return20=  11.46 success20=1.00 eps=0.903 risk=0.000 loss=0.0759 td=0.6396
ep=200 step=02083 return20=  11.70 success20=1.00 eps=0.900 risk=0.054 loss=0.0651 td=0.5997
  EVAL reward=18.58 success=100.00% final_risk=0.014
ep=205 step=02152 return20=  11.76 success20=1.00 eps=0.897 risk=0.000 loss=0.0407 td=0.6030
ep=210 step=02229 return20=  11.55 success20=1.00 eps=0.893 risk=0.000 loss=0.0622 td=0.6397
ep=215 step=02280 return20=  11.87 success20=1.00 eps=0.891 risk=0.000 loss=0.0828 td=0.5556
ep=220 step=02319 return20=  11.59 success20=1.00 eps=0.889 risk=0.000 loss=0.0693 td=0.5510
  EVAL reward=18.48 success=62.50% final_risk=0.168

--- Interpretability probe ---

Selected action: inspect_memory
Q-values: [9.448 9.67  9.571 9.723 9.515 9.599 9.435 9.13 ]
Top agent routes: [(0, 0.17), (1, 0.168), (5, 0.168)]
Top temporal weights: [0.002 0.002 0.002 0.002 0.982]
Top feature gates: [(16, 1.494), (5, 1.259), (2, 1.251), (18, 1.239), (12, 1.176)]
reward=0.175 threat=0.523 uncertainty=0.486

Selected action: inspect_memory
Q-values: [ 9.764 10.042  9.894 10.081  9.927  9.943  9.823  9.648]
Top agent routes: [(3, 0.168), (5, 0.168), (4, 0.168)]
Top temporal weights: [0.    0.001 0.001 0.184 0.812]
Top feature gates: [(16, 1.44), (1, 1.254), (12, 1.249), (14, 1.232), (2, 1.208)]
reward=0.148 threat=0.547 uncertainty=0.416

Selected action: inspect_memory
Q-values: [ 9.903 10.22  10.051 10.249 10.129 10.117 10.021  9.936]
Top agent routes: [(4, 0.172), (3, 0.169), (5, 0.167)]
Top temporal weights: [0.    0.    0.058 0.291 0.649]
Top feature gates: [(16, 1.451), (1, 1.318), (12, 1.237), (2, 1.229), (14, 1.226)]
reward=0.127 threat=0.594 uncertainty=0.357

Selected action: inspect_memory
Q-values: [10.11  10.446 10.271 10.472 10.361 10.356 10.311 10.266]
Top agent routes: [(4, 0.175), (3, 0.168), (1, 0.166)]
Top temporal weights: [0.    0.026 0.148 0.358 0.466]
Top feature gates: [(16, 1.429), (1, 1.4), (2, 1.275), (12, 1.261), (14, 1.238)]
reward=0.099 threat=0.620 uncertainty=0.308

Selected action: inspect_memory
Q-values: [10.204 10.549 10.376 10.574 10.461 10.472 10.464 10.434]
Top agent routes: [(4, 0.177), (3, 0.168), (1, 0.166)]
Top temporal weights: [0.014 0.088 0.231 0.314 0.352]
Top feature gates: [(16, 1.398), (1, 1.379), (2, 1.262), (14, 1.24), (12, 1.211)]
reward=0.071 threat=0.619 uncertainty=0.267
"""
