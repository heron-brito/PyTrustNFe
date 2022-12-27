# coding=utf-8

import mock
import os.path
import unittest
from pytrustnfe.certificado import Certificado
from pytrustnfe.nfse.carioca import gerar_nfse
from pytrustnfe.nfse.carioca import cancelar_nfse


class test_nfse_carioca(unittest.TestCase):

    caminho = os.path.dirname(__file__)

    def _get_nfse(self):
        rps = {
          'ambiente': 'homologacao',
          'rps': {            
                   'assinatura': 'admin$321',
                   'numero': '200',
                   'serie': '1',
                   'tipo_rps': '1',
                   'data_emissao': '2020-01-01T21:00:00',
                   'natureza_operacao': '1',
                   'optante_simples': '1',
                   'incentivador_cultural': '2',
                   'status': '1',
                   'valor_servico': '5.00',
                   'valor_deducao': '0',
                   'valor_pis': '0',
                   'valor_cofins': '0',
                   'valor_inss': '0',
                   'valor_ir': '0',
                   'valor_csll': '0',
                   'iss_retido': '2',
                   'valor_iss': '0',
                   'valor_iss_retido': '0',
                   'outras_retencoes': '0',
                   'base_calculo': '5.00',
                   'aliquota_issqn': '0.05',
                   'valor_liquido_nfse': '5.00',
                   'desconto_incondicionado': '',
                   'desconto_condicionado': '',
                   'codigo_servico': '0107',
                   'cnae_servico': '',
                   'codigo_tributacao_municipio': '010701',
                   'codigo_municipio': '3304557',
                   'descricao': 'Somente um teste',
                   'prestador': {
                       'cnpj': '23834691000124',
                       'inscricao_municipal': '10021294',
                   },                   
                   "tomador": {
                       "tipo_cpfcnpj": "1",
                       "cpf_cnpj": "07769776000110",
                       "inscricao_municipal": "3867153",
                    #    "cpf_cnpj": "12345678923256",
                    #    "inscricao_municipal": "123456",
                       "razao_social": "Trustcode",
                       "tipo_logradouro": "1",
                       "logradouro": "Vinicius de Moraes, 42",
                       "numero": "42",
                       "bairro": "Corrego",
                       "cidade": "3304557",
                       "uf": "RJ",
                       "cep": "22640102",
                   },
               },
       }
        return rps

    def test_envio_nfse(self):
        # pfx_source = open(os.path.join(self.caminho, "teste.pfx"), "rb").read()
        # pfx = Certificado(pfx_source, "123456")
        pfx_source = open(os.path.join(self.caminho, "23834691000124.pfx"), "rb").read()
        pfx = Certificado(pfx_source, "admin$321")

        nfse = self._get_nfse()
        path = os.path.join(os.path.dirname(__file__), "XMLs")
        xml_return = open(os.path.join(path, "carioca_resultado.xml"), "r").read()


        retorno = gerar_nfse(pfx, **nfse)
        print('retorno')
        print(retorno)

        self.assertEqual(retorno["received_xml"], xml_return)
        self.assertEqual(retorno["object"].Cabecalho.Sucesso, True)
        self.assertEqual(retorno["object"].ChaveNFeRPS.ChaveNFe.NumeroNFe, 446)
        self.assertEqual(retorno["object"].ChaveNFeRPS.ChaveRPS.NumeroRPS, 6)        

        with mock.patch(
            "pytrustnfe.nfse.carioca.get_authenticated_client"
        ) as client:
            retorno = mock.MagicMock()
            client.return_value = retorno
            retorno.service.EnvioLoteRPS.return_value = xml_return

            retorno = gerar_nfse(pfx, **nfse)
            # retorno = gerar_nfse(pfx, nfse=nfse)

            self.assertEqual(retorno["received_xml"], xml_return)
            self.assertEqual(retorno["object"].Cabecalho.Sucesso, True)
            self.assertEqual(retorno["object"].ChaveNFeRPS.ChaveNFe.NumeroNFe, 446)
            self.assertEqual(retorno["object"].ChaveNFeRPS.ChaveRPS.NumeroRPS, 6)

    # def test_nfse_signature(self):
    #     pfx_source = open(os.path.join(self.caminho, "teste.pfx"), "rb").read()
    #     pfx = Certificado(pfx_source, "123456")

    #     nfse = self._get_nfse()
    #     path = os.path.join(os.path.dirname(__file__), "XMLs")
    #     xml_sent = open(os.path.join(path, "carioca_signature.xml"), "r").read()

    #     with mock.patch(
    #         "pytrustnfe.nfse.carioca.get_authenticated_client"
    #     ) as client:
    #         retorno = mock.MagicMock()
    #         client.return_value = retorno
    #         retorno.service.EnvioLoteRPS.return_value = "<xml></xml>"

    #         retorno = gerar_nfse(pfx, nfse=nfse)
    #         # retorno = envio_lote_rps(pfx, nfse=nfse)
    #         # f = open(os.path.join(path, "carioca_signature.xml"), "w")
    #         # f.write(retorno["sent_xml"])
    #         # f.close()
    #         self.assertEqual(retorno["sent_xml"], xml_sent)

    # def _get_cancelamento(self):
    #     return {
    #         "cnpj_remetente": "123",
    #         "assinatura": "assinatura",
    #         "numero_nfse": "456",
    #         "inscricao_municipal": "654",
    #         "codigo_verificacao": "789",
    #     }

    # def test_cancelamento_nfse_ok(self):
    #     pfx_source = open(os.path.join(self.caminho, "teste.pfx"), "rb").read()
    #     pfx = Certificado(pfx_source, "123456")
    #     cancelamento = self._get_cancelamento()

    #     path = os.path.join(os.path.dirname(__file__), "XMLs")
    #     xml_return = open(os.path.join(path, "carioca_canc_ok.xml"), "r").read()

    #     with mock.patch(
    #         "pytrustnfe.nfse.carioca.get_authenticated_client"
    #     ) as client:
    #         retorno = mock.MagicMock()
    #         client.return_value = retorno
    #         retorno.service.CancelamentoNFe.return_value = xml_return

    #         retorno = cancelamento_nfe(pfx, cancelamento=cancelamento)

    #         self.assertEqual(retorno["received_xml"], xml_return)
    #         self.assertEqual(retorno["object"].Cabecalho.Sucesso, True)

    # def test_cancelamento_nfse_com_erro(self):
    #     pfx_source = open(os.path.join(self.caminho, "teste.pfx"), "rb").read()
    #     pfx = Certificado(pfx_source, "123456")
    #     cancelamento = self._get_cancelamento()

    #     path = os.path.join(os.path.dirname(__file__), "XMLs")
    #     xml_return = open(os.path.join(path, "carioca_canc_errado.xml"), "r").read()

    #     with mock.patch(
    #         "pytrustnfe.nfse.carioca.get_authenticated_client"
    #     ) as client:
    #         retorno = mock.MagicMock()
    #         client.return_value = retorno
    #         retorno.service.CancelamentoNFe.return_value = xml_return

    #         retorno = cancelamento_nfe(pfx, cancelamento=cancelamento)

    #         self.assertEqual(retorno["received_xml"], xml_return)
    #         self.assertEqual(retorno["object"].Cabecalho.Sucesso, False)
    #         self.assertEqual(retorno["object"].Erro.ChaveNFe.NumeroNFe, 446)
