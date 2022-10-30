"""contract.cairo test file."""
import os

import pytest

# from starkware.starknet.testing.starknet import Starknet

from forked_starknet import ForkedStarknet

# The path to the contract source code.
CONTRACT_FILE = os.path.join("contracts", "contract.cairo")

def split_uint(a):
    return (a & ((1 << 128) - 1), a >> 128)

def to_uint(a):
    return a[0] + (a[1] << 128)


# The testing library uses python's asyncio. So the following
# decorator and the ``async`` keyword are needed.
@pytest.mark.asyncio
async def test_increase_balance():
    """Test increase_balance method."""
    # Create a new Starknet class that simulates the StarkNet
    # system.
    starknet = await ForkedStarknet.empty()

    user_address = 0x063c94d6B73eA2284338f464f86F33E12642149F763Cd8E76E035E8E6A5Bb0e6
    dai_address = 0x03e85bfbb8e2a42b7bead9e88e9a1b19dbccf661471061807292120462396ec9
    bridge_address = 0x075ac198e734e289a6892baa8dd14b21095f13bf8401900f5349d5569c3f6e60

    dai = await starknet.get_contract_at(dai_address)

    balance = (await dai.balanceOf(user_address).call()).result.res

    print(balance)


    allowance = (await dai.allowance(user_address, bridge_address).call()).result.res

    print(allowance)

    tx = await dai.approve(bridge_address, split_uint(10)).execute(user_address)

    # print(tx)

    allowance = (await dai.allowance(user_address, bridge_address).call()).result.res

    print(allowance)

    # print(starknet.state.state.cache.storage_view)

    assert allowance.low == 10

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

    # print(starknet.state.state.cache.storage_view)
