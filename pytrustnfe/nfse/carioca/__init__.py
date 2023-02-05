# © 2018 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import time
import suds
from OpenSSL import crypto
from pytrustnfe.client import get_authenticated_client
from pytrustnfe.certificado import extract_cert_and_key_from_pfx, save_cert_key
from pytrustnfe.xml import render_xml, sanitize_response
from base64 import b64encode

# from pytrustnfe.nfe.assinatura import Assinatura
from lxml import etree
from .assinatura import Assinatura

import logging
logger = logging.getLogger(__name__)

# Teste
# https://stackoverflow.com/questions/4426204/how-can-i-output-what-suds-is-generating-receiving
logging.basicConfig(level=logging.DEBUG)



def _render(certificado, method, **kwargs):
    path = os.path.join(os.path.dirname(__file__), "templates")
    logger.warning('render')
    logger.warning(kwargs)
    # xml_send = render_xml(path, "%s.xml" % method, True, **kwargs)
    xml_send = render_xml(path, f"{method}.xml", False, **kwargs)
    logger.warning('render fim')
    logger.warning('_render xml_send')
    logger.warning(xml_send)
    logger.warning('_render xml_send fim')

    reference = ""
    if method == "GerarNfse":
        reference = "r%s" % kwargs["rps"]["numero"]
    elif method == "CancelarNfse":
        reference = "Cancelamento_NF%s" % kwargs["cancelamento"]["numero_nfse"]

    logger.warning('xml_send assinador')
    logger.warning(certificado.__dict__)
    logger.warning(f'{certificado.pfx},pass:  {certificado.password}')
    signer = Assinatura(certificado.pfx, certificado.password)
    # xml_send = signer.assina_xml(xml_send, reference)
    # xml_send = signer.assina_xml(xml_send)
    xml_send = etree.fromstring(xml_send)
    xml_send = signer.assina_xml(xml_send)
    logger.warning(xml_send)
    logger.warning('xml_send assinado fim\n')
    logger.warning('kwargs["rps"]')
    logger.warning(kwargs["rps"])
    # return xml_send.encode("utf-8")
    return xml_send

def sign_tag(certificado, **kwargs):
    pkcs12 = crypto.load_pkcs12(certificado.pfx, certificado.password)
    key = pkcs12.get_privatekey()
    if "rps" in kwargs:
        logger.warning('assinando item')
        time.sleep(2)
        logger.warning(kwargs)
        # logger.warning(item.__dict__)
        logger.warning(kwargs["rps"]["assinatura"])
        signed = crypto.sign(key, kwargs["rps"]["assinatura"], "SHA1")
        logger.warning(signed)
        kwargs["rps"]["assinatura"] = b64encode(signed).decode()
        logger.warning(kwargs["rps"]["assinatura"])
        # for item in kwargs["rps"]:
        #     logger.warning('assinando item')
        #     time.sleep(5)
        #     logger.warning(item)
        #     # logger.warning(item.__dict__)
        #     signed = crypto.sign(key, item["assinatura"], "SHA1")
        #     item["assinatura"] = b64encode(signed).decode()
            # logger.warning(item["assinatura"])
    # if "cancelamento" in kwargs:
    #     signed = crypto.sign(key, kwargs["cancelamento"]["assinatura"], "SHA1")
    #     kwargs["cancelamento"]["assinatura"] = b64encode(signed).decode()


def _send(certificado, method, **kwargs):
    base_url = ""
    if kwargs["ambiente"] == "producao":
        base_url = "https://notacarioca.rio.gov.br/WSNacional/nfse.asmx?wsdl"
    else:
        base_url = "https://notacariocahom.rio.gov.br/WSNacional/nfse.asmx?wsdl" # noqa

    # if ( method == "GerarNfse" ):
        # sign_tag(certificado, **kwargs)

    # xml_send = kwargs["xml"].decode("utf-8")
    xml_send = kwargs["xml"]
    logger.warning('_send xml_send')
    logger.warning(xml_send)
    cert, key = extract_cert_and_key_from_pfx(certificado.pfx, certificado.password)
    cert, key = save_cert_key(cert, key)
    logger.warning(f'cert:{cert} key:{key}')
    client = get_authenticated_client(base_url, cert, key)
    logger.warning('client')
    logger.warning(client)
    logger.warning('client.service')
    # logger.warning(client.service, method)

    try:
        response = getattr(client.service, method)(xml_send)
        # response = getattr(client.service, method)(1, xml_send)
    except suds.WebFault as e:
        return {
            "sent_xml": str(xml_send),
            "received_xml": str(e.fault.faultstring),
            "object": None,
        }

    logger.warning('response')
    logger.warning(response)
    logger.warn('client.last_sent()')
    print(client.last_sent())
    response, obj = sanitize_response(response)
    return {"sent_xml": str(xml_send), "received_xml": str(response), "object": obj}


def xml_gerar_nfse(certificado, **kwargs):
    logger.warning('xml_gerar_nfse')
    return _render(certificado, "GerarNfse", **kwargs)


def gerar_nfse(certificado, **kwargs):
    logger.warning('gerar_nfse')
    logger.warning(kwargs)
    if "xml" not in kwargs:
        kwargs["xml"] = xml_gerar_nfse(certificado, **kwargs)
        logger.warning(kwargs)
    return _send(certificado, "GerarNfse", **kwargs)


def xml_cancelar_nfse(certificado, **kwargs):
    return _render(certificado, "CancelarNfse", **kwargs)


def cancelar_nfse(certificado, **kwargs):
    if "xml" not in kwargs:
        kwargs["xml"] = xml_cancelar_nfse(certificado, **kwargs)
    return _send(certificado, "CancelarNfse", **kwargs)
