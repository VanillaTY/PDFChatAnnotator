from django.db import models

# Create your models here.


class LabelName(models.Model):
    # question = models.ForeignKey(Question, on_delete=models.CASCADE)
    labelName1 = models.CharField(max_length=200, blank=True, null=True)
    labelName2 = models.CharField(max_length=200, blank=True, null=True)
    labelName3 = models.CharField(max_length=200, blank=True, null=True)
    labelName4 = models.CharField(max_length=200, blank=True, null=True)
    labelName5 = models.CharField(max_length=200, blank=True, null=True)
    labelName6 = models.CharField(max_length=200, blank=True, null=True)
    labelName7 = models.CharField(max_length=200, blank=True, null=True)
    labelName8 = models.CharField(max_length=200, blank=True, null=True)
    labelName9 = models.CharField(max_length=200, blank=True, null=True)


class LabelLists(models.Model):
    # question = models.ForeignKey(Question, on_delete=models.CASCADE)
    imgName = models.CharField(max_length=200)
    label1 = models.CharField(max_length=200, blank=True, null=True)
    label2 = models.CharField(max_length=200, blank=True, null=True)
    label3 = models.CharField(max_length=200, blank=True, null=True)
    label4 = models.CharField(max_length=200, blank=True, null=True)
    label5 = models.CharField(max_length=200, blank=True, null=True)
    label6 = models.CharField(max_length=200, blank=True, null=True)
    label7 = models.CharField(max_length=200, blank=True, null=True)
    label8 = models.CharField(max_length=200, blank=True, null=True)
    label9 = models.CharField(max_length=200, blank=True, null=True)
