import zipfile
from io import BytesIO

import os

from django.conf import settings
from django.contrib import admin

# Register your models here.
from django.core.mail import EmailMessage, send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string

from orders.generators import create_pdf
from orders.models import Offer


def generate_selected_pdf(modeladmin, request, queryset):

    if len(queryset) > 1:
        zip_subdir = "Racuni_predracuni"
        zip_filename = "%s.zip" % zip_subdir

        # Open StringIO to grab in-memory ZIP contents
        s = BytesIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w")

        for obj in queryset:

            obj.generate_pdf()
            file_name = os.path.join(settings.BASE_DIR, 'offers', str(obj.offer_number) + '.pdf')


            fdir, fname = os.path.split(file_name)
            zip_path = os.path.join(zip_subdir, fname)

            # Add file, at correct path
            zf.write(file_name, zip_path)

            # Must close zip for all contents to be written
        zf.close()

        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")

        # ..and correct content-disposition
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

    elif len(queryset) == 1:
        obj = queryset[0]
        obj.generate_pdf()
        file_name = os.path.join(settings.BASE_DIR, 'offers', str(obj.offer_number) + '.pdf')

        with open(file_name, 'rb') as file_obj:
            resp = HttpResponse(file_obj, content_type="application/pdf")
            resp['Content-Disposition'] = 'attachment; filename="predracun.pdf'

    return resp

create_pdf.short_description = "Izvozi kot .pdf"


def admin_mail(modeladmin, request, queryset):
    for obj in queryset:
        subject = ''
        message = ''
        pdf_path = ''


        obj.generate_pdf()
        html_context = {
            'recipient': obj.recipient,
            'type': 'predračun',
            'date': obj.date.date()
        }
        subject = 'Predračun št.' + str(obj.offer_number)
        message = render_to_string('pdf_offer_invoice.html', html_context)
        recipient_mail = obj.recipient.email
        pdf_path = os.path.join(settings.BASE_DIR, 'offers', str(obj.offer_number) + '.pdf')


        email = EmailMessage(
            subject,
            message,
            'giacotesting@gmail.com',
            [recipient_mail],
        )

        email.attach_file(pdf_path)
        email.content_subtype = 'html'
        email.send()

send_mail.short_description = "Pošlji email"

class OfferAdmin(admin.ModelAdmin):
    readonly_fields = ('offer_number', 'total_no_vat', 'total_with_vat')
    list_display = ('offer_number', 'date', 'total_with_vat',)
    actions = [generate_selected_pdf, admin_mail]


admin.site.register(Offer, OfferAdmin)