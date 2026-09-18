from datetime import datetime
from pathlib import Path
import subprocess
import sys
import time


PROJECT = Path(__file__).parent

PROGRAMS = [
    "smartbudget_analysis.py",
    "invoice_ocr.py",
]


def run_program(filename):
    """Run one project program and check for errors."""
    program_path = PROJECT / filename

    print(f"\nRunning {filename}...")

    result = subprocess.run(
        [sys.executable, str(program_path)],
        cwd=PROJECT,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)

        raise RuntimeError(
            f"{filename} failed."
        )

    print(f"{filename} completed successfully.")


def main():
    start_time = time.time()

    print("=" * 50)
    print("SMARTBUDGET AUTOMATED PIPELINE")
    print(
        "Started:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )
    print("=" * 50)

    completed = []

    try:
        for program in PROGRAMS:
            run_program(program)
            completed.append(program)

    except RuntimeError as error:
        print("\nPipeline stopped.")
        print(error)
        sys.exit(1)

    elapsed = time.time() - start_time

    print("\n" + "=" * 50)
    print("PIPELINE COMPLETED")
    print(f"Programs completed: {len(completed)}")
    print(f"Runtime: {elapsed:.2f} seconds")
    print(
        "Finished:",
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )
    print("=" * 50)


if __name__ == "__main__":
    main()