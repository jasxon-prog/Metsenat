from django.shortcuts import render
from app.models import Sponsor, Student, SponsorAdd
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from . import serializers
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models.functions import TruncMonth
import datetime
from rest_framework import permissions
from . permissions import CustomPermission
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class SponsorListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Sponsor.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('status', 'amount')
    search_fields = ['full_name', 'phone_number']
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_serializer_class(self):
        return serializers.SponsorSerializer if self.request.method == 'POST' else serializers.SponsorListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [CustomPermission]
        return super().get_permissions()
    
    

class SponsorDetailAPIView(generics.RetrieveAPIView):
    queryset = Sponsor.objects.all()
    serializer_class = serializers.SponsorListSerializer


class StudentSponsorCreateAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.StudentSponsorSerializer


class StudentSponsorUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.SponsorStudentUpdateSerializer
    queryset = SponsorAdd.objects.all()



class StudentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Student.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ('student_type', 'otm')
    search_fields =['full_name', 'otm']

    def get_serializer_class(self):
        return serializers.StudentSerializer if self.request.method == 'POST' else serializers.StudentListSerializer
    

class StudentDetailAPIView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = serializers.StudentListSerializer


class DashboardAPIView(APIView):

    def get(self, request, *args, **kwargs):
        total_paid_amount = Sponsor.objects.aggregate(total=Sum('amount'))['total'] or 0
        total_requested_amount = Student.objects.aggregate(total=Sum('contract_amount'))['total'] or 0
        amount_need_paid = total_requested_amount - total_paid_amount
        return Response(data={
                'total_paid_amount': total_paid_amount,
                'total_requested_amount': total_requested_amount,
                'amount_need_paid': amount_need_paid
            }, status=200)

    
class DashboardGraphAPIView(APIView):

    def get(self, request):
        this_year = timezone.now().year

        student = Student.objects.filter(created_at__year=this_year).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')

        formating_student = [
            {'month': entry['month'].strftime('%Y-%m-%d'), 'count':entry['count']}
            for entry in student
        ]  if student else [{'month': None, 'count': 0}]

        sponsor = Sponsor.objects.filter(created_at__year=this_year).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')

        formating_sponsor = [
            {'month': entry['month'].strftime('%Y-%m-%d'), 'count':entry['count']}
            for entry in sponsor
        ] if student else [{'month': None, 'count': 0}] 

        return Response({
            "Student" : formating_student,
            "Sponsor" : formating_sponsor
        })