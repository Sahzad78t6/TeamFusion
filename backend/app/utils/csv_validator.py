import csv
import os
import logging

logger = logging.getLogger(__name__)

OPPORTUNITIES_CSV_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../ml/datasets/opportunities.csv")
)

def validate_opportunities_csv(csv_path: str = OPPORTUNITIES_CSV_PATH) -> bool:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Opportunities CSV dataset missing at: {csv_path}")

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            raise ValueError(f"Opportunities CSV at {csv_path} is empty.")

        expected_cols = len(header) # Should be 10
        if expected_cols != 10:
            raise ValueError(f"Opportunities CSV header has {expected_cols} columns, expected 10.")

        row_count = 0
        for i, row in enumerate(reader, start=2):
            if not row or not any(row):
                continue
            row_count += 1
            if len(row) != expected_cols:
                raise ValueError(
                    f"Opportunities CSV format error on line {i} (id={row[0] if row else 'N/A'}): "
                    f"Expected {expected_cols} columns, but found {len(row)} columns. "
                    f"Raw row content: {row}"
                )
            
            # VerifyDictReader parsing produces expected keys
            try:
                min_score = float(row[7])
                if not (0.0 <= min_score <= 1.0):
                    raise ValueError(f"Line {i}: min_relevance_score {min_score} out of bounds 0..1")
            except ValueError as e:
                raise ValueError(f"Line {i}: invalid min_relevance_score '{row[7]}': {e}")

    logger.info(f"✓ Opportunities CSV validation successful ({row_count} rows verified cleanly).")
    return True

if __name__ == "__main__":
    validate_opportunities_csv()
    print("CSV validation passed!")
