from cryptocurrency.blockchain.models import *
from cryptocurrency.blockchain.views import *

blocks = Block.objects.filter()
hashes = [block.hash for block in blocks]
print(hashes)

chain.last_block