# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desidered behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models

class DrVote(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fcode = models.CharField(db_column='FCode', max_length=32, blank=True, null=True)  # Field name made lowercase.
    votecount = models.IntegerField(db_column='VoteCount', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dr_vote'


class DrFactory(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=32)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=36)  # Field name made lowercase.
    logoname = models.CharField(db_column='LogoName', max_length=32)  # Field name made lowercase.
    externinfo1 = models.CharField(db_column='ExternInfo1', max_length=128)  # Field name made lowercase.
    externinfo2 = models.CharField(db_column='ExternInfo2', max_length=128)  # Field name made lowercase.
    externinfo3 = models.CharField(db_column='ExternInfo3', max_length=128)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'dr_factory'


class DrVoteRecord(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    ucode = models.CharField(db_column='UCode', max_length=32)  # Field name made lowercase.
    votedate = models.CharField(db_column='VoteDate', max_length=10)  # Field name made lowercase.
    voteip = models.CharField(db_column='VoteIp', max_length=15)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dr_vote_record'

class DrReviewExpert(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=32)  # Field name made lowercase.
    faceimage = models.CharField(db_column='FaceImage', max_length=32)  # Field name made lowercase.
    info = models.CharField(db_column='Info', max_length=200)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=36)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'dr_review_expert'

class DrConfig(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)  # Field name made lowercase.
    startdate = models.CharField(db_column='StartDate', max_length=10)  # Field name made lowercase.
    stopdate = models.CharField(db_column='StopDate', max_length=10)  # Field name made lowercase.
    enable = models.IntegerField(db_column='Enable', blank=True, null=True)
    title = models.CharField(db_column='Title', max_length=36)  # Field name made lowercase.
    introduce = models.CharField(db_column='Introduce', max_length=2000)  # Field name made lowercase.
    logoimage = models.CharField(db_column='LogoImage', max_length=32)  # Field name made lowercase.
    zhubanorg = models.CharField(db_column='ZhuBanOrg', max_length=32)  # Field name made lowercase.
    xiebanorg = models.CharField(db_column='XieBanOrg', max_length=32)  # Field name made lowercase.
    zhichiorg = models.CharField(db_column='ZhiChiOrg', max_length=32)  # Field name made lowercase.
    xiezhuorg = models.CharField(db_column='XieZhuOrg', max_length=32)  # Field name made lowercase.

    xiezhupp = models.CharField(db_column='XieZhuPP', max_length=32)  # Field name made lowercase.
    erweima = models.CharField(db_column='ErWeiMa', max_length=32)  # Field name made lowercase.
    class Meta:
        managed = False
        db_table = 'dr_config'


