from string_with_arrows import string_with_arrows


class Error:
    def __init__(self, pos_start, pos_end, error_name, details) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f"{self.error_name}: {self.details}\n"
        result += f"File :{self.pos_start.fn}, in line: {self.pos_start.ln + 1}"
        result += "\n\n" + string_with_arrows(
            self.pos_start.ftxt, self.pos_start, self.pos_end
        )
        return result


class IllegalCharacterError(Error):
    def __init__(self, pos_start, pos_end, details) -> None:
        super().__init__(pos_start, pos_end, "Illegal Character", details)

