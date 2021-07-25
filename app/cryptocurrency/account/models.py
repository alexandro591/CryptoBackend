from django.db import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
import uuid

class Account(models.Model):
  uuid = models.UUIDField(null=False, blank=False, default=uuid.uuid4, editable=False, unique=True)
  user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    null=True, 
    blank=True,
    unique=True,
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  @property
  def to_dict(self):
    return {
      "id": self.pk,
      "uuid": str(self.uuid),
      # "user": model_to_dict(self.user) if self.user else None,
      "created_at": str(self.created_at),
      "updated_at": str(self.updated_at),
    }

  class Meta:
    db_table = 'accounts'