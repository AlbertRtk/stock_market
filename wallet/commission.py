

class Commission:
    def __init__(self, rate: float, minimum: float):
        self.rate = rate
        self.minimum = minimum

    def __call__(self, trade: float, *args, **kwargs) -> float:
        fee = trade * self.rate
        fee = round(fee, 2)
        return max(fee, self.minimum)

    def minimal_recommended_investment(self):
        return self.minimum / self.rate
