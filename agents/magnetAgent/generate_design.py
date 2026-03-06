"""Generate Halbach magnet design files and plots using HalbachMRIDesigner."""

import os
import subprocess


def main() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    halbach_dir = os.path.join(project_root, "HalbachMRIDesigner")
    halbach_script = os.path.join(halbach_dir, "HalbachMRIDesigner.py")
    input_json = os.path.join(halbach_dir, "examples", "mri1.json")

    output_prefix = os.path.join(project_root, "outputs", "halbach_design")
    os.makedirs(os.path.dirname(output_prefix), exist_ok=True)

    cmd = [
        "python",
        halbach_script,
        input_json,
        "--contour",
        "--quiver",
        "--scad",
        "-o",
        output_prefix,
    ]

    result = subprocess.run(
        cmd,
        cwd=project_root,
        text=True,
        capture_output=True,
        timeout=300,
    )

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise SystemExit(result.returncode)

    print("\nGenerated files:")
    print(f"- {output_prefix}.scad")
    print(f"- {output_prefix}.geo (if --fem is enabled)")
    print(f"- {output_prefix}.msh (if --fem is enabled)")
    print("Plots were displayed for contour and quiver.")


if __name__ == "__main__":
    main()
