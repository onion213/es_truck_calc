import pydantic


class FormValue(pydantic.BaseModel):
    cam_stand_to_ground: float
    cam_stand_center_to_roi_head: float
    roi_head_to_tail: float
    roi_tail_to_rear_wall: float


class CalcResult(pydantic.BaseModel):
    cam_stand_center_to_white_line_head: float
    white_line_head_width: float
    white_line_head_to_tail: float
    white_line_tail_to_ground: float
    white_line_tail_width: float
    front_center_point_to_white_line_head: float
    rear_center_point_to_white_line_head: float
