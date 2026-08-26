from pathlib import Path


class PatchApplier:

    def apply(
        self,
        workspace_path: str,
        file_path: str,
        diff: str,
    ) -> str:

        workspace = Path(workspace_path)
        target_file = workspace / file_path

        if not target_file.exists():
            raise FileNotFoundError(
                f"Patch target not found: {file_path}"
            )

        original = target_file.read_text(
            encoding="utf-8"
        )

        updated = self._apply_diff(
            original,
            diff,
        )

        target_file.write_text(
            updated,
            encoding="utf-8",
        )

        return str(target_file)

    def _apply_diff(
        self,
        original: str,
        diff: str,
    ) -> str:

        diff_lines = diff.splitlines()

        original_lines = original.splitlines()

        old_lines = []
        new_lines = []

        mode = None

        for line in diff_lines:

            if line.startswith("***"):
                continue

            if line.startswith("@@"):
                mode = "changes"
                continue

            if line.startswith("---"):
                continue

            if line.startswith("+++"):
                continue

            if mode != "changes":
                continue

            if line.startswith("-"):
                old_lines.append(line[1:])

            elif line.startswith("+"):
                new_lines.append(line[1:])

            else:
                # Context line
                context = line[1:] if line.startswith(" ") else line

                old_lines.append(context)
                new_lines.append(context)

        if not old_lines:
            raise ValueError(
                "Patch does not contain a valid change block"
            )

        old_block = "\n".join(old_lines)
        new_block = "\n".join(new_lines)

        original_text = "\n".join(original_lines)

        if old_block not in original_text:
            raise ValueError(
                "Patch context could not be found "
                "in the target file"
            )

        updated = original_text.replace(
            old_block,
            new_block,
            1,
        )

        return updated + "\n"