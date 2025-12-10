import json
from pathlib import Path
from dinapy.ena.models import Experiment, WebinPayload, Submission, Project, Sample, Run, Study

# Directory (relative to this file) where generated schemas will be written.
OUT_DIR = Path(__file__).parent / "schemas"
print(f"Exporting ENA JSON Schemas to {OUT_DIR}")
def export_all(out_dir: Path = OUT_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)

    files = {
        "schema_webin_v2_payload.json": WebinPayload.model_json_schema(),
        "schema_submission.json": Submission.model_json_schema(),
        "schema_project.json": Project.model_json_schema(),
        "schema_study.json": Study.model_json_schema(),
        "schema_sample.json": Sample.model_json_schema(),
        "schema_run.json": Run.model_json_schema(),
        "schema_experiment.json": Experiment.model_json_schema()
    }

    for name, schema in files.items():
        path = out_dir / name
        with path.open("w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        print(f"Wrote {path}")

if __name__ == "__main__":
    export_all()