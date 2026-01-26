import json
import subprocess

def js_spline_lookup(
    ibi_indexed,
    interpolation_groups,
    tension=0.2,
    node_path="node",
    script_path="/Users/nina/Desktop/University of Vienna/PhD projects/python code/interoception-synchrony/Interpolate IBI data/src/js_curve_interpolator/run_interpolator.js"
):
    payload = {
        "ibi_indexed": ibi_indexed,
        "interpolation_groups": interpolation_groups,
        "tension": tension
    }

    result = subprocess.run(
        [node_path, script_path],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False   # 🔴 important - needs to be True
    )

    # print("NODE STDOUT:\n", result.stdout)
    # print("NODE STDERR:\n", result.stderr)

    result.check_returncode()

    return json.loads(result.stdout)

