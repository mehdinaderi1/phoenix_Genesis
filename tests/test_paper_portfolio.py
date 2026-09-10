from execution.paper_portfolio import PaperPortfolio


def test_portfolio_starts_with_initial_balance():

    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    assert portfolio.get_balance() == 1000
    assert portfolio.get_total_pnl() == 0


def test_portfolio_applies_profit():

    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    balance = portfolio.apply_realized_pnl(
        10
    )

    assert balance == 1010
    assert portfolio.get_balance() == 1010
    assert portfolio.get_total_pnl() == 10


def test_portfolio_applies_loss():

    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    balance = portfolio.apply_realized_pnl(
        -10
    )

    assert balance == 990
    assert portfolio.get_balance() == 990
    assert portfolio.get_total_pnl() == -10


def test_portfolio_ignores_none_pnl():

    portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    balance = portfolio.apply_realized_pnl(
        None
    )

    assert balance == 1000
    assert portfolio.get_total_pnl() == 0