import cv2
import click
import logging
from pathlib import Path
import modern_robotics as mr
from src.envs import UnfoldCloth
from robosuite.utils.input_utils import *
from robosuite.controllers import load_controller_config
from dm_robotics.transformations import transformations as tr


def grasp_imp(env, state):
    for i in range(10):
        env.step([0, 0, 0, 0, 0, 0, state])
        env.render()


def grasp(env):
    grasp_imp(env, 1)


def ungrasp(env):
    grasp_imp(env, -1)


@click.command()
@click.option('--cloth', is_flag=True, help="include cloth in sim")
@click.option('--n', default=1, show_default=True, help="number of simulation runs")
@click.option('--debug', is_flag=True, default=False, show_default=True, help="debug logging")
def main(cloth, n, debug):

    if debug:
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(format='%(asctime)s - %(message)s', level=log_level)

    # Create dict to hold options that will be passed to env creation call
    options = {
        "robots": "Panda",
        "env_name": UnfoldCloth.__name__.split(".")[-1],
        "asset_path": str((Path(__file__).parent / "assets").resolve())
    }

    # Choose controller
    controller_name = "OSC_POSE"

    controller_config = load_controller_config(default_controller=controller_name)
    # controller_config['uncouple_pos_ori'] = True

    # Load the desired controller
    options["controller_configs"] = controller_config

    # initialize the task
    env = suite.make(
        **options,
        has_renderer=True,
        has_offscreen_renderer=True,
        ignore_done=True,
        use_camera_obs=False,
        control_freq=10,
        include_cloth=cloth,
        logger=logging.getLogger(__name__)
    )

    for _ in range(n):

        initial_state = env.reset()
        env.viewer.set_camera(camera_id=0)

        if cloth:
            pick_object_pose = tr.pos_quat_to_hmat(initial_state['cloth_pos'], initial_state['cloth_quat'])
            pick_object_pose = tr.pos_quat_to_hmat(initial_state['cube_pos'], initial_state['cube_quat'])
        else:
            pick_object_pose = tr.pos_quat_to_hmat(initial_state['cube_pos'], initial_state['cube_quat'])

        eef_pose = tr.pos_quat_to_hmat(initial_state['robot0_eef_pos'], initial_state['robot0_eef_quat'])

        last_obs = env.pick_manipulation(pick_object_pose, eef_pose)

        logging.debug(
            f"eef_axis: {tr.quat_axis(last_obs['robot0_eef_quat'])} : eef_angle: {np.rad2deg(tr.quat_angle(last_obs['robot0_eef_quat']))}")
        if cloth:
            logging.debug(f"cloth_pos: {last_obs['cloth_pos']} eef_pos: {last_obs['robot0_eef_pos']}")
        else:
            logging.debug(f"cube_pos: {last_obs['cube_pos']} eef_pos: {last_obs['robot0_eef_pos']}")

        grasp(env)
        cv2.waitKey(1000)

    env.close()


if __name__ == "__main__":
    main()
