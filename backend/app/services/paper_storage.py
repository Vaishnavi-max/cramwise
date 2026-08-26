from pathlib import Path
import json

from app.parsers.paper_grouper import PaperGroup


class PaperStorage:
    """
    Saves and loads paper-wise grouping information.
    """

    def __init__(
        self,
        base_dir: Path | None = None,
    ):
        self.base_dir = (
            base_dir
            if base_dir is not None
            else Path("uploads/temp/papers")
        )

    def save(
        self,
        document_name: str,
        papers: list[PaperGroup],
    ) -> Path:
        """
        Save paper grouping information as papers.json.
        """

        output_dir = (
            self.base_dir
            / document_name
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_dir
            / "papers.json"
        )

        data = {
            "document": document_name,
            "paper_count": len(papers),
            "papers": [],
        }

        for paper in papers:

            data["papers"].append(
                {
                    "paper_id": paper.paper_id,
                    "subject": paper.subject,
                    "subject_code": paper.subject_code,
                    "exam_type": paper.exam_type,
                    "semester": paper.semester,
                    "pages": paper.pages,
                }
            )

        output_file.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return output_file

    def load(
        self,
        document_name: str,
    ) -> dict:
        """
        Load previously saved papers.json.
        """

        output_file = (
            self.base_dir
            / document_name
            / "papers.json"
        )

        if not output_file.exists():

            raise FileNotFoundError(
                f"Paper file not found: "
                f"{output_file}"
            )

        return json.loads(
            output_file.read_text(
                encoding="utf-8",
            )
        )