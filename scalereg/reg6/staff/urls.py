from django.conf.urls import *

urlpatterns = patterns('',
    (r'^$', 'scalereg.reg6.staff.views.index'),
    (r'^checkin/$', 'scalereg.reg6.staff.views.CheckIn'),
    (r'^finish_checkin/$', 'scalereg.reg6.staff.views.FinishCheckIn'),
    (r'^cash_payment/$', 'scalereg.reg6.staff.views.CashPayment'),
    (r'^reprint/$', 'scalereg.reg6.staff.views.Reprint'),
    (r'^update_attendee/$', 'scalereg.reg6.staff.views.UpdateAttendee'),
)
