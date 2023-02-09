from lxml import etree
from pytrustnfe.certificado import extract_cert_and_key_from_pfx
from signxml import XMLSigner, methods
from pytrustnfe.nfe.assinatura import Assinatura as _Assinatura

import logging
logger = logging.getLogger(__name__)

# Teste
# https://stackoverflow.com/questions/4426204/how-can-i-output-what-suds-is-generating-receiving
logging.basicConfig(level=logging.DEBUG)

class Assinatura(_Assinatura):

    def assina_xml(self, xml_element):
        logger.warning('assina_xml')
        print('assina_xml')
        
        
        cert, key = extract_cert_and_key_from_pfx(self.arquivo, self.senha)

        for element in xml_element.iter("*"):
            if element.text is not None and not element.text.strip():
                element.text = None

        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm=u"rsa-sha1",
            digest_algorithm=u"sha1",
            c14n_algorithm=u"http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
        )

        logger.warning('assina_xml signer end')

        ns = {}
        ns[None] = signer.namespaces["ds"]
        signer.namespaces = ns
        element_signed = xml_element.find(".//{http://notacarioca.rio.gov.br/WSNacional/XSD/1/nfse_pcrj_v01.xsd}Rps")
        # element_signed = xml_element.find("{http://notacarioca.rio.gov.br/WSNacional/XSD/1/nfse_pcrj_v01.xsd}")
        logger.warning('element_signed')
        logger.warning(element_signed.text)
        signed_root = signer.sign(
            xml_element, key=key.encode(), cert=cert.encode()
        )
        signature = signed_root.find(
            ".//{http://www.w3.org/2000/09/xmldsig#}Signature"
        )

        if element_signed is not None and signature is not None:
            parent = xml_element.getchildren()[0]
            logger.warning('parent')
            logger.warning(parent.text)
            parent.append(signature)
        logger.warning(f'xml_element: {xml_element}')
        return etree.tostring(xml_element, encoding=str)
