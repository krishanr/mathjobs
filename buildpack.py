from pathlib import Path
import zipfile

project_dir = Path(__file__).resolve().parents[0]

(project_dir / "data/processed/archive").mkdir(exist_ok=True)

with zipfile.ZipFile(project_dir / "arxiv-metadata-processed.zip", 'r') as zip_ref:
        zip_ref.extract("arxiv-metadata-ext-category.csv",path=project_dir / "data/processed/archive")
with zipfile.ZipFile(project_dir / "arxiv-metadata-processed.zip", 'r') as zip_ref:
        zip_ref.extract("arxiv-group-count.csv",path=project_dir / "data/processed/archive")
with zipfile.ZipFile(project_dir / "arxiv-metadata-processed.zip", 'r') as zip_ref:
        zip_ref.extract("arxiv-metadata-ext-taxonomy.csv",path=project_dir / "data/processed/archive")
with zipfile.ZipFile(project_dir / "arxiv-metadata-processed.zip", 'r') as zip_ref:
        zip_ref.extract("arxiv-metadata-ext-version.csv",path=project_dir / "data/processed/archive")
with zipfile.ZipFile(project_dir / "arxiv-metadata-processed.zip", 'r') as zip_ref:
        zip_ref.extract("arxiv-metadata-influential.csv",path=project_dir / "data/processed/archive")