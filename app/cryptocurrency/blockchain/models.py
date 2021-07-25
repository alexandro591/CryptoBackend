from django.db import models
from cryptocurrency.utils import encryption
import json
from Crypto.Signature import pkcs1_15 as verifier
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from django.conf import settings
import hashlib
from django.db.models import Sum
from cryptocurrency.account.models import Account
import uuid
from fernet_fields import EncryptedTextField
from colorama import Fore, Style
import traceback

class Wallet(models.Model):
  uuid = models.UUIDField(null=False, blank=False, default=uuid.uuid4, editable=False, unique=True)
  account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='wallets')
  public_key = EncryptedTextField(null=False, blank=False)
  private_key = EncryptedTextField(null=False, blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  @property
  def balance(self):
    transactions_received = self.transactions_received.filter(
      status=Transaction.STATUS_CHOICES.COMPLETED
    ).aggregate(balance = Sum('amount'))["balance"]
    
    transactions_sent = self.transactions_sent.exclude(
      status=Transaction.STATUS_CHOICES.ERROR
    ).aggregate(balance = Sum('amount'))["balance"]
    
    return (transactions_received or 0.0) - (transactions_sent or 0.0)

  @property 
  def to_dict(self):
    return {
      "id": self.pk,
      "uuid": str(self.uuid),
      "account": self.account.to_dict,
      "public_key": self.public_key,
      "private_key": self.private_key,
      "created_at": str(self.created_at),
      "updated_at": str(self.updated_at),
    }

  def save(self, *args, **kwargs):
    if not self.public_key or not self.private_key:
      key = RSA.generate(settings.RSA_BITS)
      self.public_key = key.public_key().exportKey('PEM').decode('utf-8')
      self.private_key = key.exportKey('PEM').decode('utf-8')
      super().save(*args, **kwargs)

  def send_money(self, amount, receiver):
    if (self.balance or 0)>=amount or self == Wallet.objects.get(account__user__isnull=True):
      transaction = Transaction(amount = amount, sender = self, receiver = receiver);
      private_key = RSA.import_key(self.private_key)
      transaction_hash = SHA256.new(json.dumps(transaction.to_dict).encode('utf8'))
      signature = verifier.new(private_key).sign(transaction_hash)
      transaction.save(sender_public_key = self.public_key, signature = signature)
      return transaction
    raise Exception("Error", "not enough coins to proceed with this transaction")

  class Meta:
    db_table = 'wallets'

class Transaction(models.Model):
  
  class STATUS_CHOICES(models.TextChoices):
    PENDING = "PENDING", ('PENDING')
    ERROR = "ERROR", ('ERROR')
    COMPLETED = "COMPLETED", ('COMPLETED')
  
  uuid = models.UUIDField(null=False, blank=False, default=uuid.uuid4, editable=False, unique=True)
  amount = models.FloatField(null=False, blank=False)
  sender = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions_sent')
  receiver = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions_received')
  status = models.TextField(null=False, blank=False, choices=STATUS_CHOICES.choices, default=STATUS_CHOICES.PENDING)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  @property
  def to_dict(self):
    return {
      "id": self.pk,
      "uuid": str(self.uuid),
      "amount": self.amount,
      "sender": self.sender.to_dict,
      "receiver": self.receiver.to_dict,
      "status": self.status,
      "created_at": str(self.created_at),
      "updated_at": str(self.updated_at),
    }

  def save(self, *args, **kwargs):
    try:
      sender_public_key = kwargs["sender_public_key"]
      signature = kwargs["signature"]
      public_key = RSA.import_key(sender_public_key)
      transaction_hash = SHA256.new(json.dumps(self.to_dict).encode('utf8'))
      verifier.new(public_key).verify(transaction_hash, signature)
      previous_hash = Block.objects.filter().last().hash if Block.objects.filter().last() else None
      new_block = Block(previous_hash = previous_hash, transaction = self);
      
      if self.sender == Wallet.objects.get(account__user__isnull=True):
        self.status = self.STATUS_CHOICES.COMPLETED
      
      super().save(*args)
      
      if(self.status == self.STATUS_CHOICES.COMPLETED):
        new_block.save()
    
    except Exception:
      print(f"{Fore.RED}An error ocurred while trying to save the transaction{Style.RESET_ALL}: {traceback.format_exc()}")
      self.status = self.STATUS_CHOICES.ERROR
      super().save(*args)

  class Meta:
    db_table = 'transactions'
    
class Block(models.Model):

  uuid = models.UUIDField(null=False, blank=False, default=uuid.uuid4, editable=False, unique=True)
  previous_hash = models.TextField(null=True, blank=False, unique=True)
  hash = models.TextField(null=False, blank=False, unique=True)
  transaction = models.OneToOneField(
    Transaction,
    on_delete=models.CASCADE,
    primary_key=True,
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  @property
  def nonce(self):
    return encryption.generateNonce()
  
  @property
  def to_dict(self):
    return {
      "id": self.pk,
      "uuid": str(self.uuid),
      "previous_hash" : self.previous_hash,
      "hash": self.hash,
      "transaction" : self.transaction.to_dict,
      "created_at": str(self.created_at),
      "updated_at": str(self.updated_at),
    }
  
  @property
  def calculate_hash(self):
    sha256 = hashlib.sha256()
    transactionStr = f"{json.dumps(self.transaction.to_dict)}"
    transactionUTF8 = transactionStr.encode('utf-8')
    sha256.update(transactionUTF8)
    return sha256.hexdigest()
  
  def save(self, *args, **kwargs):
    self.hash = self.calculate_hash
    super().save(*args, **kwargs)
  
  class Meta:
    db_table = 'blocks'