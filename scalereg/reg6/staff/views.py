# Create your views here.

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from scalereg.common.utils import services_perm_checker
from scalereg.common.views import handler500
from scalereg.reg6 import models
from scalereg.reg6 import validators
from scalereg.reg6.views import GenerateOrderID
from scalereg.reg6.views import NotifyAttendee

@login_required
def index(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')
  return render_to_response('reg6/staff/index.html',
    {'title': 'Staff Page',
    })


@login_required
def CheckIn(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method == 'GET':
    return render_to_response('reg6/staff/checkin.html',
      {'title': 'Attendee Check In',
      })

  attendees = []
  if request.POST.get('verisign'):
    orders = models.Order.objects.filter(payment_type='verisign',
        pnref=request.POST.get('verisign'))
    if orders.count() == 1:
      attendees = models.Attendee.objects.filter(valid=True, order=orders[0])

  if not attendees and request.POST['express']:
    # TODO: Duplicated from CheckIn() in reg6/views.py.
    code = request.POST['express'].lower()
    success = len(code) == 10
    if success:
      id_str = code[:4]
      try:
        attendee_id = int(id_str)
        attendee = models.Attendee.objects.get(id=attendee_id)
      except:
        success = False

    if success:
      success = attendee.checkin_code() == code

    if success:
      attendees = [attendee]

  if not attendees and request.POST.get('last_name'):
    attendees = models.Attendee.objects.filter(valid=True,
        last_name__icontains=request.POST.get('last_name'))

  if not attendees and request.POST.get('zip'):
    attendees = models.Attendee.objects.filter(valid=True,
        zip=request.POST.get('zip'))

  attendees = [att for att in attendees]
  if request.POST.get('last_name'):
    bad_attendees = models.Attendee.objects.filter(valid=False,
        last_name__icontains=request.POST.get('last_name'))
    attendees += bad_attendees

  for att in attendees:
    if att.checked_in:
      try:
        rp = models.Reprint.objects.get(attendee=att)
        count = rp.count
      except:
        count = 0
      att.rp_count = count + 1

  return render_to_response('reg6/staff/checkin.html',
    {'title': 'Attendee Check In',
     'attendees': attendees,
     'express': request.POST.get('express'),
     'last_name': request.POST.get('last_name'),
     'verisign': request.POST.get('verisign'),
     'zip': request.POST.get('zip'),
     'search': 1,
    })


@login_required
def FinishCheckIn(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method != 'POST':
    return HttpResponseRedirect('/reg6/')

  if 'id' not in request.POST:
    return handler500(request, msg='No ID')

  try:
    attendee = models.Attendee.objects.get(id=request.POST.get('id'))
  except models.Attendee.DoesNotExist:
    return handler500(request, msg='We could not find your registration')

  try:
    attendee.checked_in = True
    attendee.save()
    kiosk_agents = models.KioskAgent.objects.filter(attendee=attendee)
    for agent in kiosk_agents:
      agent.delete()
  except:
    return handler500(request, msg='We encountered a problem with your checkin')

  return render_to_response('reg6/staff/finish_checkin.html',
    {'title': 'Attendee Check In',
     'attendee': attendee,
    })


@login_required
def CashPayment(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  tickets = models.Ticket.objects.filter(cash=True)
  if request.method == 'GET':
    return render_to_response('reg6/staff/cash.html',
      {'title': 'Cash Payment',
       'tickets': tickets,
      })

  for var in ['FIRST', 'LAST', 'EMAIL', 'ZIP', 'TICKET']:
    if var not in request.POST or not request.POST.get(var):
      return render_to_response('reg6/staff/cash.html',
        {'title': 'Cash Payment',
         'tickets': tickets,
         'failure': 'missing data: no %s field' % var,
        })

  try:
    ticket = models.Ticket.objects.get(name=request.POST.get('TICKET'))
  except:
    return render_to_response('reg6/staff/cash.html',
      {'title': 'Cash Payment',
       'tickets': tickets,
       'failure': 'cannot find ticket type',
      })

  order = models.Order()
  bad_order_nums = [ x.order_num for x in models.TempOrder.objects.all() ]
  bad_order_nums += [ x.order_num for x in models.Order.objects.all() ]
  order.order_num = GenerateOrderID(bad_order_nums)
  assert order.order_num
  order.valid = True
  order.name = '%s %s' % (request.POST.get('FIRST'), request.POST.get('LAST'))
  order.address = 'Cash'
  order.city = 'Cash'
  order.state = 'Cash'
  order.zip = request.POST.get('ZIP')
  order.email = request.POST.get('EMAIL')
  # FIXME add a field in the Model or something.
  if ticket.name in ('GUEST', 'KID', 'STAFF'):
    order.payment_type = 'invitee'
  else:
    order.payment_type = 'cash'
  order.amount = ticket.price

  attendee = models.Attendee()
  attendee.first_name = request.POST.get('FIRST')
  attendee.last_name = request.POST.get('LAST')
  attendee.zip = request.POST.get('ZIP')
  attendee.email = request.POST.get('EMAIL')
  attendee.valid = True
  attendee.checked_in = True
  attendee.can_email = False
  attendee.order = order
  attendee.badge_type = ticket
  try:
    attendee.save()
    order.save()
  except: # FIXME catch the specific db exceptions
    attendee.delete()
    order.delete()
    return render_to_response('reg6/staff/cash.html',
      {'title': 'Cash Payment',
       'tickets': tickets,
       'failure': 'cannot save order, bad data?',
      })

  return render_to_response('reg6/staff/cash.html',
    {'title': 'Cash Payment',
     'success': True,
     'tickets': tickets,
    })


@login_required
def CashPaymentRegistered(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method == 'GET':
    return handler500(request, msg='POST only.')

  if not 'id' in request.POST or not request.POST.get('id'):
    return handler500(request, msg='missing data: no %s field' % var)

  try:
    attendee = models.Attendee.objects.get(id=request.POST.get('id'))
  except:
    return handler500(request, msg='cannot find attendee')

  if not 'action' in request.POST or request.POST.get('action') != 'pay':
    return render_to_response('reg6/staff/cash_registered.html',
      {'title': 'Cash Payment For Registered Attendee',
       'attendee': attendee,
      })

  order = models.Order()
  bad_order_nums = [ x.order_num for x in models.TempOrder.objects.all() ]
  bad_order_nums += [ x.order_num for x in models.Order.objects.all() ]
  order.order_num = GenerateOrderID(bad_order_nums)
  assert order.order_num
  order.valid = True
  order.name = '%s %s' % (attendee.first_name, attendee.last_name)
  order.address = 'Cash'
  order.city = 'Cash'
  order.state = 'Cash'
  order.zip = attendee.zip
  order.email = attendee.email
  order.payment_type = 'cash'
  order.amount = attendee.ticket_cost()

  attendee.valid = True
  attendee.checked_in = True
  attendee.order = order
  try:
    attendee.save()
    order.save()
  except: # FIXME catch the specific db exceptions
    attendee.delete()
    order.delete()
    return handler500(request, msg='cannot save order, bad data?')

  return render_to_response('reg6/staff/cash_registered.html',
    {'title': 'Cash Payment For Registered Attendee',
     'attendee': attendee,
     'success': True,
    })


@login_required
def Email(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method == 'GET':
    return HttpResponseRedirect('/reg6/staff/checkin/')

  EMAIL_TEMPLATE = 'reg6/staff/email.html'
  if not 'id' in request.POST or not request.POST.get('id'):
    return render_to_response(EMAIL_TEMPLATE,
      {'title': 'Attendee Email Invalid',
       'attendee': None,
      })

  try:
    attendee = models.Attendee.objects.get(id=int(request.POST.get('id')))
    NotifyAttendee(attendee)
  except:
    attendee = None

  return render_to_response(EMAIL_TEMPLATE,
      {'title': 'Attendee Email',
       'attendee': attendee,
      })


@login_required
def Reprint(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method == 'GET':
    return HttpResponseRedirect('/reg6/staff/checkin/')

  REPRINT_TEMPLATE = 'reg6/staff/reprint.html'
  if not request.POST.get('id'):
    return render_to_response(REPRINT_TEMPLATE,
        {'title': 'Attendee Reprint Invalid',
         'reprint': None,
        })

  try:
    attendee = models.Attendee.objects.get(id=int(request.POST.get('id')))
    try:
      reprint = models.Reprint.objects.get(attendee=attendee)
    except:
      reprint = models.Reprint()
      reprint.attendee = attendee
      reprint.count = 0

    kiosk_agents = models.KioskAgent.objects.filter(attendee=attendee)
    for agent in kiosk_agents:
      agent.delete()

    reprint.count += 1
    reprint.save()
    return render_to_response(REPRINT_TEMPLATE,
        {'title': 'Attendee Reprint',
         'reprint': reprint,
        })
  except:
    return render_to_response(REPRINT_TEMPLATE,
        {'title': 'Attendee Reprint Error',
         'reprint': None,
        })


@login_required
def UpdateAttendee(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method == 'GET':
    return handler500(request, msg='POST only.')

  if not 'id' in request.POST or not request.POST.get('id'):
    return handler500(request, msg='missing data: no %s field' % var)

  try:
    attendee = models.Attendee.objects.get(id=request.POST.get('id'))
  except:
    return handler500(request, msg='cannot find attendee')

  if not 'action' in request.POST or request.POST.get('action') != 'update':
    return render_to_response('reg6/staff/update_attendee.html',
      {'title': 'Update Attendee',
       'attendee': attendee,
       'orig_salutation': attendee.salutation,
       'orig_first_name': attendee.first_name,
       'orig_last_name': attendee.last_name,
       'orig_title': attendee.title,
       'orig_org': attendee.org,
       'orig_email': attendee.email,
       'orig_zip': attendee.zip,
       'orig_phone': attendee.phone,
       'salutations': models.SALUTATION_CHOICES,
      })

  for var in ['SALUTATION', 'FIRST', 'LAST', 'TITLE', 'ORG', 'EMAIL', 'ZIP',
              'PHONE', 'ORIG_SALUTATION', 'ORIG_FIRST', 'ORIG_LAST',
              'ORIG_TITLE', 'ORIG_ORG', 'ORIG_EMAIL', 'ORIG_ZIP', 'ORIG_PHONE']:
    if var not in request.POST:
      return handler500(request, msg='missing data: no %s field' % var)

  attendee.salutation = request.POST.get('SALUTATION')
  attendee.first_name = request.POST.get('FIRST')
  attendee.last_name = request.POST.get('LAST')
  attendee.title = request.POST.get('TITLE')
  attendee.org = request.POST.get('ORG')
  attendee.email = request.POST.get('EMAIL')
  attendee.zip = request.POST.get('ZIP')
  attendee.phone = request.POST.get('PHONE')
  try:
    attendee.full_clean()
  except:
    return render_to_response('reg6/staff/update_attendee.html',
      {'title': 'Update Attendee',
       'attendee': attendee,
       'orig_salutation': request.POST.get('ORIG_SALUTATION'),
       'orig_first_name': request.POST.get('ORIG_FIRST'),
       'orig_last_name': request.POST.get('ORIG_LAST'),
       'orig_title': request.POST.get('ORIG_TITLE'),
       'orig_org': request.POST.get('ORIG_ORG'),
       'orig_email': request.POST.get('ORIG_EMAIL'),
       'orig_zip': request.POST.get('ORIG_ZIP'),
       'orig_phone': request.POST.get('ORIG_PHONE'),
       'salutations': models.SALUTATION_CHOICES,
       'error': True,
      })

@login_required
def UpdateAttendee(request):
  can_access = services_perm_checker(request.user, request.path)
  if not can_access:
    return HttpResponseRedirect('/accounts/profile/')

  if request.method == 'GET':
    return handler500(request, msg='POST only.')

  if not 'id' in request.POST or not request.POST['id']:
    return handler500(request, msg='missing data: no %s field' % var)

  try:
    attendee = models.Attendee.objects.get(id=request.POST['id'])
  except:
    return handler500(request, msg='cannot find attendee')

  if not 'action' in request.POST or request.POST['action'] != 'update':
    return render_to_response('reg6/staff/update_attendee.html',
      {'title': 'Update Attendee',
       'attendee': attendee,
       'orig_salutation': attendee.salutation,
       'orig_first_name': attendee.first_name,
       'orig_last_name': attendee.last_name,
       'orig_title': attendee.title,
       'orig_org': attendee.org,
       'orig_email': attendee.email,
       'orig_zip': attendee.zip,
       'orig_phone': attendee.phone,
       'salutations': models.SALUTATION_CHOICES,
      })

  for var in ['SALUTATION', 'FIRST', 'LAST', 'TITLE', 'ORG', 'EMAIL', 'ZIP',
              'PHONE', 'ORIG_SALUTATION', 'ORIG_FIRST', 'ORIG_LAST',
              'ORIG_TITLE', 'ORIG_ORG', 'ORIG_EMAIL', 'ORIG_ZIP', 'ORIG_PHONE']:
    if var not in request.POST:
      return handler500(request, msg='missing data: no %s field' % var)

  attendee.salutation = request.POST['SALUTATION']
  attendee.first_name = request.POST['FIRST']
  attendee.last_name = request.POST['LAST']
  attendee.title = request.POST['TITLE']
  attendee.org = request.POST['ORG']
  attendee.email = request.POST['EMAIL']
  attendee.zip = request.POST['ZIP']
  attendee.phone = request.POST['PHONE']
  try:
    attendee.full_clean()
  except:
    return render_to_response('reg6/staff/update_attendee.html',
      {'title': 'Update Attendee',
       'attendee': attendee,
       'orig_salutation': request.POST['ORIG_SALUTATION'],
       'orig_first_name': request.POST['ORIG_FIRST'],
       'orig_last_name': request.POST['ORIG_LAST'],
       'orig_title': request.POST['ORIG_TITLE'],
       'orig_org': request.POST['ORIG_ORG'],
       'orig_email': request.POST['ORIG_EMAIL'],
       'orig_zip': request.POST['ORIG_ZIP'],
       'orig_phone': request.POST['ORIG_PHONE'],
       'salutations': models.SALUTATION_CHOICES,
       'error': True,
      })

  try:
    attendee.save()
  except: # FIXME catch the specific db exceptions
    return handler500(request, msg='cannot save attendee update, bad data?')

  return render_to_response('reg6/staff/update_attendee.html',
    {'title': 'Cash Payment For Registered Attendee',
     'attendee': attendee,
     'orig_salutation': request.POST.get('ORIG_SALUTATION'),
     'orig_first_name': request.POST.get('ORIG_FIRST'),
     'orig_last_name': request.POST.get('ORIG_LAST'),
     'orig_title': request.POST.get('ORIG_TITLE'),
     'orig_org': request.POST.get('ORIG_ORG'),
     'orig_email': request.POST.get('ORIG_EMAIL'),
     'orig_zip': request.POST.get('ORIG_ZIP'),
     'orig_phone': request.POST.get('ORIG_PHONE'),
     'salutations': models.SALUTATION_CHOICES,
     'success': True,
    })
