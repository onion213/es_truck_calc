import math

from .classes import FormValue, CalcResult

from .constants import (
    SENSOR_SIZE,
    DUPLICATED_ANGLE,
    MAX_RESOL_DIFF,
    ROI_HEIGHT,
    ROI_WIDTH,
    CAM_MOUNT_SIZE,
)


def calc(form_value: FormValue) -> CalcResult:
    # break down form value
    cam_stand_to_ground = form_value.cam_stand_to_ground
    cam_stand_center_to_roi_head = form_value.cam_stand_center_to_roi_head
    roi_head_to_tail = form_value.roi_head_to_tail
    roi_tail_to_rear_wall = form_value.roi_tail_to_rear_wall

    # include mount size in calculation
    cam_to_ground = cam_stand_to_ground - CAM_MOUNT_SIZE["height"]
    cam_to_roi_head = cam_stand_center_to_roi_head - CAM_MOUNT_SIZE["depth"]

    # calculate white line
    ## head
    cam_to_white_line_head = (
        cam_to_roi_head * cam_to_ground / (cam_to_ground - ROI_HEIGHT["top"])
    )
    cam_stand_center_to_white_line_head = (
        cam_to_white_line_head + CAM_MOUNT_SIZE["depth"]
    )
    white_line_head_width = (
        ROI_WIDTH * cam_to_ground / (cam_to_ground - ROI_HEIGHT["top"])
    )

    ## tail
    cam_to_white_line_tail = (
        (cam_to_roi_head + roi_head_to_tail)
        * cam_to_ground
        / (cam_to_ground - ROI_HEIGHT["top"])
    )
    white_line_head_to_tail = cam_to_white_line_tail - cam_to_white_line_head
    if (
        cam_stand_center_to_white_line_head + white_line_head_to_tail
        > cam_stand_center_to_roi_head + roi_head_to_tail + roi_tail_to_rear_wall
    ):
        residual_length = (
            cam_stand_center_to_white_line_head
            + white_line_head_to_tail
            - (cam_stand_center_to_roi_head + roi_head_to_tail + roi_tail_to_rear_wall)
        )
        white_line_tail_to_ground = (
            residual_length * cam_to_ground / cam_to_white_line_tail
        )
        white_line_tail_width = (
            ROI_WIDTH
            * (cam_to_ground - white_line_tail_to_ground)
            / (cam_to_ground - ROI_HEIGHT["top"])
        )
    else:
        white_line_tail_to_ground = 0.0
        white_line_tail_width = white_line_head_width

    (
        front_center_point_to_white_line_head,
        rear_center_point_to_white_line_head,
    ) = calc_point(form_value)

    print(
        SENSOR_SIZE,
        DUPLICATED_ANGLE,
        MAX_RESOL_DIFF,
    )
    result_dict = {
        "cam_stand_center_to_white_line_head": cam_stand_center_to_white_line_head,
        "white_line_head_width": white_line_head_width,
        "white_line_head_to_tail": white_line_head_to_tail,
        "white_line_tail_to_ground": white_line_tail_to_ground,
        "white_line_tail_width": white_line_tail_width,
        "front_center_point_to_white_line_head": front_center_point_to_white_line_head,
        "rear_center_point_to_white_line_head": rear_center_point_to_white_line_head,
    }
    return CalcResult(**result_dict)


def calc_point(form_value: FormValue) -> tuple[float, float]:
    # calculate point
    # break down form value
    cam_stand_to_ground = form_value.cam_stand_to_ground
    cam_stand_center_to_roi_head = form_value.cam_stand_center_to_roi_head
    roi_head_to_tail = form_value.roi_head_to_tail
    roi_tail_to_rear_wall = form_value.roi_tail_to_rear_wall

    # calc angles

    ## front center point
    ## rear center point
    return (0.0, 0.0)


def calc_resol(
    nearest_point_from_vertical_rad: float,
    center_from_nearest_point_rad: float,
    depth_fov_rad: float,
) -> float:
    center_angle_rad = nearest_point_from_vertical_rad + center_from_nearest_point_rad
    return math.tan(depth_fov_rad / 2) / math.cos(center_angle_rad)


def calc_width_at_nearest(
    cam_to_ground: float,
    nearest_point_from_vertical_rad: float,
    center_from_nearest_point_rad: float,
    depth_fov_rad: float,
    camera_rotation: str,
) -> float:
    if camera_rotation == "vertical":
        v_pxs = SENSOR_SIZE["long"]["px"]
        h_pxs = SENSOR_SIZE["short"]["px"]
    elif camera_rotation == "horizontal":
        v_pxs = SENSOR_SIZE["short"]["px"]
        h_pxs = SENSOR_SIZE["long"]["px"]
    else:
        raise ValueError("camera_rotation must be vertical or horizontal")
    return (
        (cam_to_ground - ROI_HEIGHT["top"])
        / math.cos(nearest_point_from_vertical_rad)
        * math.cos(center_from_nearest_point_rad)
        * math.tan(depth_fov_rad / 2)
        * h_pxs
        / v_pxs
    )


def calc_theta2_candidate(
    lower_cam_top_from_vertical_rad,
    total_angle_rad,
    head_angle_rad,
) -> tuple[float, float]:
    # Condition1 上下方向の画角が十分であること
    cond1_range = (
        total_angle_rad + head_angle_rad - lower_cam_top_from_vertical_rad,
        float("inf"),
    )
    # Condition2 最近部で左右の画角が十分であること
    cond2_range = (0.0, float("inf"))
    # Condition3 theta1側のカメラと解像度の差が十分小さいこと
    cond3_range = (0.0, float("inf"))

    mins, maxs = zip(cond1_range, cond2_range, cond3_range)
    res = (max(mins), min(maxs))
    if res[0] > res[1]:
        return 0.0, 0.0
    else:
        return res
