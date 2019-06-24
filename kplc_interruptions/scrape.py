import logging
import os
import tempfile

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.core.files import File
from requests_cache import CachedSession

from kplc_interruptions.interruptions.models import (
    Interruption, InterruptionPdf)

LOGGER = logging.getLogger(__name__)

KPLC_INTERRUPTIONS_URL = "https://kplc.co.ke/category/view/50/planned-power-interruptions";


def make_request(url):
    # TODO: consider adding project's details in the headers.
    response = requests.get(url)
    if not response.ok:
        # TODO: use custom exception
        raise Exception("Bad request")

    return response.content.decode("utf-8")


def download_pdf(url):
    """
    Download the PDF file containing the power interruption details.

    Params:
        url (str): URL to download the PDF from.

    Returns the PDF filename and a PDF file object.
    """
    # content-disposition header isn't set so we do this instead
    pdf_filename = url.rsplit('/', 1)[1]
    response = requests.get(url, stream=True)
    if not response.ok:
        # TODO: use custom exception
        raise Exception("Bad request")

    # assert content-type of the file to download is PDF
    if response.headers["Content-Type"] != "application/pdf":
        # TODO: use custom exception
        raise Exception("Not a pdf")

    # delete the temporary file once file is closed
    pdf_file_temp = tempfile.NamedTemporaryFile(delete=True)
    for chunk in response.iter_content(chunk_size=4096):
        pdf_file_temp.write(chunk)
    pdf_file_temp.seek(0)

    return pdf_filename, pdf_file_temp


def scrape_interruption_titles(url=None):
    """
    Scrape power interruption titles and PDF links from KPLC website.

    Params:
        url (str): URL to crawl and get titles and links from.

    Returns a dict containing the interruption title and interruption link to
    the page with the PDF to download.

    Example:
    {
        "title": "Interruptions - 20.06.2019",
        "link": "https://kplc.co.ke/content/item/3071/interruptions---20.06.2019"
    }
    """
    url = url or KPLC_INTERRUPTIONS_URL
    try:
        content = make_request(url)
    except Exception:
        LOGGER.error(
            "Error making request", exc_info=True, extra={"url": url})
        return None

    # parse content
    soup = BeautifulSoup(content, "html.parser")
    for h2_tag in soup.find("main").find_all("h2", class_='generictitle'):
        yield {
            "title": h2_tag.string,
            "link": h2_tag.a.get('href')
        }

    # get next link
    a_tag = soup.find(
        "ul", class_="pagination").find("a", attrs={"rel": "next"})
    if isinstance(a_tag, Tag):
        next_url = a_tag.get("href")
        yield from scrape_interruption_titles(next_url)


def scrape_interruption_pdf_files(url):
    """
    Scrape power interruption link and download PDF containing interruption
    details.

    Params:
        url (str): URL that contains PDF download link(s)

    Returns a dict containing the interruption parent link, the downloaded
    file path, the download link text and the PDF download link.

    Example:
    {
        "parent_link":"https://kplc.co.ke/content/item/3071/interruptions---20.06.2019",
        "pdf_filename": "c8JP5YCE4HQ4_Interruptions - 20.06.2019.pdf",
        "pdf_file_temp": tempfile.NamedTemporaryFile(),
        "download_link_text": "Interruptions - 20.06.2019.pdf",
        "download_link": "https://kplc.co.ke/img/full/c8JP5YCE4HQ4_Interruptions%20-%2020.06.2019.pdf"
    }
    """
    try:
        content = make_request(url)
    except Exception:
        LOGGER.error(
            "Error making request", exc_info=True, extra={"url": url})
        return None

    # parse content
    soup = BeautifulSoup(content, "html.parser")
    a_tags = []
    # most of the download links are found inside anchor tags with docicon
    # class.
    attachment_div = soup.find("div", class_="attachments")
    if attachment_div:
        a_tags.extend(attachment_div.find_all("a", class_="docicon"))
    # some of the download links especially the one marked as archives is
    # inside anchor tags with download class.
    genericintro_div = soup.find("div", class_="genericintro")
    if genericintro_div:
        a_tags.extend(genericintro_div.find_all("a", class_="download"))

    for a_tag in a_tags:
        download_link_text = a_tag.get_text()
        download_link = a_tag.get("href")

        try:
            pdf_filename, pdf_file_temp = download_pdf(download_link)
        except Exception:
            LOGGER.error(
                "Error making request", exc_info=True,
                extra={"download_link": download_link})
            return None

        yield {
            "parent_link": url,
            "pdf_filename": pdf_filename,
            "pdf_file_temp": pdf_file_temp,
            "download_link_text": download_link_text,
            "download_link": download_link
        }


def stage_interruptions():
    """
    Stage the scraped details in the database.
    """
    for interruption_dict in scrape_interruption_titles():
        title = interruption_dict["title"]
        link = interruption_dict["link"]
        interruption, _ = Interruption.objects.get_or_create(
            title=title, link=link)
        print("Saved interruption {}".format(interruption))

    print("\n\nFinished saving interruptions\n\n")

    for interruption in Interruption.objects.all():
        for pdf_dict in scrape_interruption_pdf_files(interruption.link):
            pdf_file_temp = pdf_dict["pdf_file_temp"]
            pdf_filename = pdf_dict["pdf_filename"]
            pdf_link_name = pdf_dict["download_link_text"]
            pdf_link = pdf_dict["download_link"]

            try:
                pdf = InterruptionPdf.objects.get(
                    interruption=interruption, pdf_link=pdf_link)
            except InterruptionPdf.DoesNotExist:
                pdf = InterruptionPdf(
                    interruption=interruption, pdf_link=pdf_link,
                    pdf_link_name=pdf_link_name)
                pdf.pdf_file.save(
                    pdf_filename, File(pdf_file_temp), save=False)
                pdf.save()

            print("\tSaved PDF {}".format(pdf))
