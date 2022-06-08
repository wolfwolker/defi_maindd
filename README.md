# INTRO #

This project aims to be a wrapper with some shortcuts to use chain-maind cli by crypto.com https://crypto.org/docs/wallets/cli.html

Use it under your responsibility.

Is not my business if there is any bug or misconfiguration and you lose your funds. 


# USAGE #

0. install chain_maind cli tool, if you use linux or macos you can download it with homebrew
1. add the variables described in the `.env.dist` to your environment or to the `.env` file
2. you should create a virtualenv under `./venv/` and install the requirements
3. run `./main.py --help` to see available commands and options


# COMMAND SAMPLES # 

some chain-maind command samples:

```commandline
chain-maind keys list --keyring-backend file
chain-maind query bank balances ADDRESS --chain-id crypto-org-chain-mainnet-1 --node https://mainnet.crypto.org:443
chain-maind query distribution rewards ADDRESS --chain-id crypto-org-chain-mainnet-1 --node https://mainnet.crypto.org:443
chain-maind query staking delegations ADDRESS --chain-id crypto-org-chain-mainnet-1 --node https://mainnet.crypto.org:443
chain-maind tx staking redelegate FROM_ADDRESS TO_ADDRESS 300005012basecro --chain-id crypto-org-chain-mainnet-1 --node https://mainnet.crypto.org:443 --keyring-backend file --from default -y --gas auto --fees 5778basecro
chain-maind tx distribution withdraw-all-rewards --chain-id crypto-org-chain-mainnet-1 --node https://mainnet.crypto.org:443 --keyring-backend file --from default --gas auto -y --fees 7000basecro
```
