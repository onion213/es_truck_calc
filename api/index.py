from flask import Flask, render_template, request


from .classes import FormValue
from .calc import calc

app = Flask(__name__)


@app.route("/")
def home():
    form_value = FormValue(
        cam_stand_to_ground=0.0,
        cam_stand_center_to_roi_head=0.0,
        roi_head_to_tail=0.0,
        roi_tail_to_rear_wall=0.0,
    )
    return render_template("index.html", form_value=form_value, result=None)


@app.route("/", methods=["POST"])
def run_calc():
    form_value = FormValue(**request.form)  # type: ignore
    print(form_value)
    return render_template("index.html", form_value=form_value, result=calc(form_value))
