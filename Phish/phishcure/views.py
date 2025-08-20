from django.shortcuts import render
import socket
import requests
import datetime
from urllib.parse import urlparse
import numpy as np
import joblib
from bs4 import BeautifulSoup
from .feature_extraction import FeatureExtraction
from Phish.settings import MODEL_DIR


def home(request):
    """
    Renders the home page template.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response containing the home page template.
    """
    return render(request, "Home.html")


def get_domain_info(domain):
    """
    Extracts domain information from whois.com.

    Parameters:
        domain (str): The domain name.

    Returns:
        tuple: A tuple containing the creation date, expiration date,
        and registrar of the domain.
    """
    url = f"https://www.whois.com/whois/{domain}"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')

        # Find registrar info
        registrar_tag = soup.find("div", {"class": "df-value"})
        registrar = registrar_tag.text.strip() if registrar_tag else None

        # Find creation date
        creation_date = find_info(content, "Creation Date:")
        if creation_date:
            creation_date = creation_date.split("T")[0]

        # Find expiration date
        expiration_date = find_info(content, "Registry Expiry Date:")
        if expiration_date:
            expiration_date = expiration_date.split("T")[0]

        return creation_date, expiration_date, registrar
    return None, None, None


def find_info(content, keyword):
    """
    Finds specific information within the HTML content.

    Parameters:
        content (str): The HTML content.
        keyword (str): The keyword to search for.

    Returns:
        str or None: The found information or None if not found.
    """
    start = content.find(keyword)
    if start != -1:
        start += len(keyword)
        end = content.find("\n", start)
        return content[start:end].strip()
    return None


def result(request):
    """
    Processes the form submission and renders the result page.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response containing the result page template.
    """
    if request.method == "POST":
        url = request.POST["url"]
        data = FeatureExtraction.getAttributes(url)
        data = np.array(list(data.values())).reshape(1, -1)

        model = joblib.load(open(MODEL_DIR, "rb"))
        probabilities = model.predict(data)[0]
        predicted_value = np.argmax(probabilities)

        domain = urlparse(url).netloc
        ip_address = socket.gethostbyname(domain)

        creation_date, expiration_date, registrar = get_domain_info(domain)

        # Handling None creation_date
        if creation_date:
            creation_date = datetime.datetime.strptime(
                creation_date, "%Y-%m-%d").date()
            today = datetime.date.today()
            domain_age_days = (today - creation_date).days
            domain_age_formatted = domain_age_days / 365
            domain_age = "{:.0f}".format(domain_age_formatted)
        else:
            domain_age = None

        # Handling None expiration_date
        if expiration_date:
            expiration_date = datetime.datetime.strptime(
                expiration_date, "%Y-%m-%d").date()
        else:
            expiration_date = None

        context = {
            "url": url,
            "domain": domain,
            "ip_address": ip_address,
            "registrar": registrar,
            "creation_date": creation_date,
            "expiration_date": expiration_date,
            "domain_age": domain_age,
            "predicted_value": predicted_value,
        }

        if predicted_value == 0:
            return render(request, "secure.html", context)
        else:
            return render(request, "unsecure.html", context)
    else:
        return render(request, "Home.html")


def about(request):
    """
    Renders the about page template.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered response containing the about page template.
    """
    return render(request, "About.html")
