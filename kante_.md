# Go2 학습·정책 설정 메모

현재 사용한 `Unitree-Go2-Flat` 기준. 경로는 프로젝트 루트(`/home/lee/unitree_rl_mjlab`) 기준이다.

## 1. 학습과 실행 명령

설치 및 동작 확인용 학습:

```bash
python scripts/train.py Unitree-Go2-Flat \
  --env.scene.num-envs 64 \
  --agent.max-iterations 20 \
  --agent.run-name setup_test \
  --agent.logger tensorboard
```

본 학습용 명령:

```bash
python scripts/train.py Unitree-Go2-Flat \
  --env.scene.num-envs 1024 \
  --agent.max-iterations 10001 \
  --agent.run-name go2_flat_baseline \
  --agent.logger tensorboard
```

학습 및 학습 장면 기록 명령어



저장된 체크포인트 확인:

```bash
find logs/rsl_rl/go2_velocity -path '*setup_test*' -name 'model_*.pt' | sort -V
```

학습한 모델 실행:

```bash
python scripts/play.py Unitree-Go2-Flat \
  --checkpoint-file "logs/rsl_rl/go2_velocity/2026-09-24_15-22-47_setup_test/model_19.pt" \
  --num-envs 1 \
  --device cuda:0 \
  --viewer native
```

## 2. 정책이란?

정책(actor)은 관측값을 입력받아 행동을 출력하는 신경망이다. 여기서는 로봇 자세, 관절 상태, 속도 명령 등을 받아 관절 목표 위치를 결정한다. Critic은 학습 중 상태의 가치를 추정한다.

- 사람이 설정하는 것: 신경망 구조, 학습률, 보상, 관측, 행동, 환경.
- 학습으로 만들어지는 것: 정책 신경망의 가중치. `model_*.pt` 체크포인트에 저장된다.
- 원하는 걷는 방식을 바꾸려면 보상·환경을, 학습 방법을 바꾸려면 PPO 설정을 살펴본다.

## 3. 설정 파일 위치와 적용 순서

| 설정 대상 | 파일 | 주요 항목 |
|---|---|---|
| 정책·가치 신경망, PPO, 반복 횟수 | [go2/rl_cfg.py](src/tasks/velocity/config/go2/rl_cfg.py) | `actor`, `critic`, `algorithm`, `max_iterations` |
| 공통 관측·행동·명령·보상·환경 | [velocity_env_cfg.py](src/tasks/velocity/velocity_env_cfg.py) | `observations`, `actions`, `commands`, `rewards`, `events`, `terminations`, `curriculum` |
| Go2 전용 설정과 평지 설정 | [go2/env_cfgs.py](src/tasks/velocity/config/go2/env_cfgs.py) | 자세 허용 범위, 보행 위상, 접촉 종료 조건, 지형 |
| 태스크와 설정 연결 | [go2/__init__.py](src/tasks/velocity/config/go2/__init__.py) | `Unitree-Go2-Flat`, `Unitree-Go2-Rough` 등록 |
| 학습 시작 및 설정 저장 | [train.py](scripts/train.py) | 태스크 설정 로드, CLI 반영, `runner.learn()` |
| 체크포인트와 ONNX 저장 | [runner.py](src/tasks/velocity/rl/runner.py) | `VelocityOnPolicyRunner.save()` |
| 보상 계산 구현 | [rewards.py](src/tasks/velocity/mdp/rewards.py) | 보상 함수의 실제 계산식 |

평지 환경은 아래 순서로 만들어진다.

```text
make_velocity_env_cfg()           공통 기본값
  → unitree_go2_rough_env_cfg()    Go2 전용 값 적용
  → unitree_go2_flat_env_cfg()     평지 적용, 지형 스캔 제거
  → 학습 명령의 CLI 옵션 적용
```

공통 파일을 바꾸면 이를 사용하는 다른 로봇에도 영향을 준다. Go2만 바꾸려면 `go2/env_cfgs.py`에서 `cfg` 값을 덮어쓴다. 평지에만 적용하려면 `unitree_go2_flat_env_cfg()`의 `return cfg` 전에 작성한다.

`if play:` 내부는 실행 모드 전용이다. 학습에 반영할 설정은 이 조건 밖에 둔다. G1 등 다른 로봇은 해당 `config/<로봇>/` 폴더를 확인하고, 모션 추종 태스크는 `src/tasks/tracking/`을 확인한다.

## 4. 신경망과 PPO 설정

`src/tasks/velocity/config/go2/rl_cfg.py`의 현재 기본값:

| 항목 | 값 | 의미 |
|---|---|---|
| `actor.hidden_dims` | `(512, 256, 128)` | 행동을 결정하는 신경망의 은닉층 크기 |
| `critic.hidden_dims` | `(512, 256, 128)` | 가치 추정 신경망의 은닉층 크기 |
| `activation` | `elu` | 활성화 함수 |
| `obs_normalization` | `True` | 관측값 정규화 |
| `actor.distribution_cfg.init_std` | `1.0` | 학습 중 행동 분포의 초기 표준편차 |
| `algorithm.learning_rate` | `0.001` | 초기 학습률 |
| `algorithm.schedule` | `adaptive` | 학습률 적응 조정 |
| `algorithm.entropy_coef` | `0.01` | 탐색을 유도하는 엔트로피 항의 계수 |
| `algorithm.clip_param` | `0.2` | PPO 정책 갱신의 클리핑 범위 |
| `algorithm.gamma` | `0.99` | 미래 보상 할인율 |
| `algorithm.lam` | `0.95` | GAE 이점 추정 계수 |
| `algorithm.num_learning_epochs` | `5` | 수집한 데이터에 대한 학습 반복 수 |
| `algorithm.num_mini_batches` | `4` | 데이터를 나누는 미니배치 수 |
| `num_steps_per_env` | `24` | 한 학습 반복마다 환경별로 수집하는 스텝 수 |
| `max_iterations` | `10001` | 학습 반복 횟수 |
| `save_interval` | `100` | 체크포인트 저장 간격(학습 반복 기준) |
| `experiment_name` | `go2_velocity` | 로그 폴더 이름 |

명령행에서 지정한 값은 기본값을 덮어쓴다. 예를 들어 기존 `setup_test`는 `--agent.max-iterations 20`을 사용했으므로 실제 반복 횟수 설정은 20이다. 당시 실제 설정은 해당 실행 폴더의 `params/agent.yaml`에서 확인한다.

## 5. 관측·행동·속도 명령

공통 설정 파일 `velocity_env_cfg.py`에서 확인한다.

- **관측 (`actor_terms`, `observations`)**: 몸체 각속도, 중력 방향, 속도 명령, 보행 위상, 관절 위치·속도, 이전 행동 등. Go2 평지에서는 `height_scan`을 제거한다. Critic에는 선속도와 발 접촉 등 추가 정보가 들어간다.
- **행동 (`actions["joint_pos"]`)**: `JointPositionActionCfg`로 관절 목표 위치를 제어한다. Go2는 공통 `scale=0.25`, `use_default_offset=True`를 사용한다. 출력에 스케일을 적용하고 기본 관절 위치를 더한다.
- **속도 명령 (`commands["twist"]`)**: 목표 전후·좌우 속도와 회전 속도를 설정한다. 기본 범위는 `lin_vel_x=(-1.0, 2.0)`, `lin_vel_y=(-1.0, 1.0)`, `ang_vel_z=(-1.0, 1.0)`이다. 선속도 단위는 m/s, 각속도는 rad/s이다.
- **명령 커리큘럼 (`curriculum["command_vel"]`)**: 학습 단계에 따라 속도 범위를 바꾼다. 초기 단계는 전후 `(-0.5, 1.0)`, 좌우 `(-0.5, 0.5)`이고, 다음 단계는 `step=5000 * 24`에 지정되어 있다. 학습 속도 범위를 바꿀 때 `commands`와 커리큘럼을 함께 확인한다.
- **실행 모드 속도**: `go2/env_cfgs.py`의 평지 함수 안 `if play:`에서 전후 `(-0.5, 1.0)`, 좌우 `(-0.5, 0.5)`, 회전 `(-0.5, 0.5)`로 설정한다.

## 6. 보상과 원하는 행동 조정

공통 `rewards`에서 보상 항목과 `weight`, 함수 파라미터를 설정한다. Go2 전용 파일에서는 관절별 자세 허용 범위와 보행 위상 등을 추가로 지정한다.

| 항목 | 현재 weight | 관련 행동 |
|---|---:|---|
| `track_linear_velocity` | `1.0` | 목표 선속도 추종 |
| `track_angular_velocity` | `1.0` | 목표 회전 속도 추종 |
| `body_orientation_l2` | `-1.0` | 몸체 기울어짐 억제 |
| `pose` | `1.0` | 기준 자세 유지, 정지·보행·달리기별 허용 범위 |
| `action_rate_l2` | `-0.05` | 행동의 급격한 변화 억제 |
| `joint_pos_limits` | `-10.0` | 관절 위치 한계 위반 억제 |
| `is_terminated` | `-200.0` | 실패 종료에 대한 페널티 |
| `foot_gait` | `0.5` | 발 접촉 타이밍과 보행 위상 |
| `foot_clearance` | `-1.0` | 발 높이 관련 비용, `target_height=0.10` |
| `foot_slip` | `-0.25` | 발 미끄러짐 억제 |

Go2의 `foot_gait` 위상 오프셋은 `[0.0, 0.5, 0.5, 0.0]`이다. 보상은 여러 항목이 함께 작용하므로 한 값을 바꿨다고 특정 동작이 보장되지는 않는다. 정확한 의미는 연결된 보상 함수의 계산식을 함께 확인한다.

예: Go2 평지에서만 발 높이 목표와 행동 변화 페널티를 바꾸려면 `unitree_go2_flat_env_cfg()`의 `return cfg` 앞에 다음과 같이 추가한다. 아래는 수정 예시이며 현재 코드에 적용한 값은 아니다.

```python
cfg.rewards["foot_clearance"].params["target_height"] = 0.12
cfg.rewards["action_rate_l2"].weight = -0.1
```

그 밖에 `events`는 마찰·질량 중심 등의 무작위화와 외력, `terminations`는 넘어짐·접촉 등의 종료 조건, `curriculum`은 난이도 변화를 설정한다. 이것들도 학습되는 행동에 영향을 준다.

## 7. 모델 가중치와 실제 사용한 설정 저장 위치

기본 저장 구조:

```text
logs/rsl_rl/<experiment_name>/<날짜_시간>[_<run_name>]/
├── model_<반복번호>.pt   학습 체크포인트
├── policy.onnx          추론용으로 내보낸 정책
└── params/
    ├── agent.yaml       실제 학습에 사용한 신경망·PPO 설정
    └── env.yaml         실제 학습에 사용한 환경·보상·관측 설정
```

2026-09-24 확인한 기존 실행 폴더:

```text
/home/lee/unitree_rl_mjlab/logs/rsl_rl/go2_velocity/2026-09-24_15-22-47_setup_test/
```

이 폴더에는 `model_0.pt`, `model_19.pt`, `policy.onnx`가 있다. 현재 확인된 체크포인트 중 반복 번호가 가장 큰 파일은 [model_19.pt](logs/rsl_rl/go2_velocity/2026-09-24_15-22-47_setup_test/model_19.pt)이다.

`VelocityOnPolicyRunner.save()`는 체크포인트를 저장할 때 `policy.onnx`도 내보낸다. ONNX 파일명은 고정되어 있어 같은 실행 폴더에서 다음 저장 시 갱신된다.

설정 파일을 수정해도 기존 체크포인트의 가중치는 바뀌지 않는다. 변경한 보상이나 학습 목표를 반영하려면 새로 학습하거나 호환되는 체크포인트에서 이어서 학습해야 한다. 관측 차원이나 신경망 구조를 바꾸면 기존 가중치를 그대로 불러오지 못할 수 있다.

`params/*.yaml`은 당시 설정을 기록한 파일이다. 다음 학습의 기본값을 바꾸려면 소스 설정 또는 CLI 옵션을 수정한다.
