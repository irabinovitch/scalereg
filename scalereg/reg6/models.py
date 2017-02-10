from django.db import models
from scalereg.reg6 import validators
import datetime

SALUTATION_CHOICES = (
  ('Mr', 'Mr.'),
  ('Ms', 'Ms.'),
  ('Mrs', 'Mrs.'),
  ('Dr', 'Dr.'),
)

PAYMENT_CHOICES = (
  ('verisign', 'Verisign'),
  ('google', 'Google Checkout'),
  ('cash', 'Cash'),
  ('invitee', 'Invitee'),
  ('exhibitor', 'Exhibitor'),
  ('speaker', 'Speaker'),
  ('press', 'Press'),
  ('freeup', 'Free Upgrade'),
)

TICKET_CHOICES = (
  ('expo', 'Expo Only'),
  ('full', 'Full'),
  ('press', 'Press'),
  ('speaker', 'Speaker'),
  ('exhibitor', 'Exhibitor'),
  ('staff', 'Staff'),
  ('friday', 'Friday Only'),
)

class Order(models.Model):
  # basic info
  order_num = models.CharField(max_length=10, primary_key=True,
      help_text='Unique 10 upper-case letters + numbers code')
  valid = models.BooleanField(default=False)
  date = models.DateTimeField(auto_now_add=True)

  # name and address
  name = models.CharField(max_length=120)
  address = models.CharField(max_length=120)
  city = models.CharField(max_length=60)
  state = models.CharField(max_length=60)
  zip = models.CharField(max_length=20)
  country = models.CharField(max_length=60, blank=True)

  # contact info
  email = models.EmailField()
  phone = models.CharField(max_length=20, blank=True)

  # payment info
  amount = models.DecimalField(max_digits=6, decimal_places=2)
  payment_type = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
  auth_code = models.CharField(max_length=30, blank=True,
      help_text='Only used by Verisign')
  pnref = models.CharField(max_length=15, blank=True,
      help_text='Payment Network Reference ID (PNREF), a number generated by '
                'PayPal that uniquely identifies the transaction')
  resp_msg = models.CharField(max_length=60, blank=True,
      help_text='Only used by Verisign')
  result = models.CharField(max_length=60, blank=True,
      help_text='Only used by Verisign')
  already_paid_attendees = models.ManyToManyField('Attendee', blank=True,
      related_name='already_paid',
      help_text='Attendees charged multiple times on this order')

  class Meta:
    permissions = (('view_order', 'Can view order'),)

  def __unicode__(self):
    return u'%s' % self.order_num

  def save(self, *args, **kwargs):
    validators.isNotNegative(self.amount, self)
    validators.isValidOrderNumber(self.order_num, self)
    return super(Order, self).save(*args, **kwargs)


class TicketManager(models.Manager):
  def get_queryset(self):
    exclude = []
    set = super(TicketManager, self).get_queryset()
    for item in set:
      if not item.is_public():
        exclude.append(item)
    for item in exclude:
      set = set.exclude(name=item.name)
    return set

  def names(self):
    name_list = []
    for f in self.get_queryset():
      name_list.append(f.name)
    return name_list


class Ticket(models.Model):
  name = models.CharField(max_length=5, primary_key=True,
      help_text='Up to 5 letters, upper-case letters + numbers')
  description = models.CharField(max_length=60)
  type = models.CharField(max_length=10, choices=TICKET_CHOICES)
  price = models.DecimalField(max_digits=5, decimal_places=2)
  priority = models.IntegerField(
      help_text='Ordering priority, lower numbers first')
  public = models.BooleanField(default=False,
      help_text='Publicly available on the order page')
  cash = models.BooleanField(default=False,
      help_text='Available for cash purchase')
  upgradable = models.BooleanField(default=False,
      help_text='Eligible for upgrades')
  limit = models.PositiveIntegerField(
      help_text='Maximum number of tickets, 0 for unlimited')
  start_date = models.DateField(null=True, blank=True,
      help_text='Available on this day')
  end_date = models.DateField(null=True, blank=True,
      help_text='Not Usable on this day')

  objects = models.Manager()
  public_objects = TicketManager()

  @staticmethod
  def ticket_cost(ticket, items, promo):
    # TODO remove this without double-apply promo.
    ticket = Ticket.objects.get(name=ticket.name)
    price_modifier = promo.price_modifier if promo else 1
    ticket_price = ticket.price
    if promo and (promo.applies_to_all or
                  ticket in promo.applies_to.all()):
      ticket_price *= price_modifier

    items_price = 0
    for item in items:
      # TODO remove this without double-apply promo.
      item = Item.objects.get(name=item.name)
      additional_cost = item.price
      if item.promo:
        additional_cost *= price_modifier
      items_price += additional_cost
      if item.ticket_offset:
        ticket_price = 0
    return ticket_price + items_price

  def is_public(self):
    if not self.public:
      return False
    today = datetime.date.today()
    if self.start_date and self.start_date > today:
      return False
    if self.end_date and self.end_date <= today:
      return False
    return True

  class Meta:
    permissions = (('view_ticket', 'Can view ticket'),)

  def __unicode__(self):
    return u'%s' % self.name

  def save(self, *args, **kwargs):
    validators.isAllCapsDigits(self.name, self)
    validators.isNotNegative(self.price, self)
    validators.isValidStartStopDates(self.start_date, self)
    return super(Ticket, self).save(*args, **kwargs)


class PromoCodeManager(models.Manager):
  def get_queryset(self):
    exclude = []
    set = super(PromoCodeManager, self).get_queryset()
    for item in set:
      if not item.is_active():
        exclude.append(item)
    for item in exclude:
      set = set.exclude(name=item.name)
    return set

  def names(self):
    name_list = []
    for f in self.get_queryset():
      name_list.append(f.name)
    return name_list


class PromoCode(models.Model):
  name = models.CharField(max_length=5, primary_key=True,
      help_text='Up to 5 letters, upper-case letters + numbers')
  description = models.CharField(max_length=60)

  price_modifier = models.DecimalField(max_digits=3, decimal_places=2,
      help_text='This is the price multiplier, i.e. for 0.4, $10 becomes $4.')
  active = models.BooleanField(default=False)
  start_date = models.DateField(null=True, blank=True,
      help_text='Available on this day')
  end_date = models.DateField(null=True, blank=True,
      help_text='Not Usable on this day')
  applies_to = models.ManyToManyField(Ticket, blank=True)
  applies_to_all = models.BooleanField(default=False,
      help_text='Applies to all tickets')

  objects = models.Manager()
  active_objects = PromoCodeManager()

  def is_active(self):
    if not self.active:
      return False
    today = datetime.date.today()
    if self.start_date and self.start_date > today:
      return False
    if self.end_date and self.end_date <= today:
      return False
    return True

  def is_applicable_to(self, ticket):
    if self.applies_to_all:
      return True
    return ticket in self.applies_to.all()

  class Meta:
    permissions = (('view_promocode', 'Can view promo code'),)

  def __unicode__(self):
    return self.name

  def save(self, *args, **kwargs):
    validators.isAllCapsDigits(self.name, self)
    validators.isPositive(self.price_modifier, self)
    validators.isValidStartStopDates(self.start_date, self)
    return super(PromoCode, self).save(*args, **kwargs)


class Item(models.Model):
  name = models.CharField(max_length=4,
      help_text='Unique, up to 4 upper-case letters / numbers')
  description = models.CharField(max_length=60)

  price = models.DecimalField(max_digits=5, decimal_places=2)

  active = models.BooleanField(default=False)
  pickup = models.BooleanField(default=False,
      help_text='Can we track if this item gets picked up?')
  promo = models.BooleanField(default=False,
      help_text='Price affected by promo code?')
  ticket_offset = models.BooleanField(default=False,
      help_text='Item offsets ticket price?')
  applies_to = models.ManyToManyField(Ticket, blank=True)
  applies_to_all = models.BooleanField(default=False,
      help_text='Applies to all tickets')

  class Meta:
    permissions = (('view_item', 'Can view item'),)

  def __unicode__(self):
    return u'%s (%s)' % (self.description, self.name)

  def save(self, *args, **kwargs):
    validators.isAllCapsDigits(self.name, self)
    validators.isNotNegative(self.price, self)
    return super(Item, self).save(*args, **kwargs)


# base class
class Answer(models.Model):
  question = models.ForeignKey('Question')
  text = models.CharField(max_length=200)

  class Meta:
    permissions = (('view_answer', 'Can view answer'),)

  def __str_text__(self):
    if len(self.text) > 50:
      return '%s...' % self.text[:50]
    return '%s' % self.text

  def __unicode__(self):
    return u'(%d) %s' % (self.question.id, self.__str_text__())


class ListAnswer(Answer):
  pass


class TextAnswer(Answer):
  pass


# base class
class Question(models.Model):
  text = models.CharField(max_length=200)
  active = models.BooleanField(default=False)
  applies_to_tickets = models.ManyToManyField(Ticket, blank=True)
  applies_to_items = models.ManyToManyField(Item, blank=True)
  applies_to_all = models.BooleanField(default=False,
      help_text='Applies to all tickets')

  class Meta:
    permissions = (('view_question', 'Can view question'),)

  def get_answers(self):
    return Answer.objects.filter(question=self.id)

  def __unicode__(self):
    if len(self.text) > 37:
      return u'%s...' % self.text[:37]
    return u'%s' % self.text


class ListQuestion(Question):
  pass


class TextQuestion(Question):
  max_length = models.IntegerField()


class Attendee(models.Model):
  # badge info
  badge_type = models.ForeignKey(Ticket)
  order = models.ForeignKey(Order, blank=True, null=True)
  valid = models.BooleanField(default=False)
  checked_in = models.BooleanField(default=False,
      help_text='Only for valid attendees')

  # attendee name
  salutation = models.CharField(max_length=10, choices=SALUTATION_CHOICES,
      blank=True)
  first_name = models.CharField(max_length=60)
  last_name = models.CharField(max_length=60)
  title = models.CharField(max_length=60, blank=True)
  org = models.CharField(max_length=60, blank=True)

  # contact info
  email = models.EmailField()
  zip = models.CharField(max_length=20)
  phone = models.CharField(max_length=20, blank=True)

  # etc
  promo = models.ForeignKey(PromoCode, blank=True, null=True)
  ordered_items = models.ManyToManyField(Item, blank=True)
  obtained_items = models.CharField(max_length=60, blank=True,
      help_text='comma separated list of items')
  can_email = models.BooleanField(default=False)
  answers = models.ManyToManyField(Answer, blank=True)

  def ticket_cost(self):
    return Ticket.ticket_cost(self.badge_type, self.ordered_items.all(),
                              self.promo)

  def full_name(self):
    return '%s %s' % (self.first_name, self.last_name)

  class Meta:
    permissions = (('view_attendee', 'Can view attendee'),)

  def __unicode__(self):
    return u'%s (%s) ' % (self.id, self.email)

  def save(self, *args, **kwargs):
    validators.isValidAttendeeCheckin(self.checked_in, self)
    return super(Attendee, self).save(*args, **kwargs)


class TempOrder(models.Model):
  order_num = models.CharField(max_length=10, primary_key=True,
      help_text='Unique 10 upper-case letters + numbers code')
  attendees = models.TextField(blank=True)
  upgrade = models.ForeignKey('Upgrade', blank=True, null=True)
  date = models.DateTimeField(auto_now_add=True)

  def attendees_list(self):
    return [int(x) for x in self.attendees.split(',')]

  def upgrades_list(self):
    return [int(x) for x in self.attendees.split(',')]

  def __unicode__(self):
    return '%s' % self.order_num

  def save(self, *args, **kwargs):
    validators.isValidTempOrder(None, self)
    return super(TempOrder, self).save(*args, **kwargs)


class Coupon(models.Model):
  code = models.CharField(max_length=10, primary_key=True,
      help_text='Unique 10 upper-case letters + numbers code')
  badge_type = models.ForeignKey(Ticket)
  order = models.ForeignKey(Order)
  used = models.BooleanField(default=False)
  max_attendees = models.PositiveSmallIntegerField()
  expiration = models.DateField(null=True, blank=True,
      help_text='Not usable on this day')

  def is_valid(self):
    if self.used:
      return False
    if self.expiration and self.expiration <= datetime.date.today():
      return False
    return True

  class Meta:
    permissions = (('view_coupon', 'Can view coupon'),)

  def save(self, *args, **kwargs):
    validators.isValidOrderNumber(self.code, self)
    return super(Coupon, self).save(*args, **kwargs)


class Reprint(models.Model):
  attendee =  models.ForeignKey(Attendee)
  count = models.IntegerField()

  class Meta:
    permissions = (('view_reprint', 'Can view reprint'),)

  def __unicode__(self):
    return '%s %d' % (self.attendee, self.count)


class Upgrade(models.Model):
  attendee = models.ForeignKey(Attendee)
  valid = models.BooleanField(default=False)

  old_badge_type = models.ForeignKey(Ticket, related_name='old_badge_type')
  old_ordered_items = models.ManyToManyField(Item, blank=True,
      related_name='old_ordered_items')
  old_order = models.ForeignKey(Order, related_name='old_order')

  new_badge_type = models.ForeignKey(Ticket)
  new_ordered_items = models.ManyToManyField(Item, blank=True)
  new_order = models.ForeignKey(Order, blank=True, null=True)

  def upgrade_cost(self):
    old_total = Ticket.ticket_cost(self.old_badge_type,
                                   self.old_ordered_items.all(),
                                   self.attendee.promo)
    new_total = Ticket.ticket_cost(self.new_badge_type,
                                   self.new_ordered_items.all(),
                                   self.attendee.promo)
    return new_total - old_total

  class Meta:
    permissions = (('view_upgrade', 'Can view upgrade'),)

  def __unicode__(self):
    return '%s' % self.attendee
