"""Открытый банк заданий ЕГЭ.

Parsing using Celery tasks.

"""
import time
import re
import os
import redis
import pickle
from celery import shared_task
from celery import chain
import requests
import hashlib
import logging
import lxml.html
from lxml.cssselect import CSSSelector as S
from ..models import Subject
from django.template.defaultfilters import slugify
from unidecode import unidecode
from edu import subject_slug
from raven.contrib.django.raven_compat.models import client
from lxml import etree  # noqa
from core.tasks import get
log = logging.getLogger(__name__)


@shared_task
def ege_subjects_and_urls(*args):
    """Scans a root URL http://www.fipi.ru/content/otkrytyy-bank-zadaniy-ege

    Returns a list of pairs [(title.lower().capitalize(), url), ...]

    Example:

    >>> subjects_and_urls()
    >>> [('русский язык', 'http://85.142.162.119/os11/xmodules/...'), ...]

    """
    try:
        url = "http://www.fipi.ru/content/otkrytyy-bank-zadaniy-ege"
        tree = lxml.html.fromstring(get(url))
        links = S('div.content table a[href^="http://85."]')(tree)
        res = [(" ".join(el.text_content().split()).lower().capitalize(),
                el.get('href'))
               for el in links]

        subjects = (title for title, url in res)
        create_subjects(*subjects)
        # TODO: message if len(res) <> 15  (15 now)
        return res
    except:
        client.captureException()
        return []


@shared_task
def create_subjects(*args):
    try:
        for title in args:
            slug = subject_slug.get(
                title,
                slugify(unidecode(title))
            )
            subject, created = Subject.objects.get_or_create(
                name=title,
                slug=slug
            )
    except:
        client.captureException()


# http://85.142.162.119/os11/xmodules/qprint/openlogin.php?proj=B9ACA5BBB2E19E434CD6BEC25284C67F
@shared_task
def get_subject_sections(subject_url, *args):
    """Получить разделы по предмету вместе с ссылками

    Для предмета "Информатика":

    [('Информация и информационные процессы',
    'http://85.142.162.119/.../qsearch.php?theme_guid=...&proj_guid=...'),
    ('Информационная деятельность человека',
    'http://85.142.162.119/...'), ...]

    """
    try:
        log.debug("getting sections...")
        html = get(subject_url)
        tree = lxml.html.fromstring(html)
        links = S('td.coursebody a[href^="qsearch.php"]')(tree)
        res = [(" ".join(el.text_content().split()).lower().capitalize(),
                "http://85.142.162.119/os11/xmodules/qprint/"+el.get('href'))
               for el in links]
        for title, url in res:
            log.debug(title)
        return res
    except:
        client.captureException()


@shared_task
def process_sections(sections, *args):
    """Пройтись по всем разделам предмета.

    Parameters
    ----------
    section_title : str
       Заголовок раздела
       ("Информация и информационные процессы")

    url : str
       адрес первой страницы с задачами
    """
    total_pages = 0
    count = 1
    try:
        for section_title, url in sections:
            log.debug('Processing "{}" ({}/{})...'.format(
                section_title,
                count,
                len(args)
            ))
            html = get(url)
            tree = lxml.html.fromstring(html)
            pages = S('span.Walk a')(tree)
            pages = [int(p.text_content().strip('[]')) for p in pages]
            pages.append(0)
            total_pages = max(pages)
            count += 1

            time.sleep(5)

            chain(
                extract_tasks_from_url.s(url),
                process_tasks.s(),
            )()

            time.sleep(5)

            # for i in range(1, total_pages-1)

            # print(total_pages)
            # break
    except:
        client.captureException()


@shared_task
def extract_tasks_from_url(url):
    """Return a list of tasks"""
    html = get(url)
    tree = lxml.html.fromstring(html)
    forms = S('form[name="checkform"]')(tree)
    # tds = S('form[name="checkform"] table td')(tree)
    res = []
    for form in forms:
        guid = ''
        try:
            guid = S('input[name="guid"]')(form)[0]
        except:
            client.captureException()
        for td in S('table td')(form):
            html = ''
            for el in td.xpath("child::node()"):
                if isinstance(el, lxml.etree._ElementUnicodeResult):
                    html += str(el)
                else:
                    html += etree.tostring(el, encoding='unicode')
            res.append((guid, html))
            # log.debug(tag_contents(td).strip())
            # print(td.text_content())
    return res


@shared_task
def process_tasks(tasks):
    for task_info in tasks:
        process_task.delay(*task_info)


@shared_task
def process_task(guid, html):
    return 'TODO: create "{}" task'.format(guid)


def tag_contents(tag):
    if isinstance(tag, lxml.etree._ElementStringResult) or \
       isinstance(tag, lxml.etree._ElementUnicodeResult):
        return str(tag)

    res = []
    prev = None
    for el in tag.xpath("child::node()"):
        # is_text_element = isinstance(tag, lxml.etree._ElementUnicodeResult)
        txt = tag_to_text(el)
        # if prev is not None and isinstance(prev, lxml.etree._ElementUnicodeResult) \
        #    and el.tag == 'p':
        # if not isinstance(el, lxml.etree._ElementUnicodeResult) and \
        #    el.tag == 'p' and prev is not None:
        #     res[-1] = res[-1].rstrip()
        res.append(txt)
        prev = el

    # if tag.tail is not None:
    #     res.append(tag.tail)
    return "".join(res)


def tag_to_text(tag):
    res = []
    contents = tag_contents(tag)
    empty = not bool(contents.strip())

    if isinstance(tag, lxml.etree._ElementStringResult) or \
       isinstance(tag, lxml.etree._ElementUnicodeResult):
        return str(tag)

    # b
    elif tag.tag == "b":
        if not empty:
            res.append("**{}**".format(contents))

    elif tag.tag == "br":
        res.append("<br>")

    # i
    if tag.tag == "i":
        if not empty:
            res.append("_{}_".format(contents))

    # p
    elif tag.tag == "p":
        if not empty:
            if len(res) > 1 and res[-1].strip() == '':
                print(res)
                res.pop()
            res.append('"'+contents.strip()+'"' + "\n\n")

    # script
    elif tag.tag == "script":
        s = tag.text.strip()
        if s.startswith("ShowPictureQ"):
            m = re.search('["\'](.*?)["\']', s)
            url = m.group(1)
            url = "http://85.142.162.119/os11/"+url
            # TODO: get file from url
            res.append(url+" ")
            # res.append(element.text.strip()+"\n\n")

    # span
    elif tag.tag == "span":
        if not empty:
            res.append(contents)

    # any other tag
    else:
        try:
            raise ValueError('unknown tag: {}, {}'.format(tag.tag, tag.text))
        except:
            client.captureException()
        # if tag.text is not None:
        #     res.append(tag.text)

    return "".join(res)


@shared_task
def get_inf():
    # subject root url
    url = "http://85.142.162.119/os11/xmodules/qprint/openlogin.php?proj=B9ACA5BBB2E19E434CD6BEC25284C67F"
    try:
        chain(
            get_subject_sections.s(url),
            process_sections.s(),
            # process_tasks.s(),
        )()
    except:
        client.captureException()