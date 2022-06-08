#!./venv/bin/python

from os import environ as env
import click
import subprocess
from math import trunc, floor
import json
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# try:
#     from queue import Queue, Empty
# except ImportError:
#     from Queue import Queue, Empty  # python 2.x
#
# ON_POSIX = 'posix' in sys.builtin_module_names

bin = env.get("MAINDD_BIN", "~/.linuxbrew/bin/chain-maind")
passwd = env.get("MAINDD_PASSWD", "")
env_chain = env.get("MAINDD_BLOCKCHAIN", "crypto-org-chain-mainnet-1")
env_node = env.get("MAINDD_NODE", "https://mainnet.crypto.org:443")
env_delegator = env.get("MAINDD_DELEGATOR", "")
env_validator = env.get("MAINDD_VALIDATOR", "")

output = ["--output", "json"]
chain = ["--chain-id", env_chain, ]
node = ["--node", env_node, ]
keyring = ["--keyring-backend", "file"]
fees = ["--fees", "8500basecro"]
gas = ["--gas", "auto"]
conversion_rate = 10 ** 8  # from basecro to cro

balances = [bin, "query", "bank", "balances", env_delegator, ] + chain + node + output
check_rewards = [bin, "query", "distribution", "rewards", env_delegator, ] + chain + node + output
withdraw_rewards = [bin, "tx", "distribution", "withdraw-all-rewards", "--from", env_delegator,
                    "-y"] + keyring + chain + node + fees + gas + output
stake = [bin, "tx", "staking", "delegate", env_validator, "qty", "--from", env_delegator,
         "-y"] + keyring + chain + node + fees + gas + output
kl = [bin, "keys", "list"] + keyring + output


class CodedError(Exception):
    code = None
    output = None

    def __init__(self, code, output = None):
        self.code = code
        self.output = output


def run(command, isTx, debug=False):
    try:
        cmd = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = cmd.communicate(f'{passwd}\n'.encode())
        returnCode = cmd.wait()

        # print("output")
        # print(output)
        # print("errors")
        # print(errors)
        # print("returncode")
        # print(returnCode)

        if returnCode == 0:
            output = json.loads(output)
            if isTx and get(output, "code") != 0:
                click.echo(json.dumps(output, indent=2, sort_keys=True))
                raise CodedError(get(output, "code"), output)
            elif debug:
                click.echo(json.dumps(output, indent=2, sort_keys=True))

            return output
        else:
            raise IOError(errors, returnCode)

    except CodedError as e:
        if e.code == 13:
            pass
        # click.echo(e.code)
        raise e


# a = float(["balances"][0]["amount"]) / conversion_rate
# print(floor(a))


########
# TODO
# 1. setup a threshold
# 2. check available rewards and if there are more than threshold
# 3. withdraw withdraw_rewards
# 4. delegate rewards [remember to floor them down and always keep twice the fee]


@click.command()
@click.option("--action", prompt="action?", help="cr|rewards|balance|stake|all", default="balance", show_default=True)
@click.option('--debug', is_flag=True)
def hello(debug, action=None):
    # debug = True

    if action in ("all", "cr"):
        out = run(check_rewards, False, debug)
        click.echo(f"Cumulated rewards are {float(get(out, 'total.0.amount')) / conversion_rate} cro")
        if action == "cr":
            return 0

    if action in ("all", "rewards"):
        out = run(withdraw_rewards, True, debug)
        click.echo(f"It worked, this is the txhash {get(out, 'txhash')}")

    out = run(balances, False, debug)
    balance = float(get(out, "balances.0.amount"))
    # this 20000 is more or less double of the fees, so to the total basecro, after removing some "safety qty",
    # convert to cro and floor, that is the qty to delegate
    stake_qty = floor((balance - 20000) / conversion_rate)
    stake[5] = f"{stake_qty}cro"
    click.echo(f"The current balance is {balance} basecro")
    click.echo(f"The quantity to stake is  {stake_qty} cro")

    if action in ("all", "stake"):
        if stake_qty < 10:
            click.echo("qty is to low, skipping staking")
            return 1

        out = run(stake, True, debug)
        click.echo(f"It worked, this is the txhash {get(out, 'txhash')}")


def get(d, keys):
    if isinstance(d, list):
        d = {str(k): v for k, v in enumerate(d)}
    if "." in keys:
        key, rest = keys.split(".", 1)
        return get(d[key], rest)
    else:
        return d.get(keys)


if __name__ == '__main__':
    hello()
