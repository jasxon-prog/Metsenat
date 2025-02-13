from django.db import models


STUDENT_TYPE_CHOICES = [
    ('BR', 'Bakalavr'),
    ('MA', 'Magistratura'),
]

PAYMENT_CHOICES = [
    ('NQ', 'Naqd pul'),
    ('CD', 'Plastik karta'),
    ('PK', "Pul ko'chirish")
]

SPONSOR_TYPE_CHOICES = [
    ('YSH', 'Yuridik shaxs'),
    ('JSH', 'Jismoniy shaxs')
]

FILTER_CHOICES = [
    ('NEW', 'Yangi'),
    ('MD', 'Moderatsiyada'),
    ('CONFIRMATION', 'Tasdiqlangan'),
    ('CANCEL', 'Bekor qilingan')
]

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan sana')
    updated_at = models.DateTimeField(auto_now=True, verbose_name="O'zgartirilgan sana")

    class Meta:
        abstract = True


class OTM(BaseModel):
    title = models.CharField(max_length=255, verbose_name='OTM nomi')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'OTMlar'
        verbose_name_plural = 'OTMlar'


class Student(BaseModel):
    full_name = models.CharField(max_length=255, verbose_name="F.I.SH")
    phone_number = models.CharField(max_length=20, verbose_name='Telefon raqam')
    student_type = models.CharField(max_length=2, choices=STUDENT_TYPE_CHOICES, verbose_name='Talaba turi')
    otm = models.ForeignKey(OTM, on_delete=models.CASCADE, related_name='students', verbose_name="OTM ni tanlang")
    contract_amount = models.IntegerField(verbose_name='Kontart summa')

    def __str__(self):
        return f"{self.full_name} - {self.otm.title}"
    
    class Meta:
        verbose_name = 'Talabalar'
        verbose_name_plural = 'Talabalar'

class Sponsor(BaseModel):
    full_name = models.CharField(max_length=255, verbose_name='F.I.SH')
    phone_number = models.CharField(max_length=15, verbose_name='Telefon raqam')
    amount = models.IntegerField(verbose_name='Summa')
    org_name = models.CharField(max_length=200, null=True, blank=True)
    payment_type = models.CharField(max_length=2, choices=PAYMENT_CHOICES, default='CD', verbose_name="Tolo'v usuli")
    type = models.CharField(max_length=3, choices=SPONSOR_TYPE_CHOICES, default='JSH', verbose_name='Homiy turi')
    status = models.CharField(max_length=20, choices=FILTER_CHOICES, default='New')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Homiylar'
        verbose_name_plural = 'Homiylar'

class SponsorAdd(BaseModel):
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE, related_name='allocated_funds', verbose_name='Homiy')
    allocated_amount = models.IntegerField(verbose_name='Ajratilgan summa')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sponsorships', verbose_name='Talaba')

    def __str__(self):
        return f"{self.sponsor.full_name}  {self.student.full_name} ({self.allocated_amount})"
    
    class Meta:
        verbose_name = 'Homiy qo\'shish'
        verbose_name_plural = 'Homiy qo\'shish'