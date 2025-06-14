# app/refine_strategy.py
def refine_strategy(backtest_results):
    """
    Analyze backtest results and suggest refinements to the strategy.
    :param backtest_results: Dictionary containing backtest results
    :return: Refinement suggestions as a string
    """
    sharpe_ratio = backtest_results.get('sharpe_ratio', 0)
    returns = backtest_results.get('returns', 0)

    suggestions = []
    if sharpe_ratio < 1:
        suggestions.append("Consider adding a stop-loss to reduce risk.")
    if returns < 0:
        suggestions.append("Try optimizing entry conditions to improve returns.")

    return " ".join(suggestions) if suggestions else "No refinements suggested."