from urllib.parse import urlparse
import re
import requests
import datetime
import socket
from bs4 import BeautifulSoup


class FeatureExtraction:
    def __init__(self):
        pass

    def domainPresence(self, url):
        """
        Checks if a domain is present in the given URL.

        Parameters:
            url (str): The URL to be checked.

        Returns:
            Returns 1 if the URL contains a domain, otherwise returns 0.
        """
        return 1 if urlparse(url).netloc else 0

    def havingIP(self, url):
        """
        Checks if the given URL has an IP address in its netloc component.

        Parameters:
            url (str) : The url to be checked.

        Returns:
            int : Returns 1 if the URL's netloc component contains
            an IP address, otherwise returns 0.
        """
        try:
            ip = socket.gethostbyname(urlparse(url).netloc)
            return 1
        except socket.geterror:
            return 0

    def haveAtSign(self, url):
        """
        Checks if the given URL contains an '@' character, indicating a
        potential username and password in the URL.

        Parametrs:
            url(str) : The URL to be checked.

        Returns:
            int : Returns 1 if the '@' character is present in the URL,
            indicating potential username and password, otherwise returns 0. 
        """
        return 1 if "@" in url else 0

    def getLength(self, url):
        """
        Checks if the length of the given URL is greater than or equal to
        54 characters.

        Parameters:url (str): The URL to be checked.

        Returns:
            int : Returns 1 if the length of the URL is greater than or equal
            to 54 characters, otherwise returns 0.
        """
        return 1 if len(url) >= 54 else 0

    def getDepth(self, url):
        """
        Calculates the depth of the given URL by counting the number of
        '/' characters in it.

        Parameters : url (str): The URL to be analyzed.

        Returns:
            int : The depth of the URL, which is the number of '/' characters
            found in it.
        """
        return url.count("/")

    def redirection(self, url):
        """
        Checks if the given URL redirects to another URL.

        Parameters : url (str) : The URL to be checked for redirection.

        Returns :
            int: Returns 1 if the URL redirects to another URL, otherwise
            returns 0.
        """
        try:
            response = requests.get(url, allow_redirects=True)
            redirected_url = response.url
            return 1 if redirected_url != url else 0
        except requests.RequestException:
            return 0

    def httpDomain(self, url):
        """
        Checks if the domain of the given URL uses the HTTPS protocol.

        Parameters:
            url(str) : The URL to be checked.

        Returns:
            int : Returns 1 if the domain of the URL uses the HTTPS
            protocol, otherwise returns 0.
        """
        return 1 if urlparse(url).scheme == "https" else 0

    def tinyURL(self, url):
        """
        Checks if the given URL is a shortened URL created by common URL
        shortening services.

        Parameters:
            url (str) : The URl to be checked.

        Returns :
            int : Returns 1 if the URL matches the patterns of common URL
            shortening services, otherwise returns 0.
        """
        shortening_services = (
            r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|"
            r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|"
            r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|"
            r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|"
            r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|"
            r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|"
            r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|"
            r"tr\.im|link\.zip\.net"
        )
        match = re.search(shortening_services, url)
        return 1 if match else 0

    def prefixSuffix(self, url):
        """
        Checks if the netloc component of the given URL contains a hypen ('-').

        Parameters:
            url (str): The URL to be checked.

        Returns :
            int : Returns 1 if the netloc component of the URL conatins a hyphen ('-'), otherwise returns 0.
        """
        return 1 if "-" in urlparse(url).netloc else 0

    def domainAge(self, url):
        """
        Determine the age of the domain associated with the given URL.

        Args:
        url(str):The URL from which the domain age is to be determined.

        Returns:
            int:1 if the domain age is less than 180 days (considered young),
                0 if the domain age is 180 days or more (considered not young).
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            creation_dates = soup.find_all("meta", {"name": "creation_date"})
            if creation_dates:
                creation_date = creation_dates[0].get("content")
                creation_datetime = datetime.datetime.strptime(
                    creation_date, "%Y-%m-%dT%H:%M:%SZ")
                current_datetime = datetime.datetime.utcnow()
                domain_age = (current_datetime - creation_datetime).days
                return 1 if domain_age < 180 else 0
            else:
                return 1
        except:
            return 1

    @staticmethod
    def getAttributes(url):
        """
        Extract various features/attributes from a given URL.

        Args:
            url (str): The URL from which features/attributes to be extracted.

        Returns:
            dict: a dictionary containing the extracted features
            - "Domain": Presence of domain in URL (True/False).
            - "Have_IP": Presence of ip_address in URL (True/False).
            - "Have_At": Presence of '@' symbol in URL (True/False).
            - "URL_Length": Length of URL.
            - "URL_Depth": Depth of URL in terms of directory structure.
            - "Redirection": Presence of redirection in URL (True/False).
            - "https_domain": Use of HTTPS protocol in domain (True/False).
            - "TinyURL": Presence of TinyURL-like characteristics in URL
                (True/False).
            - "Has_hyphen": Presence of hyphen in domain-name (True/False).
            - "Domain_Age": Age of domain.
        """
        fe = FeatureExtraction()
        domain = fe.domainPresence(url)
        ip_address = fe.havingIP(url)
        at_sign = fe.haveAtSign(url)
        len_url = fe.getLength(url)
        depth_url = fe.getDepth(url)
        redirect_url = fe.redirection(url)
        https_protocol = fe.httpDomain(url)
        short_url = fe.tinyURL(url)
        have_hyphen = fe.prefixSuffix(url)
        domain_age = fe.domainAge(url)

        return {
            "Domain": domain,
            "Have_IP": ip_address,
            "Have_At": at_sign,
            "URL_Length": len_url,
            "URL_Depth": depth_url,
            "Redirection": redirect_url,
            "https_Domain": https_protocol,
            "TinyURL": short_url,
            "has_Hyphen": have_hyphen,
            "Domain_Age": domain_age,
        }
