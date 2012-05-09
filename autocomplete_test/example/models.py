from django.db import models

class Value(models.Model):
    name = models.CharField(max_length=90)
    
    def __unicode__(self):
        return self.name
    
class Example(models.Model):
    value = models.ForeignKey(Value)
    
    