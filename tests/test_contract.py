"""contract.cairo test file."""
import os

import pytest

# from starkware.starknet.testing.starknet import Starknet

from forked_starknet import ForkedStarknet

# The path to the contract source code.
CONTRACT_FILE = os.path.join("contracts", "contract.cairo")


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_increase_balance():
    """Test increase_balance method."""
    # Create a new Starknet class that simulates the StarkNet
    # system.
    starknet = await ForkedStarknet.empty()

    account = 0x063c94d6B73eA2284338f464f86F33E12642149F763Cd8E76E035E8E6A5Bb0e6
    dai = await starknet.get_contract_at(0x03e85bfbb8e2a42b7bead9e88e9a1b19dbccf661471061807292120462396ec9)

    balance = (await dai.balanceOf(account).call()).result

    print(balance)

    # # Deploy the contract.
    # contract = await starknet.deploy(
    #     source=CONTRACT_FILE,
    # )

    # # Invoke increase_balance() twice.
    # await contract.increase_balance(amount=10).execute()
    # await contract.increase_balance(amount=20).execute()

    # # Check the result of get_balance().
    # execution_info = await contract.get_balance().call()
    # assert execution_info.result == (30,)

    # # Check the result of get_balance().
    # execution_info = await contract.get_balance().call()
