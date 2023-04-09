import asyncio

import pytest
from click.testing import CliRunner

from cashu.core.migrations import migrate_databases
from cashu.core.settings import settings
from cashu.wallet import migrations
from cashu.wallet.cli.cli import cli
from cashu.wallet.wallet import Wallet
from tests.conftest import SERVER_ENDPOINT, mint


@pytest.fixture(autouse=True, scope="session")
def cli_prefix():
    yield ["--wallet", "test_wallet", "--host", settings.mint_url]


@pytest.fixture(scope="session")
def wallet():
    wallet = Wallet(settings.mint_host, "data/test_wallet", "wallet")
    asyncio.run(migrate_databases(wallet.db, migrations))
    asyncio.run(wallet.load_proofs())
    yield wallet


async def init_wallet():
    wallet = Wallet(settings.mint_host, "data/test_wallet", "wallet")
    await migrate_databases(wallet.db, migrations)
    await wallet.load_proofs()
    return wallet


@pytest.mark.asyncio
def test_info(cli_prefix):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [*cli_prefix, "info"],
    )
    assert result.exception is None
    print("INFO")
    print(result.output)
    result.output.startswith(f"Version: {settings.version}")
    assert result.exit_code == 0


@pytest.mark.asyncio
def test_balance(cli_prefix):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [*cli_prefix, "balance"],
    )
    assert result.exception is None
    print("------ BALANCE ------")
    print(result.output)
    w = asyncio.run(init_wallet())
    assert f"Balance: {w.available_balance} sat" in result.output
    assert result.exit_code == 0


@pytest.mark.asyncio
def test_invoice(mint, cli_prefix):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [*cli_prefix, "invoice", "1000"],
    )
    assert result.exception is None
    print("INVOICE")
    print(result.output)
    # wallet = asyncio.run(init_wallet())
    # assert f"Balance: {wallet.available_balance} sat" in result.output
    assert result.exit_code == 0


@pytest.mark.asyncio
def test_wallets(cli_prefix):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [*cli_prefix, "wallets"],
    )
    assert result.exception is None
    print("WALLETS")
    # on github this is empty
    if len(result.output):
        assert "test_wallet" in result.output
    assert result.exit_code == 0


@pytest.mark.asyncio
def test_send(mint, cli_prefix):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [*cli_prefix, "send", "10"],
    )
    assert result.exception is None
    print("SEND")
    print(result.output)
    assert "cashuA" in result.output, "output does not have a token"


@pytest.mark.asyncio
def test_receive_tokenv3(mint, cli_prefix):
    runner = CliRunner()
    token = "cashuAeyJ0b2tlbiI6IFt7InByb29mcyI6IFt7ImlkIjogIjI4ajhueVNMMU5kZCIsICJhbW91bnQiOiAyLCAic2VjcmV0IjogIm1PVmlIaDR2MVQwdGNORHNuRkw5X1EiLCAiQyI6ICIwMzQ3NWJjZDA2MjFjOTAwOTlmNmE2MDA2MjkxODg3MmExMmEzNmI0OGRmNDI4ZGJlMjc4MDNiOGQzZGQyMDQ4YmMifSwgeyJpZCI6ICIyOGo4bnlTTDFOZGQiLCAiYW1vdW50IjogOCwgInNlY3JldCI6ICJ2UmdneFBOT0ZJZVA0MURvejEtUGd3IiwgIkMiOiAiMDI3ODFiMmY0ZTk0NTI0NmFmY2M0MGVmYjcwNTQ5YWFlZGMyOWE3ZWQ4ZjM3ZmVkOWY1YjdmYzJhNTAzYzgzOWRjIn1dLCAibWludCI6ICJodHRwOi8vbG9jYWxob3N0OjMzMzcifV19"
    result = runner.invoke(
        cli,
        [
            *cli_prefix,
            "receive",
            token,
        ],
    )
    assert result.exception is None
    print("RECEIVE")
    print(result.output)


@pytest.mark.asyncio
def test_receive_tokenv3_no_mint(mint, cli_prefix):
    # this test works only if the previous test succeeds because we simulate the case where the mint URL is not in the token
    # therefore, we need to know the mint keyset already and have the mint URL in the db
    runner = CliRunner()
    token = "cashuAeyJ0b2tlbiI6IFt7InByb29mcyI6IFt7ImlkIjogIjI4ajhueVNMMU5kZCIsICJhbW91bnQiOiAyLCAic2VjcmV0IjogIm45X0h4XzROZHpybFRheWpkX0pXRXciLCAiQyI6ICIwMjNhYzhiOWFiMDU3ZTUzZDk1MmFhZWM4NzJmMjJhNGZlOTk0YTU3ZjQ2YWIwYjYyNzEyYzVhYzQ5ZGZlNDY0MTUifSwgeyJpZCI6ICIyOGo4bnlTTDFOZGQiLCAiYW1vdW50IjogOCwgInNlY3JldCI6ICJTTnF5VEdqUTJpQy1CbzdscWlhZF93IiwgIkMiOiAiMDM2OWJkNDhiZWZlYTQ2Zjk3ZWFjNjQ0YTBkZTViYWIyNWYxMjYwY2NjZTAzNTNlOGM4Mzg0YjY3OTE1YzlhNTE2In1dfV19"
    result = runner.invoke(
        cli,
        [
            *cli_prefix,
            "receive",
            token,
        ],
    )
    assert result.exception is None
    print("RECEIVE")
    print(result.output)


@pytest.mark.asyncio
def test_receive_tokenv2(mint, cli_prefix):
    runner = CliRunner()
    token = "eyJwcm9vZnMiOiBbeyJpZCI6ICIyOGo4bnlTTDFOZGQiLCAiYW1vdW50IjogMiwgInNlY3JldCI6ICJuWGpGRUV2SmZhMDNkeFVEbFRKM3BRIiwgIkMiOiAiMDI2NDFjNjQ0M2M3MDg4NWYyY2RhODg5ODZjZjRiZGQzNzhkNDE4Zjg4YjFhNWRhYTcyYzk3OWQ4NDU2ZDljYWJmIn0sIHsiaWQiOiAiMjhqOG55U0wxTmRkIiwgImFtb3VudCI6IDgsICJzZWNyZXQiOiAiblRXeGlhWmk5ZnNkV1FYNktMRS1NUSIsICJDIjogIjAyY2UwNzdjMjZmNWQ3ZTAxYjExMzk3ZTdmZThhN2FmZmI2YzJlZDA1ODljODBmZTY3YWUxNzUzZTQ2OGViOGMwNyJ9XSwgIm1pbnRzIjogW3sidXJsIjogImh0dHA6Ly9sb2NhbGhvc3Q6MzMzNyIsICJpZHMiOiBbIjI4ajhueVNMMU5kZCJdfV19"
    result = runner.invoke(
        cli,
        [*cli_prefix, "receive", token],
    )
    assert result.exception is None
    print("RECEIVE")
    print(result.output)


@pytest.mark.asyncio
def test_receive_tokenv1(mint, cli_prefix):
    runner = CliRunner()
    token = "W3siaWQiOiAiMjhqOG55U0wxTmRkIiwgImFtb3VudCI6IDIsICJzZWNyZXQiOiAiOEFmZmxMeEJWczRYVGxETDhkQjZpZyIsICJDIjogIjAyMTkxZjg1NTRiZjcxMGJiNzc2YjEzMmYxYjg4MTk5NjU3ZmRiYjkxZjU5ZDgzMzEzOGQ4NTQyYjI1ODliNmY5NyJ9LCB7ImlkIjogIjI4ajhueVNMMU5kZCIsICJhbW91bnQiOiA4LCAic2VjcmV0IjogIjBNZzB1TjJJT1I3eWloYWx0X1hIWVEiLCAiQyI6ICIwMmY1MzQ2ZmZiMmJiODJlOGUwYmYzZTVlNjcwYWRmYzc2ZTdhNmYxMmE4ZWIwMmUwOTk0NjQ5NmFmYWExZDdlMjEifV0="
    result = runner.invoke(
        cli,
        [*cli_prefix, "receive", token],
    )
    assert result.exception is None
    print("RECEIVE")
    print(result.output)


@pytest.mark.asyncio()
def test_nostr_send(mint, cli_prefix):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            *cli_prefix,
            "send",
            "1",
            "-n",
            "aafa164a8ab54a6b6c67bbac98a5d5aec7ea4075af8928a11478ab9d74aec4ca",
            "-y",
        ],
    )
    assert result.exception is None
    print("NOSTR_SEND")
    print(result.output)
