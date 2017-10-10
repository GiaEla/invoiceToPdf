from __future__ import unicode_literals

from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from orders.generators import generate_pdf, generate_object_number


class Offer(models.Model):
    date = models.DateTimeField('Datum')
    place = models.CharField('Kraj', max_length=100)
    offer_number = models.PositiveIntegerField('Predračun', editable=False, null=False)
    tickets = models.IntegerField(verbose_name='Karta - 30$')
    cd = models.IntegerField(verbose_name='CD - 15$')
    total_no_vat = models.DecimalField('Znesek brez DDV', max_digits=8, decimal_places=2, default=0, editable=False)
    total_with_vat = models.DecimalField('Znesek z DDV', max_digits=8, decimal_places=2, default=0, editable=False)
    recipient = models.ForeignKey(User, verbose_name='Prejemnik')
    payed = models.BooleanField('Plačano', default=False)
    pay_until = models.DateField('Rok plačila', null=True, editable=False)

    def __unicode__(self):
        return '%s %s' % (self.offer_number, self.date)

    def __str__(self):
        return '%s' % self.offer_number

    # def download_pdf(self):
    #     selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    #     for select in selected:
    #         OfferWrapper.generate_offer(select)

    class Meta:
        verbose_name = (u'predračun')
        verbose_name_plural = (u'predračuni')

    def calculate_prices(self):

        self.total_with_vat = Decimal(str(self.tickets * 30 + self.cd * 15))

        self.total_no_vat = self.total_with_vat / Decimal(str(1.22))

        super(Offer, self).save()


    def generate_pdf(self):

        html_context = {
            'products': [{'name': 'Karta', 'quantity': self.tickets, 'price_with_vat': 30.00, 'price_no_vat': 24.95},
                         {'name': 'CD', 'quantity': self.cd, 'price_with_vat': 15.00, 'price_no_vat': 12.30}],
            'offer_number': self.offer_number,
            'total_no_vat': self.total_no_vat,
            'total_with_vat': self.total_with_vat,
            'place': self.place,
            'date': self.date,
            'pay_until': self.pay_until,
        }

        pdf_path = generate_pdf('offer.html', html_context, 'offers', str(self.offer_number) + '.pdf')

        return pdf_path



    def save(self, *args, **kwargs):
        # if new offer, it generates number, otherwise it's not overwritten
        if self.offer_number is None:
            last_object = Offer.objects.all().order_by('date').last()
            self.offer_number = generate_object_number(self.date, last_object, 'offer')

        # gives a week to pay the offer
        pay_in = timedelta(days=7)
        pay_until = self.date + pay_in
        self.pay_until = pay_until
        self.calculate_prices()

        super(Offer, self).save(*args, **kwargs)

