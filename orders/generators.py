from django.template import Template
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.conf import settings

from decimal import *
from time import gmtime, strftime
import pdfkit
import os


def generate_object_number(date, last_object, type_of_object):
    """
    generates number for invoices and offers in form - last two numbers of a year + serial number
    :param date: date of invoice or offer
    :param last_object: last created object in current year
    :param type: invoice or offer
    :return: generated invoice or offer number
    """

    if not last_object:
        yr = str(date.year)
        generated_number = int(yr[2:] + '0001')

    elif type_of_object == "offer":
        generated_number = last_object.offer_number + 1

    else:
        generated_number = 0

    return generated_number



def generate_pdf(template, context, dir_name, file_name):
    """

    :param template:
    :param context:
    :param dir_name:
    :param file_name:
    :return:
    """

    html_string = render_to_string(template, context)


    relative_path = dir_name + '/' + file_name

    file_path = os.path.join(settings.BASE_DIR, relative_path)

    pdfkit.from_string(html_string, file_path)

    return relative_path


