"""Register the assembled Go2 flat and rough tasks with mjlab."""

from mjlab.tasks.registry import register_mjlab_task
from .step_03_training.runner import VelocityOnPolicyRunner

from .step_01_environment.go2_env import (
  unitree_go2_flat_env_cfg,
  unitree_go2_rough_env_cfg,
)
from .step_03_training.ppo import unitree_go2_ppo_runner_cfg

register_mjlab_task(
  task_id="Unitree-Go2-Rough",
  env_cfg=unitree_go2_rough_env_cfg(),
  play_env_cfg=unitree_go2_rough_env_cfg(play=True),
  rl_cfg=unitree_go2_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)

register_mjlab_task(
  task_id="Unitree-Go2-Flat",
  env_cfg=unitree_go2_flat_env_cfg(),
  play_env_cfg=unitree_go2_flat_env_cfg(play=True),
  rl_cfg=unitree_go2_ppo_runner_cfg(),
  runner_cls=VelocityOnPolicyRunner,
)
