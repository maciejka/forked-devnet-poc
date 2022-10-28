import copy
from typing import List, Optional, Union

from starkware.python.utils import as_non_optional, from_bytes
from starkware.cairo.lang.vm.crypto import pedersen_hash_func
from starkware.starknet.business_logic.execution.objects import TransactionExecutionInfo
from starkware.starknet.business_logic.transaction.objects import InternalL1Handler
from starkware.starknet.definitions.general_config import StarknetGeneralConfig
from starkware.starknet.public.abi import get_selector_from_name
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.services.api.messages import StarknetMessageToL1
from starkware.starknet.testing.contract import DeclaredClass, StarknetContract
from starkware.starknet.testing.contract_utils import get_abi, get_contract_class
from starkware.starknet.testing.objects import StarknetCallInfo
from starkware.starknet.testing.state import CastableToAddress, CastableToAddressSalt, StarknetState
from starkware.starknet.testing.starknet import Starknet
from starkware.storage.dict_storage import DictStorage
from starkware.storage.storage import FactFetchingContext
from starkware.starknet.business_logic.fact_state.patricia_state import PatriciaStateReader
from starkware.starknet.business_logic.fact_state.state import SharedState
from starkware.starknet.business_logic.state.state import CachedState
from starkware.starknet.business_logic.state.state_api_objects import BlockInfo
from starkware.starkware_utils.commitment_tree.patricia_tree.patricia_tree import PatriciaTree
from starkware.starknet.services.api.feeder_gateway.feeder_gateway_client import FeederGatewayClient
from services.external_api.client import RetryConfig

class ForkedStarknet(Starknet):
    """
    A high level interface to a StarkNet state object.
    Example:
      starknet = await Starknet.empty()
      contract = await starknet.deploy('contract.cairo')
      await contract.foo(a=1, b=[2, 3]).execute()
    """

    # def __init__(self, state: StarknetState):
    #     super().__init__(state)

    @classmethod
    async def empty(cls, general_config: Optional[StarknetGeneralConfig] = None) -> "ForkedStarknet":

        """
        Creates a new StarknetState instance.
        """
        if general_config is None:
            general_config = StarknetGeneralConfig()

        ffc = FactFetchingContext(storage=DictStorage(), hash_func=pedersen_hash_func)
        empty_shared_state = await SharedState.empty(ffc=ffc, general_config=general_config)

        feeder_gateway_url='https://alpha4.starknet.io/feeder_gateway/'
        # feeder_gateway_url='https://alpha-mainnet.starknet.io/feeder_gateway/'

        retry_config = RetryConfig(n_retries=1)
        fgc = FeederGatewayClient(url=feeder_gateway_url, retry_config=retry_config)

        state_reader = LoggingPatriciaStateReader(
            global_state_root=empty_shared_state.contract_states, ffc=ffc, fgc=fgc
        )

        state = CachedState(
            block_info=BlockInfo.empty(sequencer_address=general_config.sequencer_address),
            state_reader=state_reader,
        )

        return ForkedStarknet(StarknetState(state=state, general_config=general_config))

    def copy(self) -> "ForkedStarknet":
        return copy.deepcopy(self)

    async def get_contract_at(self, contract_address: int) -> StarknetContract:
        class_hash  = await self.state.state.get_class_hash_at(contract_address)
        contract_class = await self.state.state.get_contract_class(class_hash)
        return StarknetContract(
            state=self.state,
            abi=get_abi(contract_class=contract_class),
            contract_address=contract_address,
            deploy_call_info=None #deploy_call_info,
        )

class LoggingPatriciaStateReader(PatriciaStateReader):
    def __init__(self, global_state_root: PatriciaTree, ffc: FactFetchingContext, fgc: FeederGatewayClient):
        super().__init__(global_state_root, ffc)
        self.fgc = fgc

    async def get_contract_class(self, class_hash: bytes) -> ContractClass:
        # r = await super().get_contract_class(class_hash)
        data = await self.fgc.get_class_by_hash(class_hash.decode())
        r = ContractClass.load(data)
        print("\nget_contract_class({})->...".format(class_hash))
        return r
        # return await super().get_contract_class(class_hash)

    async def get_class_hash_at(self, contract_address: int) -> bytes:
        # return await super().get_class_hash_at(contract_address)
        raw = await self.fgc.get_class_hash_at(contract_address)
        # convert
        print("\nget_class_hash_at({})->{}".format(contract_address, raw))
        return raw.encode()

    async def get_nonce_at(self, contract_address: int) -> int:
        print("\nget_nonce_at({})".format(contract_address))
        return await super().get_nonce_at(contract_address)

    async def get_storage_at(self, contract_address: int, key: int) -> int:
        # r = await super().get_storage_at(contract_address, key)
        raw = await self.fgc.get_storage_at(contract_address, key)
        print("\nget_storage_at({}, {})->{}".format(contract_address, key, raw))
        return int(raw, base=16)
