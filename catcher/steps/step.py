from abc import abstractmethod


class Step:
    @abstractmethod
    def action(self, variables: dict) -> dict:
        pass
