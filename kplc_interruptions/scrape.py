import logging
import os

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

LOGGER = logging.getLogger(__name__)

KPLC_INTERRUPTIONS_URL = "https://kplc.co.ke/category/view/50/planned-power-interruptions";
KPLC_INTERRUPTIONS_DOWNLOAD_DIR = "/tmp/"

CHUNK_SIZE = 1024


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

    Returns the download path of the PDF file.
    """
    # content-disposition header isn't set so we do this instead
    pdf_filename = url.rsplit('/', 1)[1]
    response = requests.get(url)
    if not response.ok:
        # TODO: use custom exception
        raise Exception("Bad request")

    # assert content-type of the file to download is PDF
    if response.headers["Content-Type"] != "application/pdf":
        # TODO: use custom exception
        raise Exception("Not a pdf")

    download_path = os.path.join(KPLC_INTERRUPTIONS_DOWNLOAD_DIR, pdf_filename)
    with open(download_path, "wb") as fd:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            fd.write(chunk)

    return download_path


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

    get next link
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
        "download_file_path": "/tmp/c8JP5YCE4HQ4_Interruptions - 20.06.2019.pdf",
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
    a_tags = soup.find(
        "div", class_="attachments").find_all("a", class_="docicon")
    a_tags.extend(soup.find(
        "div", class_="genericintro").find_all("a", class_="download"))

    for a_tag in a_tags:
        download_link_text = a_tag.get_text()
        download_link = a_tag.get("href")
        download_file_path = download_pdf(download_link)
        yield {
            "parent_link": url,
            "download_file_path": download_file_path,
            "download_link_text": download_link_text,
            "download_link": download_link
        }


def stage_interruptions():
    """
    Stage the scraped details in the database.
    """
    for interruption in scrape_interruption_titles():
        # TODO: save this in the models

        for download in scrape_interruption_pdf_files(interruption["link"]):
            # TODO: save this in the models
