"""FinSight End-to-End Pipeline Runner
Executes the full pipeline in order:
1. Ingestion (data/raw -> staging tables)
2. Validation (quality checks on staging tables)
3. Transformation (cleaning -> transformed tables)
4. Warehouse (star schema dimension/fact loading & marts view creation)
"""

import sys
import subprocess
import time

def run_step(step_name: str, module_name: str):
    print(f"\n{'='*60}")
    print(f"Running Step: {step_name} ({module_name})")
    print(f"{'='*60}")
    start = time.time()
    subprocess.run([sys.executable, "-m", module_name], check=True)
    duration = time.time() - start
    print(f"Completed {step_name} in {duration:.2f}s")

def main():
    print("\n" + "#"*60)
    print("  FINSIGHT DATA ENGINEERING PIPELINE")
    print("#"*60)
    
    pipeline_steps = [
        ("Data Ingestion", "src.ingestion"),
        ("Data Quality Validation", "src.validation.runner"),
        ("Data Transformation", "src.transformation"),
        ("Warehouse & Marts Loading", "src.warehouse.load_fact"),
    ]

    for name, module in pipeline_steps:
        run_step(name, module)

    print("\n" + "="*60)
    print("FULL PIPELINE EXECUTED SUCCESSFULLY!")
    print("="*60)

if __name__ == "__main__":
    main()
