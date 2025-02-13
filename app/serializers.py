from rest_framework import serializers
from app.models import Sponsor, Student, SponsorAdd
from django.db.models import Sum
import re



class SponsorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sponsor
        fields = ('full_name', 'phone_number', 'amount', 'type', 'org_name')
        
    # POST, PATCH, PUT
    def validate(self, attrs):

        phone_number = attrs.get('phone_number') 
        type = attrs.get('type')
        org_name = attrs.get('org_name')

        regex = r'^\+998\d{9}$'
        if not re.match(regex, phone_number):
            raise serializers.ValidationError({
                'error': 'Telefon raqam noto\'g\'ri kiritildi'
            }, code=400)

        if type == 'JSH' and org_name:
            raise serializers.ValidationError({
                'error': 'Jismoniy shaxslar uchun organizatsiya nomi shart emas'
            }, code=400)

        if type == 'YSH' and not org_name:
            raise serializers.ValidationError({
                'error': 'Yuridik shaxslar uchun organizatsiya nomi majburiy'
            }, code=400)
        
        return super().validate(attrs)
    
    def validate_org_name(self, value):
            return value or None
    
class SponsorListSerializer(serializers.ModelSerializer):
    spent_amount = serializers.SerializerMethodField()  # custm field
     
    class Meta:
        model = Sponsor
        exclude = ('org_name', 'payment_type')

    def get_spent_amount(self, obj):
        return obj.allocated_funds.aggregate(total=Sum('allocated_amount'))['total'] or 0
    

class StudentSponsorSerializer(serializers.ModelSerializer):

    class Meta:
        model = SponsorAdd
        fields = '__all__'

    def validate(self, attrs):
        student = attrs.get('student')
        sponsor = attrs.get('sponsor')
        allocated_amount = attrs.get('allocated_amount')

        # studentga ortiqcha pul berish holati
        student_received_money = student.sponsorships.aggregate(total=Sum('allocated_amount'))['total'] or 0
        diff = student.contract_amount - student_received_money
        if diff < allocated_amount:
            raise serializers.ValidationError({
                'error': f'Bu talaba maksimal miqdorda {diff} so\'m pul bera olasiz'
            })

        # sponsorga pul yetishmasligi
        sponsor_spent_money = sponsor.allocated_funds.aggregate(total=Sum('allocated_amount'))['total'] or 0
        diff = sponsor.amount - sponsor_spent_money
        if diff  < allocated_amount:
            raise serializers.ValidationError({
                'error': f'Bu homiyda {diff} so\'m pul qolgan'
            })
        return attrs
    

class SponsorStudentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SponsorAdd
        fields = ('sponsor', 'allocated_amount')

    def update(self, instance, validated_data):
        student = instance.student
        student_total_received = instance.student.sponsorships.aggregate(total=Sum('allocated_amount'))['total'] or 0

        if 'amount' in validated_data and 'sponsor' in validated_data:
            if validated_data['sponsor'] == instance.sponsor and validated_data['amount'] != instance.amount:
                sponsor_amount = instance.sponsor.amount
                allocated_amount = instance.sponsor.allocated_funds.aggregate(total=Sum('allocated_amount'))['total'] or 0 - instance.amount
                if sponsor_amount - allocated_amount < validated_data['amount']:
                    raise serializers.ValidationError({
                        'error': f"Bu homiyda {sponsor_amount - allocated_amount} so'm qoldiq mavjud"
                    })
                if student.contract_amount - student_total_received - instance.amount < validated_data['amount']:
                    raise serializers.ValidationError({
                        'error': f"Bu talabaga {student.contract_amount - student_total_received - instance.amount} so'm berish mumkin"
                    })
            elif validated_data['sponsor'] != instance.sponsor and validated_data['amount'] == instance.amount:
                sponsor = validated_data['sponsor']
                sponsor_spent_amount = sponsor.allocated_funds.aggregate(total=Sum('allocated_amount'))['total'] or 0
                if sponsor.amount - sponsor_spent_amount < instance.amount:
                    raise serializers.ValidationError({
                        'error': f"Bu homiyda {sponsor.amount - sponsor_spent_amount} so'm mavjud"
                    })
            elif validated_data['sponsor'] != instance.sponsor and validated_data['amount'] != instance.amount:
                sponsor = validated_data['sponsor']
                sponsor_spent_money = sponsor.allocated_funds.aggregate(total=Sum('allocated_amount'))['total'] or 0

                if sponsor.amount - sponsor_spent_money < validated_data['amount']:
                    raise serializers.ValidationError({
                        'error': f"Bu homiyda {sponsor.amount - sponsor_spent_money} so'm mavjud"
                    })
                
                if student.contract_amount - (student_total_received - instance.amount) < validated_data['amount']:
                    raise serializers.ValidationError({
                        'error': f"Bu talabaga {student.contract_amount - (student_total_received - instance.amount)} so'm berish mumkin"
                    })
        return super().update(instance, validated_data)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ('full_name', 'phone_number', 'student_type', 'otm', 'contract_amount')

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        regex = regex = r'^\+998\d{9}$'
        if not re.match(regex, phone_number):
            raise serializers.ValidationError({
                'error': 'Telefon raqam noto\'g\'ri kiritildi'
            }, code=400)
        return super().validate(attrs)
    

class StudentListSerializer(serializers.ModelSerializer):
    allocated_amount = serializers.SerializerMethodField()

    class Meta:
        model = Student
        exclude = ['phone_number']

    def get_allocated_amount(self, obj):
        return obj.sponsorships.aggregate(total=Sum('allocated_amount'))['total'] or 0