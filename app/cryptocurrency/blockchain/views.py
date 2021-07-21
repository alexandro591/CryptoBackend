from cryptocurrency.blockchain.models import Transaction, Block, Wallet
from django.contrib.auth.models import User
from cryptocurrency.account.models import Account
from rest_framework.views import APIView
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from rest_framework.authtoken.models import Token
from colorama import Fore, Style
import traceback

class Chain:
  def __init__(self):
    self.blocks = []
    
    transactions = Transaction.objects.filter()
    blocks = Block.objects.filter()
    
    if(transactions.count() == 0 or blocks.count() == 0):
      GENESIS_NAME = settings.GENESIS_NAME
      CREATOR_NAME = settings.CREATOR_NAME
      
      try:
        superuser = User.objects.get(username=settings.SUPERADMIN_USER)
      except:
        superuser = User.objects.create_superuser(settings.SUPERADMIN_USER, settings.SUPERADMIN_EMAIL, settings.SUPERADMIN_PASSWORD)
      
      genesis_account, _ = Account.objects.get_or_create(name=GENESIS_NAME)
      creator_account, _ = Account.objects.get_or_create(name=CREATOR_NAME, user=superuser)
      
      genesis_wallet, _ = Wallet.objects.get_or_create(account = genesis_account)
      creator_wallet, _ = Wallet.objects.get_or_create(account = creator_account)
      
      genesis_wallet.sendMoney(100, creator_wallet)
  
  # def genesis_wallet(self):
  
  def updateChain(self):
    blocks = Block.objects.filter()
    self.blocks = []
    for block in blocks:
      self.blocks.append(block.to_dict)
  
  def transactionsFromWallet(self, wallet):
    transactions = Transaction.objects.filter(receiver = wallet)
    received = []
    for transaction in transactions:
      received.append(transaction.to_dict)
    sent = []
    transactions = Transaction.objects.filter(sender = wallet)
    for transaction in transactions:
      sent.append(transaction.to_dict)
    return {
      "received": received,
      "sent": sent
    }

try:
  chain = Chain()
except Exception:
  print(f"{Fore.RED}An error ocurred while trying to initialize the chain{Style.RESET_ALL}: {traceback.format_exc()}")
  chain = None

class ChainView(View):
  def get(self, request):
    global chain
    if(chain == None):
      chain = Chain()
    chain.updateChain()
    return JsonResponse({
      "chain" : chain.blocks
    })
    

class ChainUserView(APIView):
  def get(self, request):
    token = request.META.get("HTTP_AUTHORIZATION")[7:]
    user = Token.objects.get(key=token).user.account
    wallets_transactions = []
    for wallet in user.wallets.all():
      wallets_transactions.append(chain.transactionsFromWallet(wallet))
    return JsonResponse({
      "transactions" : wallets_transactions
    })