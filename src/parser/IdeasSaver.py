import csv
from parser.models import Idea
from loguru import logger as log


class IdeasSaver:
    def save2csv(self, ideas: list[Idea], file_name: str = "ideas") -> None:
        fields: tuple[str, ...] = ideas[0]._fields
        
        log.info(f"Writing to {file_name}.csv")

        with open(f"{file_name}.csv", "w") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow(fields)
            writer.writerows(ideas)

        log.info("Complete!")

